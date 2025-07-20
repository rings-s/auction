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
        ('owner', _('Property Owner')), ('appraiser', _('Property Appraiser')),
        ('data_entry', _('Data Entry Specialist')), ('tenant', _('Tenant')), ('user', _('User')),
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

    def has_role(self, role_name):
        return self.role == role_name or self.is_superuser

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
            'owner': 3,
            'appraiser': 4,
            'data_entry': 2,
            'tenant': 2,
            'user': 1,
        }
        base_priority = priority_map.get(self.role, 1)
        if self.is_superuser:
            base_priority = 5
        elif self.is_staff:
            base_priority += 1
        return base_priority

    def get_accessible_properties(self):
        """Get properties accessible based on user role"""
        if self.is_superuser or self.role in ['appraiser', 'data_entry']:
            return Property.objects.all()
        elif self.role == 'owner':
            return Property.objects.filter(owner=self)
        elif self.role == 'tenant':
            # Tenants can see properties they are renting (will be implemented with lease relationship)
            return Property.objects.filter(is_published=True)
        else:
            return Property.objects.filter(is_published=True)

    def get_accessible_auctions(self):
        """Get auctions accessible based on user role"""
        if self.is_superuser or self.role == 'appraiser':
            return Auction.objects.all()
        elif self.role == 'owner':
            return Auction.objects.filter(related_property__owner=self)
        elif self.role == 'tenant':
            # Tenants can see published auctions
            return Auction.objects.filter(is_published=True)
        else:
            return Auction.objects.filter(is_published=True)

    def get_accessible_bids(self):
        """Get bids accessible based on user role"""
        if self.is_superuser or self.role == 'appraiser':
            return Bid.objects.all()
        elif self.role == 'owner':
            return Bid.objects.filter(auction__related_property__owner=self)
        elif self.role == 'tenant':
            # Tenants can see their own bids
            return Bid.objects.filter(bidder=self)
        else:
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

    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def save(self, *args, **kwargs):
        # Process profile image if it's an image file
        if self.profile_image and not self.pk:
            try:
                img = Image.open(self.profile_image)
                
                # Resize image if too large
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    
                    # Save the processed image
                    output = BytesIO()
                    img_format = 'JPEG' if self.profile_image.name.lower().endswith('.jpg') else 'PNG'
                    img.save(output, format=img_format, quality=85)
                    output.seek(0)
                    
                    # Replace the file with optimized version
                    self.profile_image.save(
                        self.profile_image.name,
                        ContentFile(output.read()),
                        save=False
                    )
            except Exception as e:
                # Handle gracefully if not an image or processing fails
                pass
        
        super().save(*args, **kwargs)
    
    @property
    def profile_image_url(self):
        """Get profile image URL or fallback to user avatar"""
        if self.profile_image:
            return self.profile_image.url
        elif self.user.avatar:
            return self.user.avatar.url
        return None


# -------------------------------------------------------------------------
# Bank Account Model
# -------------------------------------------------------------------------

class BankAccount(models.Model):
    """Bank account information for users"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bank_accounts',
        verbose_name=_('المستخدم')
    )
    bank_account_name = models.CharField(max_length=200, verbose_name=_('اسم صاحب الحساب'))
    bank_name = models.CharField(max_length=200, verbose_name=_('اسم البنك'))
    iban_number = models.CharField(
        max_length=34, 
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$',
                message=_('رقم IBAN غير صحيح. يجب أن يبدأ برمز البلد ويتبع التنسيق الدولي')
            )
        ],
        verbose_name=_('رقم الآيبان')
    )
    account_number = models.CharField(max_length=50, blank=True, verbose_name=_('رقم الحساب'))
    swift_code = models.CharField(max_length=11, blank=True, verbose_name=_('رمز السويفت'))
    is_primary = models.BooleanField(default=False, verbose_name=_('الحساب الرئيسي'))
    is_verified = models.BooleanField(default=False, verbose_name=_('موثق'))
    notes = models.TextField(blank=True, verbose_name=_('ملاحظات'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('حساب بنكي')
        verbose_name_plural = _('الحسابات البنكية')
        indexes = [
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['iban_number']),
        ]
    
    def __str__(self):
        return f"{self.bank_account_name} - {self.bank_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary account per user
        if self.is_primary:
            BankAccount.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'bank_account_name': self.bank_account_name,
            'bank_name': self.bank_name,
            'iban_number': self.iban_number,
            'account_number': self.account_number,
            'swift_code': self.swift_code,
            'is_primary': self.is_primary,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# -------------------------------------------------------------------------
# Payment Model for Reports
# -------------------------------------------------------------------------

class Payment(models.Model):
    """Payment tracking model for reports (no payment gateway integration)"""
    
    PAYMENT_TYPE_CHOICES = [
        ('rent', _('إيجار')),
        ('property', _('عقارات')),
        ('deposit', _('تأمين')),
        ('maintenance', _('صيانة')),
        ('utility', _('مرافق')),
        ('fee', _('رسوم')),
        ('auction', _('مزاد')),
        ('other', _('أخرى')),

    ]
    
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('paid', _('مدفوع')),
        ('overdue', _('متأخر')),
        ('partial', _('مدفوع جزئياً')),
        ('cancelled', _('ملغي')),
    ]
    
    # Basic Information
    payment_id = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الدفعة'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('المستخدم')
    )
    
    # Payment Details
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('المبلغ'))
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_('العملة'))
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name=_('نوع الدفعة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    
    # References
    property_reference = models.ForeignKey(
        'base.Property',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('العقار المرتبط')
    )
    tenant_reference = models.ForeignKey(
        'base.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('المستأجر المرتبط')
    )
    
    # Dates
    payment_date = models.DateField(verbose_name=_('تاريخ الدفع'))
    due_date = models.DateField(null=True, blank=True, verbose_name=_('تاريخ الاستحقاق'))
    
    # Description and Notes
    description = models.TextField(verbose_name=_('الوصف'))
    notes = models.TextField(blank=True, verbose_name=_('ملاحظات'))
    
    # Bank Account Reference
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('الحساب البنكي')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('دفعة')
        verbose_name_plural = _('الدفعات')
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['property_reference']),
            models.Index(fields=['tenant_reference']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Auto-generate payment ID if not provided
        if not self.payment_id:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_num = random.randint(1000, 9999)
            self.payment_id = f"PAY-{timestamp}-{random_num}"
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.due_date and self.status in ['pending', 'partial']:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_type': self.payment_type,
            'payment_type_display': self.get_payment_type_display(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'description': self.description,
            'property_reference': {
                'id': self.property_reference.id,
                'title': self.property_reference.title,
            } if self.property_reference else None,
            'tenant_reference': {
                'id': self.tenant_reference.id,
                'full_name': self.tenant_reference.full_name,
            } if self.tenant_reference else None,
            'bank_account': self.bank_account.to_dict() if self.bank_account else None,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }