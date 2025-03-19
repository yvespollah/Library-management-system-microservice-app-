from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
import json
from .auth import GatewayAuthentication
from rest_framework.decorators import api_view


# ProxyView est une vue API générique qui intercepte et redirige les requêtes vers un microservice.
class ProxyView(APIView):
    authentication_classes = [GatewayAuthentication]


    # Elle retourne l’URL du microservice cible en fonction de la requête.
    def get_service_url(self, request):
        # À implémenter dans les classes enfants BookServiceView, UserServiceView ,etc
        raise NotImplementedError
    

    # Cette méthode prend une requête entrante et la redirige vers le bon microservice.
    def proxy_request(self, request, *args, **kwargs):
        # Construire l'URL du service
        service_url = self.get_service_url(request) # Récupère l’URL du microservice cible (défini dans get_service_url des classes enfants).
        
        # Préparer les headers
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Si l'utilisateur est authentifié, ajouter les infos dans un header personnalisé
        if request.user and hasattr(request.user, 'get'):
            user_info = request.user
            headers['X-User-Info'] = json.dumps(user_info)
        
        # Proxy la méthode appropriée
        method = request.method.lower()
        request_data = request.data if method in ['post', 'put', 'patch'] else None
        
        try:
            if method == 'get':
                response = requests.get(service_url, headers=headers, params=request.query_params)
            elif method == 'post':
                response = requests.post(service_url, headers=headers, json=request_data)
            elif method == 'put':
                response = requests.put(service_url, headers=headers, json=request_data)
            elif method == 'patch':
                response = requests.patch(service_url, headers=headers, json=request_data)
            elif method == 'delete':
                response = requests.delete(service_url, headers=headers)
            else:
                return Response({"error": "Méthode non supportée"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
            # Retourner la réponse du service
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
                
            return Response(response_data, status=response.status_code)
            
        except requests.RequestException as e:
            return Response(
                {"error": f"Erreur de communication avec le service: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def get(self, request, *args, **kwargs):
        return self.proxy_request(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.proxy_request(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.proxy_request(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.proxy_request(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.proxy_request(request, *args, **kwargs)

class BookServiceView(ProxyView):
    def get_service_url(self, request):
        path = request.path.replace('/api/books', '')
        return f"{settings.MICROSERVICES['BOOK_SERVICE']}books{path}"

class UserServiceView(ProxyView):
    def get_service_url(self, request):
        path = request.path.replace('/api/users', '')
        return f"{settings.MICROSERVICES['USER_SERVICE']}users{path}"

class LoanServiceView(ProxyView):
    def get_service_url(self, request):
        path = request.path.replace('/api/loans', '')
        return f"{settings.MICROSERVICES['USER_SERVICE']}loans{path}"
    



@api_view(['GET'])
def health_check(request):
    services_status = {}
    
    # Vérifier le service de livres
    try:
        book_response = requests.get(f"{settings.MICROSERVICES['BOOK_SERVICE']}books/", timeout=2)
        services_status['book_service'] = {
            'status': 'up' if book_response.status_code == 200 else 'error',
            'code': book_response.status_code
        }
    except requests.RequestException:
        services_status['book_service'] = {'status': 'down'}
    
    # Vérifier le service d'utilisateurs
    try:
        user_response = requests.get(f"{settings.MICROSERVICES['USER_SERVICE']}users/", timeout=2)
        services_status['user_service'] = {
            'status': 'up' if user_response.status_code == 200 else 'error',
            'code': user_response.status_code
        }
    except requests.RequestException:
        services_status['user_service'] = {'status': 'down'}
    
    return Response({
        'gateway': 'up',
        'services': services_status
    })