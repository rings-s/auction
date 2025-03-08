from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.db import transaction
import random
from django.core.validators import RegexValidator, MinValueValidator

class Role(models.Model):
    """
    Defines auction platform user roles and associated permissions
    """
    ADMIN = 'admin'
    SELLER = 'seller'
    BUYER = 'buyer'
    INSPECTOR = 'inspector'
    LEGAL = 'legal'
    
    ROLE_CHOICES = [
        (ADMIN, _('Administrator')),
        (SELLER, _('Seller')),
        (BUYER, _('Buyer')),
        (INSPECTOR, _('Inspector')),
        (LEGAL, _('Legal Representative')),
    ]
    
    name = models.CharField(
        max_length=50, 
        choices=ROLE_CHOICES, 
        unique=True,
        help_text=_('Role name determines user permissions and access levels')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Detailed description of role responsibilities')
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        help_text=_('Specific permissions granted to this role'),
        related_name='auction_roles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.get_name_display()

    @property
    def default_permissions(self):
        """
        Define default permissions for each auction platform role
        """
        permissions_map = {
            self.ADMIN: {
                'can_manage_users': True,
                'can_manage_roles': True,
                'can_manage_auctions': True,
                'can_manage_contracts': True,
                'can_view_analytics': True,
                'can_manage_system': True,
            },
            self.SELLER: {
                'can_create_auctions': True,
                'can_manage_own_auctions': True,
                'can_view_own_analytics': True,
                'can_manage_own_contracts': True,
                'can_interact_with_buyers': True,
            },
            self.BUYER: {
                'can_view_auctions': True,
                'can_place_bids': True,
                'can_manage_own_contracts': True,
                'can_view_own_history': True,
                'can_interact_with_sellers': True,
            },
            self.INSPECTOR: {
                'can_inspect_items': True,
                'can_create_reports': True,
                'can_verify_documents': True,
                'can_update_item_status': True,
            },
            self.LEGAL: {
                'can_review_contracts': True,
                'can_manage_legal_documents': True,
                'can_verify_compliance': True,
                'can_handle_disputes': True,
            }
        }
        return permissions_map.get(self.name, {})


class UserProfile(models.Model):
    """
    Extended user profile for additional information
    (Role management now entirely through CustomUser.roles)
    """
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company_name = models.CharField(max_length=200, blank=True)
    company_registration = models.CharField(
        max_length=100, 
        blank=True, 
        unique=True,
        null=True
    )
    tax_id = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')



    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email is required'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)  # This triggers the CustomUser.save() method
        return user  # Removed UserProfile creation here

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        user = self.create_user(email, password, **extra_fields)
        
        # Add admin role to superuser
        admin_role, _ = Role.objects.get_or_create(name=Role.ADMIN)
        user.roles.add(admin_role)
        
        return user  # Removed UserProfile creation here


class CustomUser(AbstractUser):
    """
    Custom user model with email as the unique identifier
    and multi-role capabilities
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    verification_code_created = models.DateTimeField(null=True, blank=True)
    reset_code = models.CharField(max_length=6, blank=True)
    reset_code_created = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    roles = models.ManyToManyField(
        Role,
        verbose_name=_('roles'),
        blank=True,
        help_text=_('Roles assigned to this user'),
        related_name='users'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.roles.filter(name=role_name).exists()
    
    @property
    def role_names(self):
        """Get all of the user's role names"""
        return list(self.roles.values_list('name', flat=True))
    
    @property
    def primary_role(self):
        """
        Get the user's primary role using a priority system:
        Admin > Inspector > Legal > Seller > Buyer
        """
        # Role priority order (highest to lowest)
        role_priority = [Role.ADMIN, Role.INSPECTOR, Role.LEGAL, Role.SELLER, Role.BUYER]
        
        # Check for each role in order of priority
        for role_name in role_priority:
            if self.has_role(role_name):
                return role_name
                
        return None
    
    def has_auction_permission(self, permission_name):
        """
        Check if user has specific auction-related permission
        by checking all assigned roles
        """
        # Check each role the user has
        for role in self.roles.all():
            if role.default_permissions.get(permission_name, False):
                return True
        return False
    
    def add_role(self, role_name):
        """Add a role to the user by name"""
        if role_name not in [choice[0] for choice in Role.ROLE_CHOICES]:
            raise ValueError(f"Invalid role name: {role_name}")
            
        role, created = Role.objects.get_or_create(name=role_name)
        self.roles.add(role)
    
    def remove_role(self, role_name):
        """Remove a role from the user by name"""
        try:
            role = Role.objects.get(name=role_name)
            self.roles.remove(role)
        except Role.DoesNotExist:
            pass  # Role doesn't exist, nothing to remove
    
    def generate_verification_code(self):
        """Generate a random 6-digit verification code"""
        code = str(random.randint(100000, 999999))
        self.verification_code = code
        self.verification_code_created = timezone.now()
        self.save(update_fields=['verification_code', 'verification_code_created'])
        return code
        
    def generate_reset_code(self):
        """Generate a random 6-digit password reset code"""
        code = str(random.randint(100000, 999999))
        self.reset_code = code
        self.reset_code_created = timezone.now()
        self.save(update_fields=['reset_code', 'reset_code_created'])
        return code
    
    def verify_account(self, code):
        """Verify user account with the provided code"""
        # Check if code is valid and not expired (valid for 24 hours)
        if (self.verification_code and 
            self.verification_code == code and
            self.verification_code_created and
            timezone.now() < self.verification_code_created + timezone.timedelta(hours=24)):
            
            self.is_verified = True
            self.verification_code = ''
            self.save(update_fields=['is_verified', 'verification_code'])
            return True
        return False
    
    def reset_password(self, code, new_password):
        """Reset user password with the provided code"""
        # Check if code is valid and not expired (valid for 1 hour)
        if (self.reset_code and 
            self.reset_code == code and
            self.reset_code_created and
            timezone.now() < self.reset_code_created + timezone.timedelta(hours=1)):
            
            self.set_password(new_password)
            self.reset_code = ''
            self.save(update_fields=['password', 'reset_code'])
            return True
        return False
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        """Override save to create user profile if it doesn't exist"""
        creating = self._state.adding
        super().save(*args, **kwargs)
        
        if creating:
            UserProfile.objects.get_or_create(user=self)