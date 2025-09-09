from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем или модератором"""

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name="moderators").exists():
            return True
        return obj.owner == request.user


class IsPaymentOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем платежа"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPaymentOwnerOrModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем платежа или модератором"""

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name="moderators").exists():
            return True
        return obj.user == request.user
