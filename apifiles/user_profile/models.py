from django.db import models
import uuid
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.postgres.indexes import GinIndex


def meta_default_value(internal_id_placeholder=None):
    return {
        "status": "active",
        "flags": 0,
        "internal_id": internal_id_placeholder
    }


def data_default_value():
    return {}


# Хранилище для изображений
class CustomStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None):
        # Используем стандартное хранилище файлов в MEDIA_ROOT
        location = location or settings.MEDIA_ROOT
        base_url = base_url or settings.MEDIA_URL
        super().__init__(location=location, base_url=base_url)

class UserProfile(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    project_id = models.UUIDField(default=uuid.uuid4, editable=True, unique=False)
    account_id = models.UUIDField(default=uuid.uuid4, editable = True, unique=False)
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
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    project_id = models.UUIDField(default=None, null=True)
    account_id = models.UUIDField(default=None, null=True)
    user_id = models.UUIDField(default=None, null=True)
    object_type = models.CharField(max_length=254, null=True)
    object_item = models.UUIDField(default=None, null=True) # = Profile_ID
    object_code = models.CharField(max_length=254, null=True, unique=True) # = phone or email
    name = models.CharField(max_length=254, null=False)
    meta = models.JSONField(default=meta_default_value)
    data = models.JSONField(default=data_default_value, null=True)
    
    
    class Meta:
        indexes = [
            GinIndex(fields=['data'], name='files_data_gin'),
            models.Index(fields=['object_item'], name='files_object_item_idx'),
            models.Index(fields=['created_date'], name='files_cr_date_idx'),
            models.Index(fields=['modified_date'], name='files_mod_date_idx'),
            models.Index(fields=['object_item', 'object_type'], name='files_o_item_type_idx'),
            models.Index(fields=['project_id', 'account_id', 'user_id'], name='files_p_a_u_ids_idx'),
            models.Index(fields=['account_id', 'user_id'], name='files_a_u_ids_idx'),
            models.Index(fields=['user_id'], name='files_user_id_idx')
        ]
        ordering = ['-meta__internal_id']
