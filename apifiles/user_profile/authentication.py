from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import UserProfile


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')

        if not user_id:
            raise AuthenticationFailed('User ID is missing in the token')

        try:
            return UserProfile.objects.get(user_id=user_id)  # Используем user_id для поиска пользователя
        except UserProfile.DoesNotExist:
            raise AuthenticationFailed('User not found')

        except Exception as e:
            raise AuthenticationFailed(f'Unexpected error: {str(e)}')
