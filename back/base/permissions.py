# back/base/permissions.py (Fixed version)

from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from .models import Property, Auction, Media

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

class IsMediaManager(BasePermission):
    message = _('You do not have permission to manage this media.')

    def has_object_permission(self, request, view, obj): # obj is a Media instance
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Check 1: Is the user the owner of the media object itself (uploader)?
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        # Check 2: Is the media linked to a Property?
        # And does the user have owner/appraiser/data_entry rights for properties?
        try:
            property_content_type = ContentType.objects.get_for_model(Property)
            if obj.content_type == property_content_type:
                # If user has a role that grants broad access to property media
                if request.user.role in ['appraiser', 'data_entry']:
                    return True
                # If user is the owner of the specific property this media is linked to.
                property_instance = obj.content_object # This is the Property instance
                if property_instance and hasattr(property_instance, 'owner') and property_instance.owner == request.user:
                    return True
        except Exception: # Catch potential errors if ContentType or Property model changes
            pass

        # Check 3: Is the media linked to an Auction?
        # And does the user have owner/appraiser rights for auctions (via its property)?
        try:
            auction_content_type = ContentType.objects.get_for_model(Auction)
            if obj.content_type == auction_content_type:
                auction_instance = obj.content_object # This is the Auction instance
                if auction_instance and hasattr(auction_instance, 'property'):
                    property_of_auction = auction_instance.property
                    # If user has a role that grants broad access to auction media (e.g., appraiser)
                    if request.user.role == 'appraiser':
                        return True
                    # If user is the owner of the specific property this auction (and thus its media) is linked to.
                    if property_of_auction and hasattr(property_of_auction, 'owner') and property_of_auction.owner == request.user:
                        return True
        except Exception:
            pass
        
        return False

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
    Used for updating properties and related objects like rooms.
    """
    message = _('You must be the property owner, an appraiser, or a data entry specialist to modify this item.')

    def has_permission(self, request, view):
        # User must be authenticated for any action this permission guards.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Dynamically import Property model to avoid circular imports if models.py imports permissions
        from .models import Property

        # Authenticated check (already done by has_permission, but good for direct calls too)
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Grant access if superuser or has a relevant role (appraiser, data_entry).
        # These roles are considered to have broad access to properties they are involved with.
        if request.user.is_superuser or request.user.role in ['appraiser', 'data_entry']:
            return True

        # Determine the target Property instance
        target_property = None
        if isinstance(obj, Property):
            target_property = obj
        elif hasattr(obj, 'property') and isinstance(obj.property, Property):
            # This handles cases like Room, Auction, etc., that have a direct link to a Property
            target_property = obj.property
        
        # If we found a target property, check if the current user is its owner.
        if target_property:
            return hasattr(target_property, 'owner') and target_property.owner == request.user
        
        # Fallback: If the object isn't a Property and doesn't link to one as expected,
        # and the user isn't a superuser or designated role, deny permission.
        # This prevents accidental access if the permission is misapplied.
        return False


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