from django.db import models
import uuid
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Хранилище для изображений
class CustomStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None):
        # Используем стандартное хранилище файлов в MEDIA_ROOT
        location = location or settings.MEDIA_ROOT
        base_url = base_url or settings.MEDIA_URL
        super().__init__(location=location, base_url=base_url)

class UserProfile(models.Model):
    profile_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    project_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    profile_type = models.CharField(max_length=20, choices=[('anonymous', 'Anonymous'), ('person', 'Person')])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField()
    sex = models.CharField(max_length=6, choices=[('male', 'Male'), ('female', 'Female')])
    contact_phone = models.JSONField()
    contact_email = models.JSONField()
    file_field = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class File(models.Model):
    file_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    file_name = models.CharField(max_length=30)
    file_type = models.CharField(max_length=20, choices=[('document', 'Document'), ('avatar', 'Avatar')])
    file_mime = models.CharField(max_length=10)
    file_base64 = models.TextField(null=False, blank=False)
    profile_id = models.UUIDField(null=False, blank=False)
    project_id = models.UUIDField(null=False, blank=False)

    def __str__(self):
        return f'{self.file_name} {self.file_type}'
