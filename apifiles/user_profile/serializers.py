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
        fields = ['file_id', 'file_name', 'file_type', 'file_base64']


class CustomTokenObtainPairSerializer(serializers.Serializer):
    profile_id = serializers.CharField()

    def validate(self, attrs):
        profile_id = attrs.get('profile_id')

        if not profile_id:
            raise AuthenticationFailed('profile_id is required')

        # Находим пользователя по profile_id
        try:
            user = UserProfile.objects.get(profile_id=profile_id)
        except UserProfile.DoesNotExist:
            raise AuthenticationFailed('User with this profile_id does not exist')

        # Создаем токен для найденного пользователя
        refresh = RefreshToken.for_user(user)
        refresh['profile_id'] = str(user.profile_id)
        access_token = str(refresh.access_token)

        return {
            'access': access_token,
        }