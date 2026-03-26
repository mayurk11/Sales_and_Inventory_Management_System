from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
    
    
class IsDealerUser(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'dealer')
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsDealerUser()]

        elif self.action == 'confirm':
            return [IsDealerUser()]   # ✅ Dealer confirms

        elif self.action == 'deliver':
            return [IsAdminUserCustom()]  # ✅ Admin delivers

        return super().get_permissions()