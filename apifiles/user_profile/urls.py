from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, FileUploadViewSet

router = DefaultRouter()
router.register(r'users', UserProfileViewSet)
router.register(r'files', FileUploadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
