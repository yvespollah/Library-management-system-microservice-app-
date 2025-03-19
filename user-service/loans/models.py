from django.db import models
from django.utils import timezone
from users.models import LibraryUser

class Loan(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )
    
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name='loans')
    book_id = models.IntegerField()  # ID externe du livre du service de livres
    book_title = models.CharField(max_length=200)  # Stockage dénormalisé pour éviter trop d'appels
    loan_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.user.username} - {self.book_title}"