from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from .models import *
from .utils import log_permission_denied

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


# -------------------------------------------------------------------------
# Enhanced Role-Based Permission System
# -------------------------------------------------------------------------

class RoleBasedPermission(BasePermission):
    """Base class for role-based permissions with enhanced logging and error handling"""
    
    required_roles = []
    allow_superuser = True
    require_verification = True
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if self.require_verification and not getattr(request.user, 'is_verified', False):
            return False
            
        if self.allow_superuser and request.user.is_superuser:
            return True
            
        if hasattr(request.user, 'has_any_role'):
            has_permission = request.user.has_any_role(self.required_roles)
            if not has_permission:
                log_permission_denied(request.user, self.__class__.__name__, request.method)
            return has_permission
            
        return False

class IsAdministrator(RoleBasedPermission):
    """Permission for system administrators only"""
    message = _('Administrator privileges required.')
    required_roles = ['administrator']

class IsManager(RoleBasedPermission):
    """Permission for managers and administrators"""
    message = _('Management privileges required.')
    required_roles = ['administrator', 'manager']

class IsPropertyProfessional(RoleBasedPermission):
    """Permission for property-related professionals"""
    message = _('Property professional privileges required.')
    required_roles = ['appraiser', 'agent', 'inspector', 'auctioneer', 'administrator', 'manager']

class IsFinancialRole(RoleBasedPermission):
    """Permission for financial/accounting roles"""
    message = _('Financial access privileges required.')
    required_roles = ['accountant', 'legal_advisor', 'administrator', 'manager']

class CanCreateAuctions(RoleBasedPermission):
    """Permission for users who can create auctions"""
    message = _('Auction creation privileges required.')
    required_roles = ['auctioneer', 'manager', 'administrator', 'owner']

class CanManageProperties(RoleBasedPermission):
    """Permission for users who can manage properties"""
    message = _('Property management privileges required.')
    required_roles = ['owner', 'manager', 'administrator', 'agent']

class CanManageMaintenance(RoleBasedPermission):
    """Permission for maintenance management"""
    message = _('Maintenance management privileges required.')
    required_roles = ['maintenance_manager', 'manager', 'administrator']

class CanAccessFinancialData(RoleBasedPermission):
    """Permission for financial data access"""
    message = _('Financial data access privileges required.')
    required_roles = ['accountant', 'legal_advisor', 'manager', 'administrator']

class CanInspectProperties(RoleBasedPermission):
    """Permission for property inspection"""
    message = _('Property inspection privileges required.')
    required_roles = ['inspector', 'appraiser', 'manager', 'administrator']

class IsAuctioneer(RoleBasedPermission):
    """Permission for auctioneers"""
    message = _('Auctioneer privileges required.')
    required_roles = ['auctioneer', 'administrator']

class IsAgent(RoleBasedPermission):
    """Permission for real estate agents"""
    message = _('Real estate agent privileges required.')
    required_roles = ['agent', 'manager', 'administrator']

class IsInspector(RoleBasedPermission):
    """Permission for property inspectors"""
    message = _('Property inspector privileges required.')
    required_roles = ['inspector', 'administrator']

class IsLegalAdvisor(RoleBasedPermission):
    """Permission for legal advisors"""
    message = _('Legal advisor privileges required.')
    required_roles = ['legal_advisor', 'administrator']

class CanManageWorkers(RoleBasedPermission):
    """Permission for managing workers and work assignments"""
    message = _('Worker management privileges required.')
    required_roles = ['maintenance_manager', 'manager', 'administrator', 'owner']

class CanAccessPropertyAnalytics(RoleBasedPermission):
    """Permission for accessing property analytics and detailed insights"""
    message = _('Property analytics access privileges required.')
    required_roles = ['appraiser', 'manager', 'administrator', 'owner', 'agent']

# -------------------------------------------------------------------------
# Enhanced Object-Level Permissions
# -------------------------------------------------------------------------

class EnhancedObjectOwner(BasePermission):
    """Enhanced object ownership permission with role-based overrides"""
    
    message = _('You must be the owner of this object or have appropriate role privileges.')
    override_roles = ['administrator', 'manager']
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Check for role-based overrides
        if hasattr(request.user, 'has_any_role') and request.user.has_any_role(self.override_roles):
            return True
            
        # Check ownership
        owner = getattr(obj, 'owner', None) or getattr(obj, 'user', None) or getattr(obj, 'bidder', None)
        return owner is not None and owner == request.user

class EnhancedPropertyPermission(BasePermission):
    """Enhanced property permission with role-based access"""
    
    message = _('Insufficient privileges to access this property.')
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Safe methods (GET, HEAD, OPTIONS) - check read access
        if request.method in SAFE_METHODS:
            if hasattr(request.user, 'get_accessible_properties'):
                return obj in request.user.get_accessible_properties()
        
        # Write operations - require ownership or privileged role
        if hasattr(request.user, 'can_manage_properties') and request.user.can_manage_properties():
            return True
            
        # Check direct ownership
        return hasattr(obj, 'owner') and obj.owner == request.user

class EnhancedAuctionPermission(BasePermission):
    """Enhanced auction permission with role-based access"""
    
    message = _('Insufficient privileges to access this auction.')
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Safe methods - check read access
        if request.method in SAFE_METHODS:
            if hasattr(request.user, 'get_accessible_auctions'):
                return obj in request.user.get_accessible_auctions()
        
        # Write operations - require creation privileges
        if hasattr(request.user, 'can_create_auctions') and request.user.can_create_auctions():
            return True
            
        return False

class EnhancedMaintenancePermission(BasePermission):
    """Enhanced maintenance permission with role-based access"""
    
    message = _('Insufficient privileges to manage maintenance requests.')
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Check maintenance management privileges
        if hasattr(request.user, 'can_manage_maintenance') and request.user.can_manage_maintenance():
            return True
            
        # Property owners can manage maintenance for their properties
        if hasattr(obj, 'property') and hasattr(obj.property, 'owner'):
            return obj.property.owner == request.user
            
        return False

# -------------------------------------------------------------------------
# Dynamic Permission System
# -------------------------------------------------------------------------

class DynamicRolePermission(BasePermission):
    """Dynamic permission that checks roles at runtime"""
    
    def __init__(self, required_roles=None, message=None, allow_owner=False):
        self.required_roles = required_roles or []
        self.custom_message = message
        self.allow_owner = allow_owner
        
    @property
    def message(self):
        return self.custom_message or _('Insufficient role privileges.')
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        if hasattr(request.user, 'has_any_role'):
            return request.user.has_any_role(self.required_roles)
            
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        if hasattr(request.user, 'has_any_role') and request.user.has_any_role(self.required_roles):
            return True
            
        if self.allow_owner:
            owner = getattr(obj, 'owner', None) or getattr(obj, 'user', None)
            return owner is not None and owner == request.user
            
        return False

# -------------------------------------------------------------------------
# Permission Factories
# -------------------------------------------------------------------------

def create_role_permission(roles, message=None, allow_owner=False):
    """Factory function to create dynamic role-based permissions"""
    class CustomRolePermission(DynamicRolePermission):
        def __init__(self):
            super().__init__(required_roles=roles, message=message, allow_owner=allow_owner)
    
    return CustomRolePermission

def create_combined_permission(*permission_classes):
    """Factory to combine multiple permission classes with AND logic"""
    class CombinedPermission(BasePermission):
        def has_permission(self, request, view):
            return all(perm().has_permission(request, view) for perm in permission_classes)
        
        def has_object_permission(self, request, view, obj):
            return all(perm().has_object_permission(request, view, obj) for perm in permission_classes)
    
    return CombinedPermission

