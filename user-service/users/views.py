from rest_framework import viewsets
from .models import LibraryUser
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = LibraryUser.objects.all()
    serializer_class = UserSerializer