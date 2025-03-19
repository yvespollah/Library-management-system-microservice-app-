from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Loan
from .serializers import LoanSerializer
from django.utils import timezone
import datetime
import requests
from django.conf import settings

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    
    def create(self, request, *args, **kwargs):
        # Récupérer les informations du livre depuis le service de livres
        book_id = request.data.get('book_id')
        try:
            book_response = requests.get(f"{settings.BOOK_SERVICE_URL}{book_id}/check_availability/")
            book_data = book_response.json()
            
            if not book_data.get('available'):
                return Response(
                    {"error": "Ce livre n'est pas disponible pour l'emprunt"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            mutable_data = request.data.copy()

            # Ajouter le titre du livre à la demande
            mutable_data['book_title'] = book_data.get('title')

            # Définir la date d'échéance à 14 jours à partir d'aujourd'hui
            due_date = timezone.now() + datetime.timedelta(days=14)
            mutable_data['due_date'] = due_date

            # Mettre à jour les données dans la requête
            # En créant un objet "request" temporaire avec les données modifiées
            request._full_data = mutable_data  # Remplacer les données dans l'objet request

            # Créer l'emprunt en passant les données modifiées
            response = super().create(request, *args, **kwargs)

            # Mettre à jour la disponibilité dans le service de livres
            update_response = requests.patch(
                f"{settings.BOOK_SERVICE_URL}{book_id}/",
                json={"available_copies": book_data.get('copies') - 1},
                headers={"Content-Type": "application/json"}
            )

            return response

            
        except requests.RequestException as e:
            return Response(
                {"error": f"Erreur de communication avec le service de livres: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()
        if loan.status == 'returned':
            return Response(
                {"error": "Ce livre a déjà été retourné"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour l'emprunt
        loan.return_date = timezone.now()
        loan.status = 'returned'
        loan.save()
        
        # Mettre à jour la disponibilité dans le service de livres
        try:
            book_response = requests.get(f"{settings.BOOK_SERVICE_URL}{loan.book_id}/")
            book_data = book_response.json()
            
            update_response = requests.patch(
                f"{settings.BOOK_SERVICE_URL}{loan.book_id}/",
                json={"available_copies": book_data.get('available_copies') + 1},
                headers={"Content-Type": "application/json"}
            )
            
            return Response(LoanSerializer(loan).data)
            
        except requests.RequestException as e:
            return Response(
                {"error": f"Le livre a été retourné, mais erreur de mise à jour du service de livres: {str(e)}"},
                status=status.HTTP_200_OK
            )
    
    @action(detail=False, methods=['get'])
    def user_history(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "Paramètre user_id requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loans = Loan.objects.filter(user_id=user_id)
        return Response(LoanSerializer(loans, many=True).data)