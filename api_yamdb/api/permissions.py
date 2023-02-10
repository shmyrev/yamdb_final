from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Пермишн для админа"""
    message = 'Вы должны иметь права администратора'

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Пермишн для админа и только для чтения"""
    def has_permission(self, request, view):

        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser))


class IsAdminOrIsModeratorOrIsUser(permissions.BasePermission):
    """Пермишн только авторам, админам, модераторам."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin or request.user.is_moderator
            or obj.author == request.user)
