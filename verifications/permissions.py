from rest_framework import permissions

from users.models import UserRole

STAFF_ROLES = {UserRole.STAFF, UserRole.MANAGER, UserRole.CHAIRMAN}


class IsStaffOrAbove(permissions.BasePermission):
    """
    Allows access only to users with role STAFF, MANAGER, or CHAIRMAN.
    """
    message = 'Hanya petugas atau di atas yang dapat mengakses fitur ini.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in STAFF_ROLES
        )