from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff and not request.user.is_superuser