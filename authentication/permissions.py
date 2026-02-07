from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Allows access only to admin users.

    Admin is determined by (in order):
    - `request.user.is_admin` claim (stateless JWT)
    - Django user flags `is_staff` / `is_superuser`
    """

    message = 'Admin access required.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        if getattr(user, 'is_admin', False):
            return True
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
            return True
        return False


class IsSuperAdminUser(BasePermission):
    """Allows access only to superadmin users.

    Superadmin is determined by (in order):
    - `request.user.is_superadmin` claim (stateless JWT)
    - Django user flag `is_superuser`
    """

    message = 'Super admin access required.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        if getattr(user, 'is_superadmin', False):
            return True
        if getattr(user, 'is_superuser', False):
            return True
        return False
