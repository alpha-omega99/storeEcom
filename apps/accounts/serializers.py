"""
ChicShop — Serializers Accounts
Validation stricte, sanitisation, protection XSS
"""
import re
import bleach
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserAddress

User = get_user_model()


def sanitize_text(value, max_length=None):
    """Nettoyer tout HTML potentiel — protection XSS"""
    if not value:
        return value
    cleaned = bleach.clean(str(value), tags=[], strip=True).strip()
    if max_length:
        cleaned = cleaned[:max_length]
    return cleaned


class UserRegisterSerializer(serializers.ModelSerializer):
    """Inscription — validation stricte"""
    password = serializers.CharField(
        write_only=True, required=True, min_length=10,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )
    terms_accepted = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'password', 'password_confirm', 'terms_accepted',
            'marketing_consent',
        ]

    def validate_email(self, value):
        email = value.lower().strip()
        # Vérifier les domaines jetables connus (liste partielle)
        disposable_domains = ['tempmail.com', 'guerrillamail.com', 'mailinator.com']
        domain = email.split('@')[-1]
        if domain in disposable_domains:
            raise serializers.ValidationError(
                "Les adresses email temporaires ne sont pas acceptées."
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Un compte existe déjà avec cet email.")
        return email

    def validate_first_name(self, value):
        cleaned = sanitize_text(value, max_length=50)
        if not cleaned or len(cleaned) < 2:
            raise serializers.ValidationError("Le prénom doit contenir au moins 2 caractères.")
        if not re.match(r"^[\w\sÀ-ÿ\-']+$", cleaned):
            raise serializers.ValidationError("Le prénom contient des caractères invalides.")
        return cleaned

    def validate_last_name(self, value):
        cleaned = sanitize_text(value, max_length=50)
        if not cleaned or len(cleaned) < 2:
            raise serializers.ValidationError("Le nom doit contenir au moins 2 caractères.")
        if not re.match(r"^[\w\sÀ-ÿ\-']+$", cleaned):
            raise serializers.ValidationError("Le nom contient des caractères invalides.")
        return cleaned

    def validate_phone(self, value):
        if not value:
            return value
        # Nettoyage et validation format CI/international
        cleaned = re.sub(r'[\s\-\.\(\)]', '', value)
        if not re.match(r'^\+?[\d]{8,15}$', cleaned):
            raise serializers.ValidationError(
                "Numéro de téléphone invalide. Format : +225 07 00 00 00 00"
            )
        return cleaned

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                "Vous devez accepter les conditions d'utilisation."
            )
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data.pop('terms_accepted')
        validated_data['terms_accepted_at'] = timezone.now()
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Profil utilisateur — lecture/écriture (sauf champs sensibles)"""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'city', 'address', 'is_email_verified',
            'date_joined', 'marketing_consent',
        ]
        read_only_fields = ['id', 'email', 'is_email_verified', 'date_joined']

    def validate_first_name(self, value):
        return sanitize_text(value, max_length=50)

    def validate_last_name(self, value):
        return sanitize_text(value, max_length=50)

    def validate_address(self, value):
        return sanitize_text(value, max_length=500)

    def validate_city(self, value):
        return sanitize_text(value, max_length=100)

    def validate_phone(self, value):
        if not value:
            return value
        cleaned = re.sub(r'[\s\-\.\(\)]', '', value)
        if not re.match(r'^\+?[\d]{8,15}$', cleaned):
            raise serializers.ValidationError("Numéro invalide.")
        return cleaned


class ChangePasswordSerializer(serializers.Serializer):
    """Changement de mot de passe authentifié"""
    current_password = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True, required=True, min_length=10,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError(
                {'new_password_confirm': "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Demande de réinitialisation — pas d'info sur l'existence du compte"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirmation réinitialisation avec le token"""
    token = serializers.CharField(required=True, max_length=64)
    new_password = serializers.CharField(
        write_only=True, required=True, min_length=10,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError(
                {'new_password_confirm': "Les mots de passe ne correspondent pas."}
            )
        return attrs


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'label', 'address', 'city', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_address(self, value):
        return sanitize_text(value, max_length=500)

    def validate_label(self, value):
        return sanitize_text(value, max_length=50)

    def validate_city(self, value):
        return sanitize_text(value, max_length=100)


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    """JWT personnalisé — ajouter des claims utiles au token"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims custom (non-sensibles uniquement)
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        # Normaliser l'email
        attrs['email'] = attrs.get('email', '').lower().strip()
        return super().validate(attrs)
