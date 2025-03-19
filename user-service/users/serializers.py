from rest_framework import serializers
from .models import LibraryUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user