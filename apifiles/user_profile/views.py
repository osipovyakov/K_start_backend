import base64
import filetype
import magic
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, File, CustomStorage
from .serializers import UserProfileSerializer, FileSerializer
from rest_framework import viewsets
from django.conf import settings
import os
from rest_framework.permissions import IsAuthenticated

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    http_method_names = ['get', 'post']


class FileUploadViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        profile_id = request.data.get('profile_id')
        file_name = request.data.get('file_name', 'uploaded_file')
        file_base64 = request.data.get('file_base64')
        file_type = request.data.get('file_type', 'document')
        project_id = request.data.get('project_id')

        # Проверка обязательных параметров
        if not profile_id or not file_base64:
            return Response(
                {"error": 'Параметры profile_id и file_base64 обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        try:
            # Получаем объект пользователя
            user_profile = UserProfile.objects.get(profile_id=profile_id)

            # Декодируем Base64
            file_data_decoded = base64.b64decode(file_base64)
            
            # Определяем переданный пользователем формат
            try:
                file_mime_user = file_name.split('.')[1]
            except IndexError:
                return Response({'error': 'file_name должен быть в виде *название*.*формат*'},
                status=status.HTTP_400_BAD_REQUEST)
            

            # Определяем MIME-тип и расширение с помощью filetype
            kind = filetype.guess(file_data_decoded)

            # Если формат не удалось определить, то берем формат от пользователя
            if not kind:
                file_extension = file_mime_user
            else:
                file_mime = kind.mime
                file_extension = kind.extension


            # Генерируем имя файла с расширением
            file_name_with_extension = f"{file_name.split('.')[0]}.{file_extension}"
            file_relative_path = os.path.join(
                f'files/{list(profile_id)[0]}/{list(profile_id)[1]}/{file_name_with_extension}')


            file_content = ContentFile(file_data_decoded, name=file_name_with_extension)

            # Используем файловое хранилище для сохранения файла
            custom_storage = CustomStorage()
            saved_file_path = custom_storage.save(file_relative_path, file_content)

            # Создаем объект ContentFile для хранения файла
            file_instance = File.objects.create(
                file_name=file_name,
                file_type=file_type,
                file_mime=file_mime,
                file_base64=file_base64,
                profile_id=profile_id,
                project_id=project_id,
            )

            # Сохраняем файл и путь к нему в модели
            user_profile.file_field = file_relative_path
            user_profile.save()

            return Response({'status': 'File uploaded successfully'}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({'error': 'UserProfile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)