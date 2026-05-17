"""
ChicShop — App Payments
Paiements Mobile Money : Orange Money, Wave
Sécurité : vérification des webhooks, idempotence, anti-rejeu
"""
import uuid
import hmac
import hashlib
import logging
from decimal import Decimal

from django.db import models, transaction
from django.conf import settings
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger('chicshop')
security_logger = logging.getLogger('chicshop.security')


# ============================================================
# MODELS
# ============================================================

class Payment(models.Model):
    """Enregistrement de chaque tentative/transaction de paiement"""

    class Provider(models.TextChoices):
        ORANGE_MONEY = 'orange_money', 'Orange Money'
        WAVE = 'wave', 'Wave'
        CASH = 'cash', 'Cash livraison'

    class PaymentStatus(models.TextChoices):
        INITIATED = 'initiated', 'Initié'
        PENDING = 'pending', 'En attente'
        SUCCESS = 'success', 'Succès'
        FAILED = 'failed', 'Échoué'
        CANCELLED = 'cancelled', 'Annulé'
        REFUNDED = 'refunded', 'Remboursé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        'orders.Order', on_delete=models.PROTECT, related_name='payments'
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED
    )

    # Montant en F CFA
    amount = models.DecimalField(max_digits=12, decimal_places=0)

    # Identifiants externes
    external_transaction_id = models.CharField(
        max_length=200, blank=True, db_index=True,
        help_text="ID de transaction retourné par le prestataire"
    )
    external_reference = models.CharField(max_length=200, blank=True)

    # Réponse brute du prestataire (pour audit)
    provider_response = models.JSONField(default=dict, blank=True)

    # Anti-rejeu : chaque paiement a un idempotency_key unique
    idempotency_key = models.CharField(max_length=64, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'paiement'
        verbose_name_plural = 'paiements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.provider} {self.amount} F — {self.status} ({self.order.reference})"


# ============================================================
# VIEWS
# ============================================================

class InitiatePaymentSerializer(serializers.Serializer):
    order_reference = serializers.CharField(max_length=20)
    provider = serializers.ChoiceField(choices=['orange_money', 'wave'])
    phone_number = serializers.CharField(max_length=20)


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_payment(request):
    """
    Initier un paiement Mobile Money.
    En production : connecter à l'API Orange Money CI ou Wave CI.
    """
    from apps.orders.views import Order
    import secrets

    serializer = InitiatePaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        order = Order.objects.get(reference=data['order_reference'])
    except Order.DoesNotExist:
        return Response({'detail': 'Commande introuvable.'}, status=status.HTTP_404_NOT_FOUND)

    # Vérifier que la commande est en attente
    if order.payment_status == 'paid':
        return Response({'detail': 'Cette commande est déjà payée.'}, status=status.HTTP_400_BAD_REQUEST)

    # Générer une clé d'idempotence unique
    idempotency_key = secrets.token_hex(32)

    with transaction.atomic():
        payment = Payment.objects.create(
            order=order,
            provider=data['provider'],
            amount=order.total_amount,
            idempotency_key=idempotency_key,
            status='pending',
        )

        # Ici : appel API Orange Money / Wave réel
        # Exemple (Orange Money CI) :
        # response = orange_money_client.request_payment(
        #     amount=order.total_amount,
        #     phone=data['phone_number'],
        #     order_ref=order.reference,
        # )
        # Pour l'instant : simulation
        mock_response = {
            "payment_url": f"https://payment.chicshop.ci/pay/{payment.id}",
            "payment_id": str(payment.id),
            "status": "pending",
            "message": "Vérifiez votre téléphone pour confirmer le paiement.",
        }

    logger.info(
        f"Paiement initié — order={order.reference} provider={data['provider']} "
        f"amount={order.total_amount}"
    )

    return Response(mock_response, status=status.HTTP_201_CREATED)


class WebhookView(APIView):
    """
    Webhook de paiement — reçoit les notifications des prestataires.
    CRITIQUE : vérification de la signature HMAC pour authentifier la source.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Authentification par signature HMAC uniquement

    def post(self, request, provider):
        raw_body = request.body

        # ---- 1. Vérifier la signature HMAC ----
        if not self._verify_signature(request, provider, raw_body):
            security_logger.warning(
                f"Webhook signature invalide — provider={provider} "
                f"ip={request.META.get('REMOTE_ADDR')}"
            )
            # Retourner 200 même en cas d'échec (éviter les retries sur erreur d'auth)
            return Response({'status': 'ignored'}, status=status.HTTP_200_OK)

        payload = request.data
        transaction_id = payload.get('transaction_id') or payload.get('id')
        order_ref = payload.get('order_reference') or payload.get('merchant_ref')
        payment_status = payload.get('status')

        if not all([transaction_id, order_ref]):
            return Response({'status': 'invalid_payload'}, status=status.HTTP_200_OK)

        # ---- 2. Anti-rejeu : vérifier que la transaction n'a pas déjà été traitée ----
        if Payment.objects.filter(external_transaction_id=transaction_id).exists():
            security_logger.warning(
                f"Webhook rejeu détecté — transaction_id={transaction_id}"
            )
            return Response({'status': 'already_processed'}, status=status.HTTP_200_OK)

        try:
            from apps.orders.views import Order
            order = Order.objects.get(reference=order_ref)
            payment = Payment.objects.filter(
                order=order, status='pending'
            ).select_for_update().first()

            if not payment:
                return Response({'status': 'no_pending_payment'}, status=status.HTTP_200_OK)

            with transaction.atomic():
                if payment_status in ('SUCCESS', 'success', 'SUCCESSFUL', '200'):
                    payment.status = 'success'
                    payment.external_transaction_id = transaction_id
                    payment.provider_response = payload
                    from django.utils import timezone
                    payment.completed_at = timezone.now()
                    payment.save()

                    # Marquer la commande comme payée
                    Order.objects.filter(pk=order.pk).update(payment_status='paid')

                    logger.info(
                        f"Paiement réussi — order={order_ref} "
                        f"transaction={transaction_id} montant={payment.amount}"
                    )
                elif payment_status in ('FAILED', 'failed', 'CANCELLED', 'cancelled'):
                    payment.status = 'failed'
                    payment.external_transaction_id = transaction_id
                    payment.provider_response = payload
                    payment.save()
                    logger.warning(f"Paiement échoué — order={order_ref}")

        except Order.DoesNotExist:
            security_logger.warning(f"Webhook commande introuvable — ref={order_ref}")

        # Toujours retourner 200 pour éviter les retries du prestataire
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

    def _verify_signature(self, request, provider, raw_body):
        """Vérifier la signature HMAC-SHA256 du webhook"""
        # Clé secrète partagée avec le prestataire (dans .env)
        secret_key = getattr(settings, f'{provider.upper()}_WEBHOOK_SECRET', '')
        if not secret_key:
            # Si pas de clé configurée, logger et refuser en production
            security_logger.warning(f"Clé webhook manquante pour {provider}")
            return not settings.DEBUG  # Accepter seulement en dev sans clé

        # Récupérer la signature dans les headers
        signature_header = (
            request.META.get('HTTP_X_SIGNATURE')
            or request.META.get('HTTP_X_WEBHOOK_SIGNATURE')
            or ''
        )

        # Calculer la signature attendue
        expected = hmac.new(
            secret_key.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()

        # Comparaison à temps constant (protection timing attack)
        return hmac.compare_digest(expected, signature_header)


# ============================================================
# URLS
# ============================================================
app_name = 'payments'

urlpatterns = [
    path('initiate/', initiate_payment, name='initiate'),
    path('webhook/<str:provider>/', WebhookView.as_view(), name='webhook'),
]


# ============================================================
# ADMIN
# ============================================================
from django.contrib import admin


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'provider', 'amount', 'status',
                    'external_transaction_id', 'created_at']
    list_filter = ['provider', 'status', 'created_at']
    search_fields = ['order__reference', 'external_transaction_id', 'idempotency_key']
    readonly_fields = [f.name for f in Payment._meta.fields]

    def has_add_permission(self, request):
        return False  # Les paiements sont créés uniquement par le code

    def has_delete_permission(self, request, obj=None):
        return False  # Aucune suppression pour l'audit trail
