from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(permissions.BasePermission):
    message = 'У Вас нет прав модератора.'

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()


class IsNotModerator(BasePermission):
    """Разрешает доступ только пользователям, НЕ входящим в группу модераторов."""
    message = 'Модераторы не могут выполнять это действие.'

    def has_permission(self, request, view):
        return not request.user.groups.filter(name="moders").exists()


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsModeratorOrOwner(BasePermission):
    """Разрешает доступ модераторам или владельцам объекта."""
    message = 'У Вас нет прав на это действие.'

    def has_permission(self, request, view):
        # На уровне списка пропускаем всех авторизованных (queryset отфильтрует)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Модератор может всё, владелец — только свой объект
        if request.user.groups.filter(name="moders").exists():
            return True
        return obj.owner == request.user


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        return obj == request.user
