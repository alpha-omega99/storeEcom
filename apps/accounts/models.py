"""
ChicShop — Modèle Utilisateur personnalisé
Sécurisé : téléphone CI, email unique, tracking des connexions
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager personnalisé — email comme identifiant principal"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("L'adresse email est obligatoire"))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hachage Argon2
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Le superuser doit avoir is_staff=True"))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Le superuser doit avoir is_superuser=True"))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur ChicShop.
    - UUID comme PK (évite l'énumération d'IDs)
    - Email comme login
    - Téléphone pour WhatsApp
    - Tracking des connexions pour détection d'intrusion
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identifiants
    email = models.EmailField(_('email'), unique=True, db_index=True, max_length=254)
    phone = models.CharField(
        _('téléphone'), max_length=20, blank=True,
        help_text=_('Format : +225 07 00 00 00 00')
    )

    # Profil
    first_name = models.CharField(_('prénom'), max_length=50)
    last_name = models.CharField(_('nom'), max_length=50)

    # Adresse principale
    address = models.TextField(_('adresse'), blank=True)
    city = models.CharField(_('commune'), max_length=100, blank=True)

    # Statuts
    is_active = models.BooleanField(_('actif'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_email_verified = models.BooleanField(_('email vérifié'), default=False)

    # Sécurité — tracking pour détection d'anomalies
    date_joined = models.DateTimeField(_('inscription'), default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    # Consentement RGPD
    marketing_consent = models.BooleanField(_('consentement marketing'), default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def is_locked(self):
        """Compte verrouillé après trop de tentatives ?"""
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        return False

    def increment_failed_login(self):
        """Incrémenter les échecs et verrouiller si nécessaire"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = timezone.now() + timedelta(minutes=30)
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])

    def reset_failed_login(self):
        """Réinitialiser après connexion réussie"""
        if self.failed_login_attempts > 0 or self.account_locked_until:
            self.failed_login_attempts = 0
            self.account_locked_until = None
            self.save(update_fields=['failed_login_attempts', 'account_locked_until'])


class UserAddress(models.Model):
    """Adresses multiples par utilisateur"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Domicile')  # Domicile, Bureau, etc.
    address = models.TextField()
    city = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.label} ({self.city})"

    def save(self, *args, **kwargs):
        # Une seule adresse par défaut par utilisateur
        if self.is_default:
            UserAddress.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """Tokens de réinitialisation de mot de passe sécurisés"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'token de réinitialisation'

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at
