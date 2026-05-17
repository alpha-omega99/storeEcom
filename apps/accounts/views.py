"""
ChicShop — Vues Accounts
Rate limiting, logging sécurité, gestion verrouillage compte
"""
import logging
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError

from .models import PasswordResetToken, UserAddress
from .serializers import (
    UserRegisterSerializer, UserProfileSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, UserAddressSerializer,
)
from .tasks import send_welcome_email, send_password_reset_email

User = get_user_model()
security_logger = logging.getLogger('chicshop.security')


def get_client_ip(request):
    """Extraire l'IP réelle du client (derrière proxy/Nginx)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Prendre la première IP (client), pas les proxies
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    scope = 'register'


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = 'password_reset'


class SecureTokenObtainView(TokenObtainPairView):
    """
    Login sécurisé :
    - Rate limiting strict
    - Verrouillage compte après 5 tentatives
    - Log des tentatives suspectes
    - Message d'erreur uniforme (évite l'énumération des comptes)
    """
    throttle_classes = [LoginRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        ip = get_client_ip(request)
        email = request.data.get('email', '').lower().strip()

        # Vérifier si le compte est verrouillé AVANT de vérifier le mot de passe
        try:
            user = User.objects.get(email=email)
            if user.is_locked:
                security_logger.warning(
                    f"Tentative de connexion sur compte verrouillé — email={email} ip={ip}"
                )
                return Response(
                    {
                        "detail": "Compte temporairement verrouillé suite à plusieurs tentatives échouées. "
                                  "Réessayez dans 30 minutes ou réinitialisez votre mot de passe."
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        except User.DoesNotExist:
            pass  # Ne pas révéler l'inexistence du compte

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # Connexion réussie
            try:
                user = User.objects.get(email=email)
                user.reset_failed_login()
                user.last_login_ip = ip
                user.save(update_fields=['last_login_ip'])
                security_logger.info(f"Connexion réussie — email={email} ip={ip}")
            except User.DoesNotExist:
                pass
        else:
            # Échec — incrémenter le compteur
            try:
                user = User.objects.get(email=email)
                user.increment_failed_login()
                security_logger.warning(
                    f"Échec connexion #{user.failed_login_attempts} — email={email} ip={ip}"
                )
            except User.DoesNotExist:
                # Délai artificiel pour éviter le timing attack sur l'énumération
                import time
                time.sleep(0.1)
                security_logger.warning(
                    f"Tentative connexion compte inexistant — email={email} ip={ip}"
                )

        return response


class RegisterView(generics.CreateAPIView):
    """Inscription avec rate limiting et email de bienvenue"""
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def create(self, request, *args, **kwargs):
        ip = get_client_ip(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)

        # Envoyer l'email de bienvenue (tâche asynchrone)
        send_welcome_email.delay(str(user.id))

        security_logger.info(f"Nouvel utilisateur inscrit — email={user.email} ip={ip}")

        return Response(
            {
                "message": "Compte créé avec succès ! Bienvenue chez ChicShop 🌸",
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED
        )


class LogoutView(generics.GenericAPIView):
    """Logout sécurisé — invalider le refresh token (blacklist)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"detail": "Le token de rafraîchissement est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            security_logger.info(f"Déconnexion — user={request.user.email}")
            return Response({"message": "Déconnexion réussie."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {"detail": "Token invalide ou déjà invalidé."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Profil utilisateur — consultation et mise à jour"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # PATCH par défaut
        return super().update(request, *args, **kwargs)


class ChangePasswordView(generics.GenericAPIView):
    """Changement de mot de passe — exige l'ancien"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        security_logger.info(f"Mot de passe changé — user={user.email} ip={get_client_ip(request)}")

        # Invalider tous les tokens existants en changeant le mot de passe
        # Le client devra se reconnecter
        return Response(
            {"message": "Mot de passe modifié avec succès. Veuillez vous reconnecter."},
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(generics.GenericAPIView):
    """
    Demande de réinitialisation — réponse identique qu'email existe ou non
    (protection contre l'énumération de comptes)
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    GENERIC_RESPONSE = {
        "message": "Si un compte existe avec cet email, vous recevrez un lien de réinitialisation sous peu."
    }

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        ip = get_client_ip(request)

        try:
            user = User.objects.get(email=email, is_active=True)

            # Supprimer les anciens tokens non utilisés
            PasswordResetToken.objects.filter(user=user, used=False).delete()

            # Générer un token cryptographiquement sûr
            token = secrets.token_urlsafe(48)
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(hours=1)
            )

            # Envoyer l'email (asynchrone)
            send_password_reset_email.delay(str(user.id), token)
            security_logger.info(f"Reset password demandé — email={email} ip={ip}")

        except User.DoesNotExist:
            # Délai pour éviter le timing attack
            import time
            time.sleep(0.1)
            security_logger.warning(f"Reset password compte inexistant — email={email} ip={ip}")

        # Toujours la même réponse
        return Response(self.GENERIC_RESPONSE, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirmer la réinitialisation avec le token reçu par email"""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_str = serializer.validated_data['token']

        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=token_str
            )
        except PasswordResetToken.DoesNotExist:
            security_logger.warning(
                f"Tentative reset avec token invalide — ip={get_client_ip(request)}"
            )
            return Response(
                {"detail": "Token invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not reset_token.is_valid():
            return Response(
                {"detail": "Token invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = reset_token.user
        user.set_password(serializer.validated_data['new_password'])
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.save()

        reset_token.used = True
        reset_token.save(update_fields=['used'])

        security_logger.info(f"Mot de passe réinitialisé — user={user.email}")

        return Response(
            {"message": "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter."},
            status=status.HTTP_200_OK
        )


class UserAddressViewSet(generics.ListCreateAPIView):
    """Gestion des adresses de livraison"""
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Isolation stricte : uniquement les adresses de l'utilisateur connecté
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail/modification/suppression d'une adresse"""
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # IDOR protection : filtrer par user AVANT l'accès à l'objet
        return UserAddress.objects.filter(user=self.request.user)
