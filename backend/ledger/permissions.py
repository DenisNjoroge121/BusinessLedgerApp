from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


def _member(request):
    user = request.user
    return bool(user and user.is_authenticated and user.business_id)


class OwnerWritesMemberReads(BasePermission):
    """Any member can read; only the Owner can change."""

    def has_permission(self, request, view):
        if not _member(request):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == User.Role.OWNER


class StaffWritesViewerReads(BasePermission):
    """Everyone reads; Owner and Helper add/change; only Owner deletes."""

    def has_permission(self, request, view):
        if not _member(request):
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == "DELETE":
            return request.user.role == User.Role.OWNER
        return request.user.role in (User.Role.OWNER, User.Role.HELPER)


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return _member(request) and request.user.role == User.Role.OWNER