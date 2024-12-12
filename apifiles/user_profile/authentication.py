from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        profile_id = validated_token.get('profile_id')
        if profile_id:
            try:
                return UserProfile.objects.get(profile_id=profile_id)
            except UserProfile.DoesNotExist:
                raise AuthenticationFailed('User not found')
        raise AuthenticationFailed('Invalid profile_id')
