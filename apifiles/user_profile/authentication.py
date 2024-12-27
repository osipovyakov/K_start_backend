from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        if user_id:
            try:
                return UserProfile.objects.get(user_id=user_id)
            except UserProfile.DoesNotExist:
                raise AuthenticationFailed('User not found')
        raise AuthenticationFailed('Invalid user_id')
