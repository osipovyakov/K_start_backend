from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, File

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['name', 'data']


class CustomTokenObtainPairSerializer(serializers.Serializer):
    user_id = serializers.CharField()

    def validate(self, attrs):
        user_id = attrs.get('user_id')

        if not user_id:
            raise AuthenticationFailed('user_id is required')

        # Находим пользователя по user_id
        try:
            user = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            raise AuthenticationFailed('User with this user_id does not exist')

        # Создаем токен для найденного пользователя
        refresh = RefreshToken.for_user(user)
        refresh['user_id'] = str(user.user_id)
        access_token = str(refresh.access_token)

        return {
            'access': access_token,
        }