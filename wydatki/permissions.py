from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if str(request.user) == 'admin':
            return True
        return obj.kto_kupil == request.user.uzytkownik

class IsUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if str(request.user) == 'admin':
            return True
        return obj.id == request.user.id