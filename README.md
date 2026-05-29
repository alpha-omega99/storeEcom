# 🌸 ChicShop — Backend Django

Backend REST API complet et sécurisé pour la boutique ChicShop (tapis de prière personnalisés — Abidjan).

---

## 🏗️ Structure du Projet

```
chicshop_backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # Config commune (sécurisée)
│   │   ├── development.py   # Dev (SQLite, CORS ouvert)
│   │   └── production.py    # Prod (HTTPS, HSTS, headers stricts)
│   ├── urls.py              # URL root
│   ├── wsgi.py
│   └── celery.py            # File de tâches asynchrones
│
├── apps/
│   ├── accounts/            # Utilisateurs, auth JWT, adresses
│   │   ├── models.py        # User UUID, verrouillage compte, RGPD
│   │   ├── serializers.py   # Validation & sanitisation XSS
│   │   ├── views.py         # Login sécurisé, register, reset pwd
│   │   ├── middleware.py    # Headers sécurité + logs audit
│   │   ├── tasks.py         # Emails + WhatsApp asynchrones
│   │   ├── validators.py    # Force mot de passe
│   │   ├── exceptions.py    # Handler erreurs uniforme
│   │   ├── admin.py
│   │   └── urls.py
│   │
│   ├── products/            # Catalogue, catégories, avis, codes promo
│   │   ├── models.py
│   │   ├── views.py         # Liste, détail, avis, promo
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── orders/              # Commandes (recalcul prix serveur)
│   │   ├── models.py        # Order + OrderItem avec snapshots
│   │   ├── views.py         # Création avec transaction atomique
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   └── payments/            # Mobile Money (Orange Money, Wave)
│       ├── models.py        # Audit trail immuable
│       ├── views.py         # Webhooks HMAC, anti-rejeu
│       ├── urls.py
│       └── admin.py
│
├── requirements.txt
├── manage.py
├── .env.example
└── README.md
```

---

## 🚀 Installation

### 1. Cloner & environnement virtuel
```bash
git clone https://github.com/votre-repo/chicshop_backend.git
cd chicshop_backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos vraies valeurs
nano .env
```

### 3. Base de données
```bash
# Développement (SQLite)
python manage.py migrate --settings=config.settings.development

# Production (PostgreSQL)
python manage.py migrate --settings=config.settings.production
```

### 4. Données initiales
```bash
python manage.py shell --settings=config.settings.development
```
```python
from apps.products.models import Category, Product
from django.utils import timezone
from datetime import timedelta

# Catégories
cat_pack = Category.objects.create(name="Packs cadeaux", slug="pack", icon="🎁", order=1)
cat_tapis = Category.objects.create(name="Tapis de prière", slug="tapis", icon="🕌", order=2)
cat_chapelet = Category.objects.create(name="Chapelets", slug="chapelet", icon="📿", order=3)

# Produits (exemple)
Product.objects.create(
    name="Le Duo Essentiel",
    slug="duo-essentiel",
    category=cat_pack,
    price=8990,
    original_price=11200,
    badge="NEW",
    emoji="🌸",
    allows_embroidery=True,
    is_featured=True,
    stock_quantity=50,
    description="Le pack idéal pour débuter...",
    included_items=["Tapis brodé", "Chapelet", "Emballage cadeau"],
)

# Code promo
from apps.products.models import PromoCode
PromoCode.objects.create(
    code="CHICSHOP15",
    discount_percent=15,
    max_uses=1000,
    min_order_amount=5000,
    valid_from=timezone.now(),
    valid_until=timezone.now() + timedelta(days=365),
)
```

### 5. Superuser admin
```bash
python manage.py createsuperuser --settings=config.settings.development
```

