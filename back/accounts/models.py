import os, random, uuid
from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator
from base.models import Property, Auction, Bid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def user_avatar_path(instance, filename):
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    user_uuid = instance.uuid if instance.uuid else 'temp'
    return f'users/{user_uuid}/avatars/{timestamp}_{filename}'

def user_profile_image_path(instance, filename):
    """Generate path for user profile images"""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    user_uuid = instance.user.uuid if instance.user and instance.user.uuid else 'temp'
    return f'users/{user_uuid}/profile/{timestamp}_{filename}'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email is required'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_staff=True and is_superuser=True'))

        with transaction.atomic():
            return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        # Original roles
        ('owner', _('Property Owner')),
        ('appraiser', _('Property Appraiser')),
        ('data_entry', _('Data Entry Specialist')),
        ('tenant', _('Tenant')),
        ('user', _('User')),
        
        # New specialized roles
        ('administrator', _('System Administrator')),
        ('manager', _('Property Management Manager')),
        ('agent', _('Real Estate Agent')),
        ('auctioneer', _('Auction Specialist')),
        ('inspector', _('Property Inspector')),
        ('accountant', _('Financial Accountant')),
        ('maintenance_manager', _('Maintenance Manager')),
        ('legal_advisor', _('Legal Advisor')),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'), db_index=True)
    username = None
    email = models.EmailField(_('Email'), unique=True, db_index=True)
    first_name = models.CharField(_('First name'), max_length=150)
    last_name = models.CharField(_('Last name'), max_length=150)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be in format: '+999999999'. Max 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name=_('Phone number'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date of birth'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_created = models.DateTimeField(null=True, blank=True)
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_created = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True, verbose_name=_('Avatar'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name=_('User Role'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['email'], name='accounts_user_email_idx'),
            models.Index(fields=['uuid'], name='accounts_user_uuid_idx'),
            models.Index(fields=['role'], name='accounts_user_role_idx'),
            models.Index(fields=['is_active', 'is_verified'], name='accounts_user_status_idx'),
            models.Index(fields=['date_joined'], name='accounts_user_joined_idx'),
            models.Index(fields=['role', 'is_active'], name='accounts_user_role_active_idx'),
        ]

    def has_role(self, role_name):
        """Check if user has a specific role or is superuser"""
        return self.role == role_name or self.is_superuser
    
    def has_any_role(self, role_names):
        """Check if user has any of the specified roles"""
        if not isinstance(role_names, (list, tuple)):
            role_names = [role_names]
        return self.role in role_names or self.is_superuser
    
    def is_admin_level(self):
        """Check if user has administrative level access"""
        admin_roles = ['administrator', 'manager']
        return self.has_any_role(admin_roles)
    
    def is_property_professional(self):
        """Check if user is a property-related professional"""
        professional_roles = ['appraiser', 'agent', 'inspector', 'auctioneer']
        return self.has_any_role(professional_roles)
    
    def is_financial_role(self):
        """Check if user has financial/accounting access"""
        financial_roles = ['accountant', 'legal_advisor']
        return self.has_any_role(financial_roles)
    
    def can_manage_maintenance(self):
        """Check if user can manage maintenance operations"""
        maintenance_roles = ['maintenance_manager', 'manager', 'administrator']
        return self.has_any_role(maintenance_roles)
    
    def can_create_auctions(self):
        """Check if user can create auctions"""
        auction_roles = ['auctioneer', 'manager', 'administrator', 'owner']
        return self.has_any_role(auction_roles)
    
    def can_manage_properties(self):
        """Check if user can manage properties"""
        property_roles = ['owner', 'manager', 'administrator', 'agent']
        return self.has_any_role(property_roles)
    
    def get_role_display_color(self):
        """Get a color code for the user's role for UI purposes"""
        color_map = {
            'administrator': '#dc3545',  # red
            'manager': '#fd7e14',       # orange
            'auctioneer': '#6610f2',    # purple
            'appraiser': '#0d6efd',     # blue
            'legal_advisor': '#6f42c1', # indigo
            'agent': '#198754',         # green
            'owner': '#20c997',         # teal
            'inspector': '#0dcaf0',     # cyan
            'accountant': '#ffc107',    # yellow
            'maintenance_manager': '#6c757d',  # gray
            'data_entry': '#adb5bd',    # light gray
            'tenant': '#e9ecef',        # lighter gray
            'user': '#f8f9fa',          # lightest gray
        }
        return color_map.get(self.role, '#6c757d')

    def generate_verification_code(self, length=6):
        # Use cryptographically secure random for verification codes
        import secrets
        code = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
        self.verification_code = code
        self.verification_code_created = timezone.now()
        self.is_verified = False
        self.save(update_fields=['verification_code', 'verification_code_created', 'is_verified'])
        return code

    def verify_account(self, code):
        if not self.verification_code or not self.verification_code_created or self.verification_code != code:
            return False
        
        expiry_time = self.verification_code_created + timezone.timedelta(hours=24)
        if timezone.now() > expiry_time:
            return False

        self.is_verified = True
        self.verification_code = None
        self.verification_code_created = None
        self.save(update_fields=['is_verified', 'verification_code', 'verification_code_created'])
        return True

    def generate_reset_code(self, length=6):
        # Use cryptographically secure random for reset codes
        import secrets
        code = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
        self.reset_code = code
        self.reset_code_created = timezone.now()
        self.save(update_fields=['reset_code', 'reset_code_created'])
        return code

    def reset_password(self, code, new_password):
        if not self.reset_code or not self.reset_code_created or self.reset_code != code:
            return False
        
        expiry_time = self.reset_code_created + timezone.timedelta(hours=1)
        if timezone.now() > expiry_time:
            return False

        self.set_password(new_password)
        self.reset_code = None
        self.reset_code_created = None
        self.save(update_fields=['password', 'reset_code', 'reset_code_created'])
        return True

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
        if is_new:
            UserProfile.objects.get_or_create(user=self)



    #### ############################
    #### the Dashboard methods ######

    def get_dashboard_priority(self):
        """Get user dashboard priority based on role"""
        priority_map = {
            # High-level roles
            'administrator': 5,
            'manager': 4,
            'auctioneer': 4,
            'appraiser': 4,
            'legal_advisor': 4,
            
            # Mid-level roles
            'agent': 3,
            'owner': 3,
            'inspector': 3,
            'accountant': 3,
            'maintenance_manager': 3,
            
            # Basic roles
            'data_entry': 2,
            'tenant': 2,
            'user': 1,
        }
        base_priority = priority_map.get(self.role, 1)
        
        if self.is_superuser:
            base_priority = 6  # Highest priority
        elif self.is_staff:
            base_priority += 1
            
        return base_priority

    def get_accessible_properties(self):
        """Get properties accessible based on user role"""
        # Full access roles
        if self.is_superuser or self.role in ['administrator', 'manager', 'appraiser', 'data_entry']:
            return Property.objects.select_related('owner', 'location').prefetch_related('rooms')
        
        # Property ownership roles
        elif self.role in ['owner', 'agent']:
            if self.role == 'owner':
                return Property.objects.select_related('location').prefetch_related('rooms').filter(owner=self)
            else:  # agent
                # Agents can see properties they manage (could be extended with agent-property relationships)
                return Property.objects.select_related('owner', 'location').prefetch_related('rooms').filter(is_published=True)
        
        # Specialized access roles
        elif self.role in ['auctioneer', 'inspector', 'accountant', 'maintenance_manager', 'legal_advisor']:
            # These roles can see all published properties for their work
            return Property.objects.filter(is_published=True)
        
        # Basic access roles
        elif self.role == 'tenant':
            # Tenants can see properties they are renting (will be implemented with lease relationship)
            return Property.objects.filter(is_published=True)
        
        else:  # Default for 'user' and unknown roles
            return Property.objects.filter(is_published=True)

    def get_accessible_auctions(self):
        """Get auctions accessible based on user role"""
        # Full access roles
        if self.is_superuser or self.role in ['administrator', 'manager', 'auctioneer', 'appraiser']:
            return Auction.objects.select_related('related_property', 'related_property__location', 'related_property__owner')
        
        # Property-related roles
        elif self.role in ['owner', 'agent']:
            if self.role == 'owner':
                return Auction.objects.select_related('related_property', 'related_property__location').filter(related_property__owner=self)
            else:  # agent
                # Agents can see auctions for properties they manage
                return Auction.objects.select_related('related_property', 'related_property__location', 'related_property__owner').filter(is_published=True)
        
        # Specialized access roles
        elif self.role in ['inspector', 'accountant', 'legal_advisor']:
            # These roles can see all published auctions for their work
            return Auction.objects.filter(is_published=True)
        
        # Basic access roles
        else:  # tenant, user, data_entry, maintenance_manager, and unknown roles
            return Auction.objects.filter(is_published=True)

    def get_accessible_bids(self):
        """Get bids accessible based on user role"""
        # Full access roles
        if self.is_superuser or self.role in ['administrator', 'manager', 'auctioneer', 'appraiser']:
            return Bid.objects.select_related('auction', 'auction__related_property', 'bidder')
        
        # Property-related roles
        elif self.role in ['owner', 'agent']:
            if self.role == 'owner':
                return Bid.objects.select_related('auction', 'auction__related_property', 'bidder').filter(auction__related_property__owner=self)
            else:  # agent
                # Agents can see bids for auctions they manage (could be extended with agent relationships)
                return Bid.objects.select_related('auction', 'auction__related_property', 'bidder').filter(bidder=self)
        
        # Specialized access roles
        elif self.role in ['accountant', 'legal_advisor']:
            # These roles might need to see bid data for financial/legal purposes
            # For now, restrict to their own bids, but this could be expanded
            return Bid.objects.filter(bidder=self)
        
        # Basic access roles
        else:  # tenant, user, data_entry, inspector, maintenance_manager, and unknown roles
            return Bid.objects.filter(bidder=self)



class UserProfile(models.Model):
    IDENTITY_TYPE_CHOICES = [
        ('national_identity', _('الهوية الوطنية')),
        ('residency', _('الإقامة')),
        ('gulf_citizen', _('مواطن خليجي')),
        ('diplomatic_identity', _('الهوية الدبلوماسية')),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    
    # Identity Information
    identity_type = models.CharField(
        max_length=20, 
        choices=IDENTITY_TYPE_CHOICES, 
        default='national_identity',
        verbose_name=_('نوع الهوية')
    )
    identity_number = models.CharField(max_length=50, blank=True, verbose_name=_('رقم الهوية'))
    
    # Profile Image
    profile_image = models.ImageField(
        upload_to=user_profile_image_path, 
        null=True, 
        blank=True, 
        verbose_name=_('صورة الملف الشخصي')
    )
    
    # Personal Information
    bio = models.TextField(blank=True, verbose_name=_('نبذة شخصية'))
    company_name = models.CharField(max_length=200, blank=True, verbose_name=_('اسم الشركة'))
    company_registration = models.CharField(max_length=100, blank=True, unique=True, null=True, verbose_name=_('رقم تسجيل الشركة'))
    tax_id = models.CharField(max_length=50, blank=True, verbose_name=_('الرقم الضريبي'))
    
    # Address Information
    address = models.TextField(blank=True, verbose_name=_('العنوان'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('المدينة'))
    state = models.CharField(max_length=100, blank=True, verbose_name=_('المحافظة/الولاية'))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('الرمز البريدي'))
    country = models.CharField(max_length=100, blank=True, default='المملكة العربية السعودية', verbose_name=_('الدولة'))
    
    # Financial Information
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name=_('الحد الائتماني'))
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_('التقييم'))
    
    # Professional Information
    license_number = models.CharField(max_length=50, blank=True, verbose_name=_('رقم الترخيص'))
    license_expiry = models.DateField(null=True, blank=True, verbose_name=_('تاريخ انتهاء الترخيص'))
    
    # Preferences
    preferred_locations = models.TextField(blank=True, verbose_name=_('المواقع المفضلة'))
    property_preferences = models.TextField(blank=True, verbose_name=_('تفضيلات العقارات'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('ملف تعريف المستخدم')
        verbose_name_plural = _('ملفات تعريف المستخدمين')
        indexes = [
            models.Index(fields=['user'], name='accounts_profile_user_idx'),
            models.Index(fields=['identity_type'], name='accounts_profile_id_type_idx'),
            models.Index(fields=['company_registration'], name='accounts_profile_comp_reg_idx'),
            models.Index(fields=['created_at'], name='accounts_profile_created_idx'),
            models.Index(fields=['updated_at'], name='accounts_profile_updated_idx'),
            models.Index(fields=['city', 'state'], name='accounts_profile_location_idx'),
        ]

    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def save(self, *args, **kwargs):
        from base.utils import process_profile_image, validate_image_file, log_model_action
        
        # Process profile image if it's an image file
        if self.profile_image and not self.pk:
            try:
                # Validate image file first
                validate_image_file(self.profile_image)
                
                # Process image using shared utility
                processed_image = process_profile_image(self.profile_image)
                
                # Replace the file with optimized version
                self.profile_image.save(
                    self.profile_image.name,
                    processed_image,
                    save=False
                )
                
                log_model_action('UserProfile', 'profile_image_processed', user=self.user, object_id=self.pk)
                
            except Exception as e:
                # Handle gracefully if not an image or processing fails
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing profile image: {str(e)}")
        
        super().save(*args, **kwargs)
    
    @property
    def profile_image_url(self):
        """Get profile image URL or fallback to user avatar"""
        if self.profile_image:
            return self.profile_image.url
        elif self.user.avatar:
            return self.user.avatar.url
        return None


