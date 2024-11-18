import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileSerializer, UserPhoto
from rest_framework import viewsets
from django.conf import settings
import os

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        user_profile = self.get_object()
        file_data = request.data.get('file')

        if file_data:
            try:
                # Декодируем base64
                file_name = request.data.get('file_name', 'photo.png')
                file_mime = request.data.get('file_mime', 'image/png')

                # Преобразуем base64 в изображение
                img_data = base64.b64decode(file_data)
                image = Image.open(BytesIO(img_data))

                # Формируем имя изображения
                image_name = f'{user_profile.profile_id}_{file_name}'

                # Сохраняем изображение в файловое хранилище
                # Создаем объект ContentFile для сохранения файла
                image_file = ContentFile(img_data, name=image_name)
                image_path = default_storage.save(f'user_photos/{image_name}', image_file)

                # Сохраняем путь к изображению в модели
                user_profile.photo_main = image_path
                user_profile.save()

                # Возвращаем успешный ответ
                return Response({'status': 'photo uploaded'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
