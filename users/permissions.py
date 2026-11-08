from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(permissions.BasePermission):
    message = 'У Вас нет прав модератора.'

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user
