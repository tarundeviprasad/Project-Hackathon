from rest_framework.permissions import BasePermission


class IsPatientOwnerOrPrivileged(BasePermission):
    message = 'You are not allowed to access this patient record.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True
        return getattr(obj, 'user_id', None) == user.id