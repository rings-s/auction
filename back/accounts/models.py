import os, random, uuid
from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator
from base.models import Property, Auction, Bid

def user_avatar_path(instance, filename):
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    user_uuid = instance.uuid if instance.uuid else 'temp'
    return f'users/{user_uuid}/avatars/{timestamp}_{filename}'

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
        ('data_entry', _('Data Entry Specialist')), ('user', _('User')),
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
        code = str(random.randint(10**(length-1), 10**length-1))
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
        code = str(random.randint(10**(length-1), 10**length-1))
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
        else:
            return Property.objects.filter(is_published=True)

    def get_accessible_auctions(self):
        """Get auctions accessible based on user role"""
        if self.is_superuser or self.role == 'appraiser':
            return Auction.objects.all()
        elif self.role == 'owner':
            return Auction.objects.filter(related_property__owner=self)
        else:
            return Auction.objects.filter(is_published=True)

    def get_accessible_bids(self):
        """Get bids accessible based on user role"""
        if self.is_superuser or self.role == 'appraiser':
            return Bid.objects.all()
        elif self.role == 'owner':
            return Bid.objects.filter(auction__related_property__owner=self)
        else:
            return Bid.objects.filter(bidder=self)



class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    bio = models.TextField(blank=True, verbose_name=_('نبذة شخصية'))
    company_name = models.CharField(max_length=200, blank=True, verbose_name=_('اسم الشركة'))
    company_registration = models.CharField(max_length=100, blank=True, unique=True, null=True, verbose_name=_('رقم تسجيل الشركة'))
    tax_id = models.CharField(max_length=50, blank=True, verbose_name=_('الرقم الضريبي'))
    address = models.TextField(blank=True, verbose_name=_('العنوان'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('المدينة'))
    state = models.CharField(max_length=100, blank=True, verbose_name=_('المحافظة/الولاية'))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('الرمز البريدي'))
    country = models.CharField(max_length=100, blank=True, verbose_name=_('الدولة'))
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name=_('الحد الائتماني'))
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_('التقييم'))
    license_number = models.CharField(max_length=50, blank=True, verbose_name=_('رقم الترخيص'))
    license_expiry = models.DateField(null=True, blank=True, verbose_name=_('تاريخ انتهاء الترخيص'))
    preferred_locations = models.TextField(blank=True, verbose_name=_('المواقع المفضلة'))
    property_preferences = models.TextField(blank=True, verbose_name=_('تفضيلات العقارات'))

    class Meta:
        verbose_name = _('ملف تعريف المستخدم')
        verbose_name_plural = _('ملفات تعريف المستخدمين')

    def __str__(self):
        return f"Profile for {self.user.email}"