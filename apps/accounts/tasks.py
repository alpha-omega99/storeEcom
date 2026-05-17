"""
ChicShop — Tâches Celery
Emails, notifications WhatsApp, traitement asynchrone
"""
import logging
import requests
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger('chicshop')
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id: str):
    """Email de bienvenue après inscription"""
    try:
        user = User.objects.get(id=user_id)
        subject = "Bienvenue chez ChicShop 🌸"
        message = (
            f"Bonjour {user.first_name},\n\n"
            f"Votre compte ChicShop a été créé avec succès.\n"
            f"Découvrez notre collection de tapis personnalisés sur chicshop.ci\n\n"
            f"L'équipe ChicShop"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Email de bienvenue envoyé — user={user.email}")
    except User.DoesNotExist:
        logger.error(f"Utilisateur introuvable pour email bienvenue — id={user_id}")
    except Exception as exc:
        logger.error(f"Erreur envoi email bienvenue — {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id: str, token: str):
    """Email de réinitialisation du mot de passe"""
    try:
        user = User.objects.get(id=user_id)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Réinitialisation de votre mot de passe ChicShop"
        message = (
            f"Bonjour {user.first_name},\n\n"
            f"Vous avez demandé une réinitialisation de mot de passe.\n"
            f"Cliquez sur ce lien (valable 1 heure) :\n{reset_url}\n\n"
            f"Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.\n\n"
            f"L'équipe ChicShop"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Email reset password envoyé — user={user.email}")
    except User.DoesNotExist:
        logger.error(f"Utilisateur introuvable pour reset password — id={user_id}")
    except Exception as exc:
        logger.error(f"Erreur envoi email reset — {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_order_confirmation_email(self, order_id: str):
    """Email de confirmation de commande"""
    try:
        from apps.orders.models import Order
        order = Order.objects.select_related('user').get(id=order_id)
        subject = f"Commande #{order.reference} confirmée — ChicShop 🌸"
        message = (
            f"Bonjour {order.customer_first_name},\n\n"
            f"Votre commande #{order.reference} a bien été reçue.\n"
            f"Total : {order.total_amount:,.0f} F CFA\n\n"
            f"Aminata vous contactera dans les 5 minutes sur WhatsApp pour confirmer.\n\n"
            f"L'équipe ChicShop"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False,
        )
        logger.info(f"Email confirmation commande — ref={order.reference}")
    except Exception as exc:
        logger.error(f"Erreur email confirmation commande — {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_admin_new_order_whatsapp(self, order_id: str):
    """
    Notifier Aminata (admin) via WhatsApp Business API
    d'une nouvelle commande
    """
    if not settings.WHATSAPP_API_TOKEN:
        logger.warning("WhatsApp API token non configuré — notification ignorée")
        return

    try:
        from apps.orders.models import Order
        order = Order.objects.select_related('user').prefetch_related('items__product').get(id=order_id)

        items_text = "\n".join([
            f"  • {item.product.name} (x{item.quantity}) — {item.unit_price:,.0f} F"
            for item in order.items.all()
        ])

        message = (
            f"🛍️ *NOUVELLE COMMANDE ChicShop*\n\n"
            f"Réf : #{order.reference}\n"
            f"Client : {order.customer_first_name} {order.customer_last_name}\n"
            f"Tél : {order.customer_phone}\n"
            f"Commune : {order.delivery_city}\n"
            f"Broderie : _{order.embroidery_name}_\n\n"
            f"Articles :\n{items_text}\n\n"
            f"*Total : {order.total_amount:,.0f} F CFA*\n"
            f"Paiement : {order.get_payment_method_display()}\n\n"
            f"✅ À confirmer dans les 5 minutes !"
        )

        url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": settings.WHATSAPP_ADMIN_NUMBER,
            "type": "text",
            "text": {"body": message},
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"WhatsApp admin notifié — commande={order.reference}")

    except Exception as exc:
        logger.error(f"Erreur notification WhatsApp admin — {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_order_status_update(self, order_id: str, new_status: str):
    """Notifier le client d'un changement de statut de commande par email"""
    try:
        from apps.orders.models import Order
        order = Order.objects.get(id=order_id)
        status_labels = {
            'confirmed': 'confirmée',
            'in_embroidery': 'en cours de personnalisation',
            'packaging': 'en cours d\'emballage',
            'shipped': 'expédiée',
            'delivered': 'livrée',
            'cancelled': 'annulée',
        }
        label = status_labels.get(new_status, new_status)
        subject = f"Commande #{order.reference} — {label.capitalize()}"
        message = (
            f"Bonjour {order.customer_first_name},\n\n"
            f"Votre commande #{order.reference} est maintenant : *{label}*.\n\n"
            f"L'équipe ChicShop 🌸"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error(f"Erreur email statut commande — {exc}")
        raise self.retry(exc=exc)
