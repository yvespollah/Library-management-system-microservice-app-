from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import requests
from django.conf import settings

class GatewayAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Ce middleware peut être étendu pour gérer l'authentification réelle
        # Par exemple, vérifier un token JWT avec le service utilisateur
        
        
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            # Pour les routes qui ne nécessitent pas d'authentification
            if request.path.startswith('/api/books/') and request.method == 'GET':
                return (None, None)
            
            raise AuthenticationFailed('Authentification requise')
        
        # En situation réelle, vérifiez le token avec le service utilisateur
        # Validation simple pour la démo
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Dans une implémentation réelle, vérifiez le token avec le service utilisateur
            if token == "demo-token":  # Valeur simplifiée pour la démo
                return ({"user_id": 1, "username": "demo_user"}, None)
            
        raise AuthenticationFailed('Token invalide')