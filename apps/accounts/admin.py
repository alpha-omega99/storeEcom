"""ChicShop — Admin Accounts"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserAddress, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'is_active', 'is_staff',
                    'is_email_verified', 'date_joined', 'failed_login_attempts']
    list_filter = ['is_active', 'is_staff', 'is_email_verified', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    readonly_fields = ['id', 'date_joined', 'last_login', 'last_login_ip',
                       'failed_login_attempts', 'account_locked_until']

    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Adresse'), {'fields': ('address', 'city')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'is_email_verified', 'groups', 'user_permissions')}),
        (_('Sécurité'), {'fields': ('last_login', 'last_login_ip', 'failed_login_attempts',
                                     'account_locked_until')}),
        (_('Consentements'), {'fields': ('marketing_consent', 'terms_accepted_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'city', 'is_default', 'created_at']
    list_filter = ['city', 'is_default']
    search_fields = ['user__email', 'user__first_name', 'city', 'address']
    readonly_fields = ['id', 'created_at']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'used']
    list_filter = ['used']
    readonly_fields = ['id', 'user', 'token', 'created_at', 'expires_at', 'used']
    # Ne pas permettre la création manuelle de tokens depuis l'admin
    def has_add_permission(self, request):
        return False
