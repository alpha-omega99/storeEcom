"""ChicShop — Validators, Exceptions, Tasks, Admin — Accounts"""

# ============================================================
# validators.py
# ============================================================
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordStrengthValidator:
    """Validation de force du mot de passe au-delà des règles Django par défaut"""

    def validate(self, password, user=None):
        errors = []
        if not re.search(r'[A-Z]', password):
            errors.append(_("Le mot de passe doit contenir au moins une majuscule."))
        if not re.search(r'[a-z]', password):
            errors.append(_("Le mot de passe doit contenir au moins une minuscule."))
        if not re.search(r'\d', password):
            errors.append(_("Le mot de passe doit contenir au moins un chiffre."))
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>_\-+=/\\]', password):
            errors.append(_("Le mot de passe doit contenir au moins un caractère spécial."))
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Votre mot de passe doit contenir : majuscule, minuscule, chiffre, caractère spécial."
        )
