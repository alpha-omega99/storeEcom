"""ChicShop — Gestionnaire d'exceptions uniforme"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('chicshop')


def custom_exception_handler(exc, context):
    """
    Handler personnalisé — messages d'erreur uniformes.
    Évite de fuiter des détails techniques en production.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Uniformiser le format des erreurs
        error_data = {
            'status': 'error',
            'status_code': response.status_code,
            'errors': response.data,
        }

        # Message lisible pour les erreurs courantes
        if response.status_code == 401:
            error_data['message'] = "Authentification requise."
        elif response.status_code == 403:
            error_data['message'] = "Vous n'avez pas la permission d'effectuer cette action."
        elif response.status_code == 404:
            error_data['message'] = "Ressource introuvable."
        elif response.status_code == 429:
            error_data['message'] = "Trop de requêtes. Veuillez patienter avant de réessayer."
        elif response.status_code >= 500:
            error_data['message'] = "Erreur interne. Notre équipe a été alertée."
            logger.error(f"Erreur 5xx — {exc}", exc_info=True)

        return Response(error_data, status=response.status_code)

    # Erreurs non gérées par DRF (exceptions Python non prévues)
    logger.critical(f"Exception non gérée — {exc}", exc_info=True)
    return Response(
        {
            'status': 'error',
            'status_code': 500,
            'message': "Une erreur inattendue s'est produite.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
