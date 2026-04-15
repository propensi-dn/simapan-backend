from rest_framework.permissions import BasePermission


class IsStaffOrAbove(BasePermission):
    """
    Hanya user dengan role STAFF, MANAGER, atau CHAIRMAN yang diizinkan.
    """
    message = 'Akses ditolak. Hanya petugas yang dapat mengakses endpoint ini.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ['STAFF', 'MANAGER', 'CHAIRMAN']
        )


class IsManagerOrAbove(BasePermission):
    """
    Hanya user dengan role MANAGER atau CHAIRMAN yang diizinkan.
    """
    message = 'Akses ditolak. Hanya manajer/ketua yang dapat mengakses endpoint ini.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ['MANAGER', 'CHAIRMAN']
        )
