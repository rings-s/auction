# back/base/permissions.py (Fixed version)

from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.translation import gettext_lazy as _

# --- Core Status/Role Permissions ---

class IsVerifiedUser(BasePermission):
    message = _('User account must be verified.')
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'is_verified') and request.user.is_verified

    
    
class IsAdminUser(BasePermission):
    """
    Allows access only to admin users (is_staff).
    Use this for view-level access specific to staff.
    """
    message = _('You must be an administrator (staff) to perform this action.')

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsAppraiser(BasePermission):
    """Allows access only to appraiser users or superusers."""
    message = _('You must be an appraiser to perform this action.')

    def has_permission(self, request, view):
        # Check authentication first to avoid attribute errors
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Then check role or superuser status
        return request.user.role == 'appraiser' or request.user.is_superuser

class IsDataEntry(BasePermission):
    """Allows access only to data entry specialists or superusers."""
    message = _('You must be a data entry specialist to perform this action.')

    def has_permission(self, request, view):
        # Check authentication first to avoid attribute errors
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Then check role or superuser status
        return request.user.role == 'data_entry' or request.user.is_superuser

# --- Object Ownership / Specific Relation Permissions ---

class IsObjectOwner(BasePermission):
    """
    Generic check: Allows access only to the object's owner (via 'owner' or 'user' field) or superusers.
    """
    message = _('You must be the owner of this object to perform this action.')

    def has_permission(self, request, view):
        # Essential: User must be authenticated to own anything.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # If user isn't authenticated, deny permission
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Superusers always have permission.
        if request.user.is_superuser:
            return True

        # Check for standard ownership fields. Add more ('creator', 'bidder') if needed.
        owner = None
        if hasattr(obj, 'owner'):
            owner = obj.owner
        elif hasattr(obj, 'user'):
            owner = obj.user
        elif hasattr(obj, 'bidder'): # Common for Bid models
             owner = obj.bidder
        
        # Grant permission if the user is the owner.
        # Ensure comparison is between user objects.
        return owner is not None and owner == request.user


class IsPropertyOwner(BasePermission):
    """
    Specific check: Allows access only if the user owns the Property object or is a superuser.
    Relies primarily on object-level check.
    """
    message = _('You must be the owner of this property to perform this action.')

    def has_permission(self, request, view):
        # User must be authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # If user isn't authenticated, deny permission
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Superusers always have permission.
        if request.user.is_superuser:
            return True

        # Check ownership specifically via the 'owner' attribute.
        # Ensure 'obj' is expected to be a Property instance with an 'owner'.
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsSelfOrStaff(BasePermission):
    """
    Specific check: Allows access if the object *is* the user OR the user is staff.
    Useful for UserProfile views where obj is a User instance.
    """
    message = _('You must be the relevant user or an admin (staff) to perform this action.')

    def has_permission(self, request, view):
        # User must be authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # If user isn't authenticated, deny permission
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Grant permission if the user is staff or if the object is the user themselves.
        return request.user.is_staff or obj == request.user

# --- Combined Permissions (for OR logic) ---

class IsAppraiserOrDataEntry(BasePermission):
    """Allows access only to appraisers, data entry users, or superusers."""
    message = _('You must be an appraiser or data entry specialist to perform this action.')

    def has_permission(self, request, view):
        # Check authentication first to avoid attribute errors
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Then check roles or superuser status
        return (
            request.user.role in ['appraiser', 'data_entry'] or 
            request.user.is_superuser
        )


class IsPropertyOwnerOrAppraiserOrDataEntry(BasePermission):
    """
    Allows access if the user owns the Property object, is an Appraiser, is Data Entry, or is a Superuser.
    Used for updating properties.
    """
    message = _('You must be the property owner, an appraiser, or a data entry specialist to modify this property.')

    def has_permission(self, request, view):
        # User must be authenticated.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # If user isn't authenticated, deny permission
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Grant access if superuser or has a relevant role.
        if request.user.is_superuser or request.user.role in ['appraiser', 'data_entry']:
            return True

        # Grant access if the user is the owner of the property object.
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsPropertyOwnerOrAppraiser(BasePermission):
    """
    Allows access if the user has the 'appraiser' role or has the 'owner' role.
    Used for creating Auctions.
    """
    message = _('You must be an appraiser or property owner to perform this action.')

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers and Appraisers can always attempt creation.
        if request.user.is_superuser or request.user.role == 'appraiser':
            return True

        # Allow users with the 'owner' role to attempt
        if request.user.role == 'owner':
            return True

        return False
        
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check for auction objects.
        Allows access if user is superuser, appraiser, or owns the related property.
        """
        # If user isn't authenticated, deny permission
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Superusers and appraisers always have permission
        if request.user.is_superuser or request.user.role == 'appraiser':
            return True
            
        # For property owners, check if they own the related property
        if hasattr(obj, 'related_property') and obj.related_property:
            return obj.related_property.owner == request.user
            
        return False