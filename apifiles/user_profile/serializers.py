import base64
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, File

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class FileSerializerPost(serializers.ModelSerializer):
    file_name = serializers.CharField(write_only=True)
    file_base64 = serializers.CharField(write_only=True)
    file_type = serializers.CharField(write_only=True, default='document')

    class Meta:
        model = File
        fields = ['file_name', 'file_base64', 'file_type']
    
    def validate(self, attrs):
        # Проверяем наличие обязательных полей
        if not attrs.get('file_name'):
            raise serializers.ValidationError({'file_name': 'This field is required.'})
        if not attrs.get('file_base64'):
            raise serializers.ValidationError({'file_base64': 'This field is required.'})
        if not attrs.get('file_type'):
            raise serializers.ValidationError({'file_type': 'This field is required.'})

        return attrs

    def create(self, validated_data):
        # Извлекаем значения из сериализованных данных
        file_name = validated_data.pop('file_name')
        file_base64 = validated_data.pop('file_base64')
        file_type = validated_data.pop('file_type')

        # Преобразуем Base64 данные
        data = {
            'file_name': file_name,
            'file_base64': file_base64,
            'file_type': file_type
        }

        # Создаем запись в базе данных
        file_instance = File.objects.create(
            **validated_data, 
            data=data  # Сохраняем данные в поле 'data'
        )

        return file_instance


class FileSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


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