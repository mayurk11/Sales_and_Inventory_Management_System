from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
    
    
class IsDealerUser(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'dealer')