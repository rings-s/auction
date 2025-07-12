# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

class IsPropertyManagerOrOwner(BasePermission):
    """Permission for property managers and owners"""
    message = _('You must be a property manager or owner to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['landlord', 'property_manager', 'owner'] or 
                request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Check if user owns the property or related property
        if hasattr(obj, 'related_property'):
            return (obj.related_property.owner == request.user or 
                   getattr(obj.related_property.rental_details, 'property_manager', None) == request.user)
        elif hasattr(obj, 'base_property'):
            return (obj.base_property.owner == request.user or 
                   getattr(obj.base_property.rental_details, 'property_manager', None) == request.user)
        elif hasattr(obj, 'property'):
            return (obj.property.owner == request.user or 
                   getattr(obj.property.rental_details, 'property_manager', None) == request.user)
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False

class IsLandlordOrPropertyManager(BasePermission):
    """Permission for landlords and property managers"""
    message = _('You must be a landlord or property manager to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['landlord', 'property_manager'] or 
                request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Check for rental property ownership/management
        if hasattr(obj, 'base_property'):
            return (obj.base_property.owner == request.user or 
                   getattr(obj, 'property_manager', None) == request.user)
        elif hasattr(obj, 'rental_property'):
            return (obj.rental_property.base_property.owner == request.user or 
                   obj.rental_property.property_manager == request.user)
        
        return False

class IsTenantOrLandlord(BasePermission):
    """Permission for tenants and landlords"""
    message = _('You must be a tenant or landlord to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['tenant', 'landlord', 'property_manager'] or 
                request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # For lease objects
        if hasattr(obj, 'tenant') and hasattr(obj, 'landlord'):
            return obj.tenant == request.user or obj.landlord == request.user
        
        # For financial transactions related to leases
        if hasattr(obj, 'payer') and hasattr(obj, 'payee'):
            return obj.payer == request.user or obj.payee == request.user
        
        return False

class IsMaintenanceStaffOrManager(BasePermission):
    """Permission for maintenance staff and managers"""
    message = _('You must be maintenance staff or a property manager to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['maintenance_staff', 'vendor', 'property_manager', 'landlord'] or 
                request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # For maintenance requests
        if hasattr(obj, 'assigned_to') and hasattr(obj, 'requested_by'):
            return (obj.assigned_to == request.user or 
                   obj.requested_by == request.user or
                   (hasattr(obj, 'related_property') and obj.related_property.owner == request.user))
        
        return False

class IsVendorOrManager(BasePermission):
    """Permission for vendors and managers"""
    message = _('You must be a vendor or property manager to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['vendor', 'maintenance_staff', 'property_manager', 'landlord'] or 
                request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # For vendor objects - vendors can manage their own profiles
        if hasattr(obj, 'contact_person'):
            # Allow if user is property manager/landlord or if it's their vendor profile
            return (request.user.role in ['property_manager', 'landlord'] or
                   obj.contact_person == request.user.email)
        
        return False

class CanManageContracts(BasePermission):
    """Permission for contract management"""
    message = _('You must have contract management permissions to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['landlord', 'property_manager', 'tenant'] or 
                request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # For contract objects
        if hasattr(obj, 'primary_party') and hasattr(obj, 'secondary_party'):
            return (obj.primary_party == request.user or 
                   obj.secondary_party == request.user)
        
        return False

class CanAccessFinancials(BasePermission):
    """Permission for financial data access"""
    message = _('You must have financial access permissions to perform this action.')

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.role in ['landlord', 'property_manager', 'tenant'] or 
                request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # For financial transactions
        if hasattr(obj, 'payer') and hasattr(obj, 'payee'):
            return (obj.payer == request.user or 
                   obj.payee == request.user or
                   (hasattr(obj, 'related_property') and obj.related_property.owner == request.user))
        
        return False