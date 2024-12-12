from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from user_profile.views import CustomTokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

swagger_info = openapi.Info(
    title="Your API",
    default_version="v1",
    description="Test description",
    contact=openapi.Contact(email="contact@yourapi.local"),
)

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
        description="Test description",
        contact=openapi.Contact(email="contact@yourapi.local"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_profile.urls')),
    path('users/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)