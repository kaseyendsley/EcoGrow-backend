from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    - SAFE methods (GET, HEAD, OPTIONS): allow anyone
    - POST/PUT/PATCH/DELETE: require auth
    - Object-level for non-safe methods: only owner or staff
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and (request.user.is_staff or getattr(obj, "created_by_id", None) == request.user.id))
