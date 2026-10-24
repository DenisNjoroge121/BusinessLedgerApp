from rest_framework import permissions

class IsOwnerOrHelper(permissions.BasePermission):
    """
    Allows Owners and Helpers to modify data. Viewers are read-only.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # If the action is safe (GET, HEAD, OPTIONS), everyone authenticated can see it
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Otherwise, only OWNER or HELPER can modify
        return request.user.role in ['OWNER', 'HELPER']

class IsOwnerOnly(permissions.BasePermission):
    """
    Strictly for the business owner (e.g., managing categories or users).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'OWNER'
