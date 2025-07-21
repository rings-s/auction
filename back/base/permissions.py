from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from .models import *

class IsVerifiedUser(BasePermission):
    message = _('User account must be verified.')
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                hasattr(request.user, 'is_verified') and request.user.is_verified)

class IsAdminUser(BasePermission):
    message = _('You must be an administrator to perform this action.')

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsAppraiser(BasePermission):
    message = _('You must be an appraiser to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role == 'appraiser' or request.user.is_superuser))

class IsDataEntry(BasePermission):
    message = _('You must be a data entry specialist to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role == 'data_entry' or request.user.is_superuser))

class IsObjectOwner(BasePermission):
    message = _('You must be the owner of this object to perform this action.')

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        owner = getattr(obj, 'owner', None) or getattr(obj, 'user', None) or getattr(obj, 'bidder', None)
        return owner is not None and owner == request.user

class IsPropertyOwner(BasePermission):
    message = _('You must be the owner of this property to perform this action.')

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(obj, 'owner') and obj.owner == request.user

class IsMediaManager(BasePermission):
    message = _('You do not have permission to manage this media.')

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        try:
            property_content_type = ContentType.objects.get_for_model(Property)
            if obj.content_type == property_content_type:
                if request.user.role in ['appraiser', 'data_entry']:
                    return True
                property_instance = obj.content_object
                if property_instance and hasattr(property_instance, 'owner') and property_instance.owner == request.user:
                    return True
        except Exception:
            pass

        return False

class IsAppraiserOrDataEntry(BasePermission):
    message = _('You must be an appraiser or data entry specialist to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['appraiser', 'data_entry'] or request.user.is_superuser))

class IsPropertyOwnerOrAppraiserOrDataEntry(BasePermission):
    message = _('You must be the property owner, appraiser, or data entry specialist to modify this item.')

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.role in ['appraiser', 'data_entry']:
            return True

        target_property = None
        if isinstance(obj, Property):
            target_property = obj
        elif hasattr(obj, 'property') and isinstance(obj.property, Property):
            target_property = obj.property
        
        if target_property:
            return hasattr(target_property, 'owner') and target_property.owner == request.user
        return False

class IsPropertyOwnerOrAppraiser(BasePermission):
    message = _('You must be an appraiser or property owner to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_superuser or request.user.role in ['appraiser', 'owner']))

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.role == 'appraiser':
            return True
        if hasattr(obj, 'related_property') and obj.related_property:
            return obj.related_property.owner == request.user
        return False

class IsMessageParticipant(BasePermission):
    message = _('You must be a participant in this message thread.')

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_staff:
            return True
        return obj.sender == request.user or obj.recipient == request.user

class CanSendMessages(BasePermission):
    message = _('You must have a verified account to send messages.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                getattr(request.user, 'is_verified', False) and request.user.is_active)



# these new permission classes is four the dashboard 

class CanAccessDashboard(BasePermission):
    message = _('You need appropriate permissions to access dashboard features.')
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                getattr(request.user, 'is_verified', False))

class CanAccessAdvancedDashboard(BasePermission):
    message = _('Advanced dashboard features require elevated permissions.')
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role in ['appraiser', 'data_entry'] or 
                request.user.is_staff or request.user.is_superuser)

class CanAccessAdminDashboard(BasePermission):
    message = _('Admin dashboard access requires administrator privileges.')
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_staff or request.user.is_superuser))

class CanManageAuctions(BasePermission):
    message = _('You need appraiser or owner permissions to manage auctions.')
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role in ['appraiser', 'owner'] or 
                request.user.is_superuser)



# back/base/permissions.py - Enhanced Property-Based Permissions

class IsPropertyOwnerOrManager(BasePermission):
    """Check if user owns or manages the property"""
    message = _('You must be the property owner or assigned manager.')
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Get the property from different model types
        property_obj = self._get_property_from_object(obj)
        if not property_obj:
            return False
            
        # Check ownership
        if property_obj.owner == request.user:
            return True
            
        # Check management assignment
        if property_obj.property_manager == request.user:
            return True
            
        # Check company management
        if (property_obj.management_company and 
            property_obj.management_company.contact_person == request.user):
            return True
            
        return False
    
    def _get_property_from_object(self, obj):
        """Extract property object from various model types"""
        if isinstance(obj, Property):
            return obj
        elif hasattr(obj, 'property'):
            return obj.property
        elif hasattr(obj, 'base_property'):
            return obj.base_property
        elif hasattr(obj, 'related_property'):
            return obj.related_property
        elif hasattr(obj, 'rental_property'):
            return obj.rental_property.base_property
        return None

class CanManageWorkers(BasePermission):
    """Permission to manage workers for properties"""
    message = _('You need property management permissions to manage workers.')
    
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_superuser or 
                 request.user.role in ['appraiser', 'data_entry', 'owner'] or
                 request.user.managed_properties.exists() or
                 request.user.managed_companies.exists()))

class CanAccessPropertyAnalytics(BasePermission):
    """Permission to access property analytics"""
    message = _('You need appropriate permissions to access property analytics.')
    
    def has_permission(self, request, view):
        user = request.user
        return (user and user.is_authenticated and 
                (user.is_superuser or 
                 user.role in ['appraiser', 'data_entry'] or
                 user.owned_properties.exists() or
                 user.managed_properties.exists()))