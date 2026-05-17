"""
ChicShop — Middlewares de sécurité
Headers HTTP, logging des requêtes suspectes
"""
import logging
import time

security_logger = logging.getLogger('chicshop.security')


class SecurityHeadersMiddleware:
    """Ajouter des headers de sécurité HTTP à chaque réponse"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Empêcher le cache des réponses sensibles
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'

        # Permissions Policy — désactiver les APIs navigateur non nécessaires
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), payment=()'
        )

        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'

        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response


class RequestLoggingMiddleware:
    """
    Logger les requêtes suspectes :
    - Tentatives sur des URLs sensibles
    - User-Agents suspects (scanners)
    - Requêtes volumineuses
    """
    SUSPICIOUS_PATHS = [
        '/admin/', '/wp-admin/', '/phpmyadmin/', '/.env',
        '/config.php', '/setup.php', '/.git/', '/backup',
    ]
    SUSPICIOUS_UA_KEYWORDS = [
        'sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab',
        'dirbuster', 'gobuster', 'nuclei', 'burpsuite',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        ip = self._get_ip(request)
        path = request.path.lower()
        ua = request.META.get('HTTP_USER_AGENT', '').lower()

        # Détecter les paths suspects
        for suspicious in self.SUSPICIOUS_PATHS:
            if path.startswith(suspicious) and not path.startswith('/chicshop-admin/'):
                security_logger.warning(
                    f"Accès path suspect — path={path} ip={ip} ua={ua[:100]}"
                )
                break

        # Détecter les scanners connus
        for scanner in self.SUSPICIOUS_UA_KEYWORDS:
            if scanner in ua:
                security_logger.warning(
                    f"Scanner détecté — ua={ua[:200]} ip={ip} path={path}"
                )
                break

        response = self.get_response(request)

        # Logger les erreurs serveur
        if response.status_code >= 500:
            duration = time.time() - start_time
            security_logger.error(
                f"Erreur 5xx — status={response.status_code} path={path} "
                f"ip={ip} duration={duration:.3f}s"
            )

        # Logger les 401/403 répétés (tentatives d'accès non autorisé)
        if response.status_code in (401, 403):
            security_logger.warning(
                f"Accès refusé — status={response.status_code} path={path} ip={ip}"
            )

        return response

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
