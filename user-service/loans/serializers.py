from rest_framework import serializers
from .models import Loan

class LoanSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Loan
        fields = ['id', 'user', 'username', 'book_id', 'book_title', 'loan_date', 'due_date', 'return_date', 'status']
        read_only_fields = ['loan_date', 'status']