### 6. Lancer le serveur
```bash
# Développement
python manage.py runserver --settings=config.settings.development

# Celery (dans un autre terminal)
celery -A config worker --loglevel=info

# Production (Gunicorn)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🔌 Endpoints API

| Méthode | URL | Description | Auth |
|---------|-----|-------------|------|
| `POST` | `/api/v1/auth/register/` | Inscription | Publique |
| `POST` | `/api/v1/auth/login/` | Login → JWT | Publique |
| `POST` | `/api/v1/auth/logout/` | Logout (blacklist JWT) | JWT |
| `POST` | `/api/v1/auth/token/refresh/` | Rafraîchir le JWT | JWT |
| `GET/PATCH` | `/api/v1/auth/profile/` | Profil utilisateur | JWT |
| `POST` | `/api/v1/auth/change-password/` | Changer mot de passe | JWT |
| `POST` | `/api/v1/auth/password-reset/` | Demander reset | Publique |
| `POST` | `/api/v1/auth/password-reset/confirm/` | Confirmer reset | Publique |
| `GET/POST` | `/api/v1/auth/addresses/` | Adresses livraison | JWT |
| `GET` | `/api/v1/products/` | Liste produits | Publique |
| `GET` | `/api/v1/products/categories/` | Catégories | Publique |
| `GET` | `/api/v1/products/{slug}/` | Détail produit | Publique |
| `POST` | `/api/v1/products/{slug}/reviews/` | Déposer un avis | Publique |
| `POST` | `/api/v1/products/promo/validate/` | Valider code promo | Publique |
| `POST` | `/api/v1/orders/` | Créer commande | Optionnelle |
| `GET` | `/api/v1/orders/my-orders/` | Mes commandes | JWT |
| `GET` | `/api/v1/orders/{ref}/` | Détail commande | JWT/Email |
| `POST` | `/api/v1/payments/initiate/` | Initier paiement MM | Publique |
| `POST` | `/api/v1/payments/webhook/{provider}/` | Webhook paiement | HMAC |

---

## 🔒 Sécurité — Ce qui est protégé

| Menace | Protection |
|--------|-----------|
| **Brute-force login** | Rate limiting 5/min + verrouillage compte 30 min |
| **Injection SQL** | ORM Django uniquement, `ATOMIC_REQUESTS=True` |
| **XSS** | `bleach` sur tous les champs texte, CSP headers |
| **CSRF** | Token CSRF + `CSRF_TRUSTED_ORIGINS` |
| **IDOR** | Filtre `user=request.user` avant tout accès |
| **Énumération comptes** | Réponse identique email existant/inexistant |
| **Timing attack** | `hmac.compare_digest` + délais artificiels |
| **Clickjacking** | `X-Frame-Options: DENY` |
| **MITM** | HSTS 1 an + `SECURE_SSL_REDIRECT` |
| **Token JWT exposé** | Durée courte (30 min) + blacklist à la déconnexion |
| **Rejeu webhook** | `external_transaction_id` unique + signature HMAC |
| **Prix manipulés** | Recalcul **côté serveur** à chaque commande |
| **Scan automatique** | Middleware détection User-Agent scanners |
| **Mots de passe faibles** | Argon2 + validation force personnalisée |
| **Accès admin** | URL `/chicshop-admin/` non standard |

---

## ⚙️ Variables d'environnement (.env)

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Clé secrète Django (générer avec `get_random_secret_key()`) |
| `DEBUG` | `False` en production |
| `DATABASE_URL` | URL PostgreSQL |
| `REDIS_URL` | URL Redis (cache + sessions) |
| `WHATSAPP_API_TOKEN` | Token WhatsApp Business API |
| `WHATSAPP_ADMIN_NUMBER` | Numéro d'Aminata pour les notifications |
| `EMAIL_HOST_PASSWORD` | Mot de passe SMTP |

---

## 📦 Technologies

- **Django 5** + **Django REST Framework**
- **JWT** via `djangorestframework-simplejwt`
- **PostgreSQL** (prod) / SQLite (dev)
- **Redis** (cache, sessions, Celery)
- **Celery** (tâches asynchrones : emails, WhatsApp)
- **Argon2** (hachage mot de passe — OWASP)
- **Bleach** (sanitisation XSS)
- **Gunicorn** + **Whitenoise** (prod)
- **drf-spectacular** (doc Swagger auto)

---

> 🌸 **ChicShop** — *Le tapis qui porte son nom.* · Abidjan, Côte d'Ivoire
