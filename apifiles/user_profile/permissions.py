from rest_framework import permissions

class IsAuthenticatedForNonGet(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method == 'GET':
            return True  # Разрешить доступ для GET-запросов
        return (bool(request.user))