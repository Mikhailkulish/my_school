from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    message = 'У Вас нет прав модератора.'

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()
