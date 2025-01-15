import base64
import os
import filetype
from django.utils.timezone import now
from django.core.files.base import ContentFile
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import UserProfile, File, CustomStorage
from .serializers import UserProfileSerializer, FileSerializerRead, CustomTokenObtainPairSerializer, FileSerializerPost
from .permissions import IsAuthenticatedForNonGet
from .authentication import CustomJWTAuthentication

header_params = [
    openapi.Parameter('Project-ID', openapi.IN_HEADER, description="Project ID", type=openapi.TYPE_STRING),
    openapi.Parameter('Account-ID', openapi.IN_HEADER, description="Account ID", type=openapi.TYPE_STRING),
    openapi.Parameter('User-ID', openapi.IN_HEADER, description="User ID", type=openapi.TYPE_STRING),
    openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING),
]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Используем сериализатор для валидации данных
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем access токен
        access_token = serializer.validated_data['access']

        # Возвращаем его в заголовке
        response = Response({"message": "Token issued successfully"})
        response['Authorization'] = f"Bearer {access_token}"
        return response

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticatedForNonGet]


class FileUploadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedForNonGet]
    authentication_classes = [CustomJWTAuthentication]
    queryset = File.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FileSerializerPost
        return FileSerializerRead

    @swagger_auto_schema(manual_parameters=header_params)
    def create(self, request, *args, **kwargs):
        required_headers = ['User-ID']
        missing_headers = [header for header in required_headers if not request.headers.get(header)]
        if missing_headers:
            return Response(
                {"error": f"Missing required headers: {', '.join(missing_headers)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.user.user_id
        user_id_from_headers = request.headers.get('User-ID')
        if user_id != user_id_from_headers:
            return Response(
                {"error": "User ID from token does not match User ID from headers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        account_id = request.headers['Account-ID']
        project_id = request.headers['Project-ID']
        file_base64 = request.data.get('file_base64')
        file_name = request.data.get('file_name', 'uploaded_file')
        file_type = request.data.get('file_type', 'document')


        try:
            file_data_decoded = base64.b64decode(file_base64)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid Base64 string for file_base64"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            object_code = user_profile.contact_phone or user_profile.contact_email or ''
        except UserProfile.DoesNotExist:
            return Response({'error': 'UserProfile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


        try:
            file_extension = self._get_file_extension(file_name, file_data_decoded)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        file_name_with_extension = f"{file_name.split('.')[0]}.{file_extension}"
        file_relative_path = os.path.join(
            f'files/{str(user_id)[0]}/{str(user_id)[1]}/{file_name_with_extension}'
        )

        try:
            custom_storage = CustomStorage()
            custom_storage.save(file_relative_path, ContentFile(file_data_decoded, name=file_name_with_extension))

            File.objects.create(
                created_date=now(),
                modified_date=now(),
                user_id=user_id,
                account_id=account_id,
                project_id=project_id,
                object_type=file_type,
                object_item=user_id,
                object_code=object_code,
                name=file_name_with_extension,
                meta={"status": "active", "flags": 0, "internal_id": ""},
                data={'file_mime': file_extension, 'file_data': file_base64}
            )

            user_profile.file_field = file_relative_path
            user_profile.save()

            return Response({'status': 'File uploaded successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_file_extension(self, file_name, file_data_decoded):
        # Проверяем, есть ли расширение в имени файла
        if '.' in file_name:
            file_extension = file_name.split('.')[-1]
        else:
            raise ValueError('file_name must include a valid extension')

        # Используем filetype для определения реального типа файла
        kind = filetype.guess(file_data_decoded)
        if kind:
            # Если мы смогли определить MIME-тип, и он отличается от расширения в имени файла, выберем тип от filetype
            if file_extension.lower() != kind.extension.lower():
                file_extension = kind.extension

        return file_extension
