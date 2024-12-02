from rest_framework import serializers
from .models import UserProfile, File

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file_id', 'file_name', 'file_type', 'file_base64', 'profile_id', 'project_id']
