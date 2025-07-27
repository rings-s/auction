from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class SecurityMixin:
    """Mixin for enhanced security logging and monitoring."""
    
    def log_permission_denied(self, request, reason, obj=None):
        """Log permission denied events for security monitoring."""
        logger.warning(
            f"Permission denied: {reason}",
            extra={
                'user': getattr(request, 'user', None),
                'ip': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'path': request.path,
                'method': request.method,
                'reason': reason,
                'object_type': obj.__class__.__name__ if obj else None,
                'object_id': getattr(obj, 'id', None),
                'timestamp': timezone.now().isoformat(),
            }
        )
    
    def get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class IsOwnerOrAdmin(BasePermission, SecurityMixin):
    """Permission that allows access to object owners or administrators."""
    
    message = _('You must be the owner of this object or an admin.')

    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            self.log_permission_denied(request, 'unauthenticated_access', obj)
            return False
        
        # Allow superusers
        if request.user.is_superuser:
            return True
            
        # Allow object owners
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        elif obj == request.user:
            return True
            
        # Allow administrators
        if request.user.is_staff or getattr(request.user, 'role', '') in ['administrator', 'manager']:
            return True
        
        # Log denial
        self.log_permission_denied(request, 'not_owner_or_admin', obj)
        return False


class IsAdminUser(BasePermission, SecurityMixin):
    """Permission for administrative users only."""
    
    message = _('You must be an administrator to perform this action.')

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.log_permission_denied(request, 'unauthenticated_admin_access')
            return False
        
        # Allow superusers
        if request.user.is_superuser:
            return True
            
        # Allow staff members and administrators
        if request.user.is_staff or getattr(request.user, 'role', '') in ['administrator', 'manager']:
            return True
        
        self.log_permission_denied(request, 'insufficient_admin_privileges')
        return False


class IsVerifiedUser(BasePermission, SecurityMixin):
    """Permission that requires user to be verified."""
    
    message = _('Your account must be verified to perform this action.')

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.log_permission_denied(request, 'unauthenticated_verified_access')
            return False
        
        is_verified = getattr(request.user, 'is_verified', False)
        if not is_verified:
            self.log_permission_denied(request, 'unverified_account')
            return False
        
        return True


class IsActiveUser(BasePermission, SecurityMixin):
    """Permission that requires user to be active."""
    
    message = _('Your account has been disabled.')

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not request.user.is_active:
            self.log_permission_denied(request, 'inactive_account')
            return False
        
        return True


class RoleBasedPermission(BasePermission, SecurityMixin):
    """Base class for role-based permissions."""
    
    required_roles = []
    message = _('You do not have the required role to perform this action.')

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.log_permission_denied(request, 'unauthenticated_role_access')
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        user_role = getattr(request.user, 'role', '')
        
        # Check if user has required role
        if user_role in self.required_roles:
            return True
        
        # Check role-based methods if available
        for role in self.required_roles:
            method_name = f'has_role'
            if hasattr(request.user, method_name) and request.user.has_role(role):
                return True
        
        self.log_permission_denied(
            request, 
            f'insufficient_role_privileges_required_{self.required_roles}'
        )
        return False


class IsPropertyManager(RoleBasedPermission):
    """Permission for property managers and administrators."""
    required_roles = ['manager', 'administrator', 'owner']
    message = _('You must be a property manager to perform this action.')


class IsAuctioneer(RoleBasedPermission):
    """Permission for auctioneers and administrators."""
    required_roles = ['auctioneer', 'administrator', 'manager']
    message = _('You must be an auctioneer to perform this action.')


class IsPropertyProfessional(RoleBasedPermission):
    """Permission for property professionals."""
    required_roles = ['appraiser', 'agent', 'inspector', 'auctioneer', 'administrator', 'manager']
    message = _('You must be a property professional to perform this action.')


class IsFinancialRole(RoleBasedPermission):
    """Permission for financial roles."""
    required_roles = ['accountant', 'legal_advisor', 'administrator', 'manager']
    message = _('You must have financial access rights to perform this action.')


class RateLimitedPermission(BasePermission, SecurityMixin):
    """Permission with built-in rate limiting."""
    
    rate_limit = 100  # requests per hour
    cache_key_prefix = 'rate_limit'
    message = _('Rate limit exceeded. Please try again later.')

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Generate cache key
        client_ip = self.get_client_ip(request)
        cache_key = f"{self.cache_key_prefix}_{request.user.id}_{client_ip}"
        
        # Get current request count
        current_requests = cache.get(cache_key, 0)
        
        # Check rate limit
        if current_requests >= self.rate_limit:
            self.log_permission_denied(
                request, 
                f'rate_limit_exceeded_{current_requests}_{self.rate_limit}'
            )
            return False
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 3600)  # 1 hour TTL
        
        return True


class IPWhitelistPermission(BasePermission, SecurityMixin):
    """Permission that checks IP whitelist for sensitive operations."""
    
    allowed_ips = []  # Configure in settings
    message = _('Access denied from this IP address.')

    def has_permission(self, request, view):
        if not self.allowed_ips:  # If no whitelist configured, allow all
            return True
        
        client_ip = self.get_client_ip(request)
        
        if client_ip not in self.allowed_ips:
            self.log_permission_denied(request, f'ip_not_whitelisted_{client_ip}')
            return False
        
        return True


class EnhancedObjectOwnership(BasePermission, SecurityMixin):
    """Enhanced object ownership with role-based access."""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            self.log_permission_denied(request, 'unauthenticated_object_access', obj)
            return False
        
        # Superusers can access everything
        if request.user.is_superuser:
            return True
        
        # Object ownership patterns
        ownership_fields = ['user', 'owner', 'created_by', 'author']
        
        for field in ownership_fields:
            if hasattr(obj, field):
                owner = getattr(obj, field)
                if owner == request.user:
                    return True
        
        # Role-based access for specific object types
        user_role = getattr(request.user, 'role', '')
        
        # Administrators and managers can access most objects
        if user_role in ['administrator', 'manager']:
            return True
        
        # Specific role permissions based on object type
        obj_type = obj.__class__.__name__.lower()
        
        role_permissions = {
            'property': ['owner', 'agent', 'appraiser', 'inspector'],
            'auction': ['auctioneer', 'appraiser', 'owner'],
            'bid': ['auctioneer', 'owner'],  # Owner of the property being auctioned
            'maintenance': ['maintenance_manager', 'owner'],
            'expense': ['accountant', 'owner'],
            'payment': ['accountant', 'owner'],
            'worker': ['maintenance_manager', 'owner'],
        }
        
        allowed_roles = role_permissions.get(obj_type, [])
        if user_role in allowed_roles:
            return True
        
        self.log_permission_denied(request, f'insufficient_object_permissions_{obj_type}', obj)
        return False