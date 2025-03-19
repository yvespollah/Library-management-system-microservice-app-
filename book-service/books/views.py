
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Book
from .serializers import BookSerializer
from rest_framework.response import Response

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_queryset(self):
        queryset = Book.objects.all()
        title = self.request.query_params.get('title', None)
        author = self.request.query_params.get('author', None)
        category = self.request.query_params.get('category', None)
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)
        if category:
            queryset = queryset.filter(category__icontains=category)
            
        return queryset

    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        book = self.get_object()
        return Response({
            'book_id': book.id,
            'title': book.title,
            'available': book.available_copies > 0,
            'copies': book.available_copies
        })