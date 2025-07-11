from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

class IsOwnerOrAdmin(BasePermission):
    message = _('You must be the owner of this object or an admin.')

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff

class IsAdminUser(BasePermission):
    message = _('You must be an administrator to perform this action.')

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsVerifiedUser(BasePermission):
    message = _('User account must be verified.')

    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_verified', False)