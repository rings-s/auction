from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
import uuid
import os
import random
import logging
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta

# Get an instance of a logger
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Base Model
# -------------------------------------------------------------------------
class BaseModel(models.Model):
    """Abstract base model with common fields"""
    is_deleted = models.BooleanField(_('محذوف'), default=False)
    deleted_at = models.DateTimeField(_('تاريخ الحذف'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark record as deleted instead of physically deleting it"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

# -------------------------------------------------------------------------
# Media Model
# -------------------------------------------------------------------------
class Media(BaseModel):
    """Simplified media model for images and files"""
    MEDIA_TYPES = [
        ('image', _('صورة')),
        ('document', _('مستند')),
        ('video', _('فيديو')),
        ('other', _('أخرى')),
    ]

    file = models.FileField(_('الملف'), upload_to='uploads/%Y/%m/%d/')
    name = models.CharField(_('الاسم'), max_length=255, blank=True)
    media_type = models.CharField(_('نوع الوسائط'), max_length=10, choices=MEDIA_TYPES, default='image')
    is_primary = models.BooleanField(_('صورة رئيسية'), default=False)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    
    # ContentType relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('وسائط')
        verbose_name_plural = _('وسائط')
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)
        
        # Process image if it's an image file
        if self.media_type == 'image' and self.file and not self.pk:
            try:
                img = Image.open(self.file)
                
                # Create thumbnail if needed
                if img.height > 1200 or img.width > 1200:
                    output_size = (1200, 1200)
                    img.thumbnail(output_size)
                    
                    # Save the processed image
                    output = BytesIO()
                    img_format = 'JPEG' if self.file.name.lower().endswith('.jpg') else 'PNG'
                    img.save(output, format=img_format, quality=85)
                    output.seek(0)
                    
                    # Replace the file with optimized version
                    self.file.save(
                        self.file.name,
                        ContentFile(output.read()),
                        save=False
                    )
            except Exception as e:
                # Handle gracefully if not an image or processing fails
                pass
        # For document files, ensure we don't try to process them as images
        elif self.media_type == 'document' and self.file and not self.pk:
            # Log the document file but don't try to process it
            pass
                
        super().save(*args, **kwargs)
                    

    def get_dimensions(self):
        """Get image dimensions if media is an image"""
        if self.media_type != 'image':
            return None
            
        try:
            with self.file.open() as f:
                img = Image.open(f)
                return {'width': img.width, 'height': img.height}
        except Exception:
            return None

    @property
    def file_size(self):
        """Get file size on demand"""
        if self.file:
            return self.file.size
        return 0

    def to_dict(self):
        """Return a dictionary representation for API responses"""
        dimensions = self.get_dimensions() if self.media_type == 'image' else None
        
        return {
            'id': self.id,
            'url': self.file.url if self.file else None,
            'name': self.name,
            'type': self.media_type,
            'size': self.file_size,
            'dimensions': dimensions,
            'is_primary': self.is_primary,
        }

# -------------------------------------------------------------------------
# Location Model
# -------------------------------------------------------------------------
class Location(BaseModel):
    """Location model"""
    city = models.CharField(_('المدينة'), max_length=100)
    state = models.CharField(_('المنطقة/المحافظة'), max_length=100)
    country = models.CharField(_('الدولة'), max_length=100, default='المملكة العربية السعودية')
    postal_code = models.CharField(_('الرمز البريدي'), max_length=20, blank=True)
    latitude = models.DecimalField(_('خط العرض'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('خط الطول'), max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = _('موقع')
        verbose_name_plural = _('المواقع')
        unique_together = ['city', 'state', 'country', 'postal_code']
        indexes = [
            models.Index(fields=['city', 'state']),
        ]
        
    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"

    @property
    def coordinates(self):
        """Return coordinates as tuple if both lat and long are present"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None

# -------------------------------------------------------------------------
# Property Model
# -------------------------------------------------------------------------
class Property(BaseModel):
    """Property model with integrated types as choices"""
    # Property Type choices integrated
    PROPERTY_TYPES = [
        ('residential', _('سكني')),
        ('commercial', _('تجاري')),
        ('industrial', _('صناعي')),
        ('land', _('أرض')),
        ('agricultural', _('زراعي')),
        ('mixed_use', _('متعدد الاستخدامات')),
    ]
    
    # Building Type choices integrated
    BUILDING_TYPES = [
        ('apartment', _('شقة')),
        ('villa', _('فيلا')),
        ('house', _('منزل')),
        ('office', _('مكتب')),
        ('retail', _('محل تجاري')),
        ('warehouse', _('مستودع')),
        ('other', _('أخرى')),
    ]
    
    STATUS_CHOICES = [
        ('available', _('متاح')),
        ('under_contract', _('تحت العقد')),
        ('sold', _('مباع')),
        ('auction', _('في المزاد')),
    ]

    # Basic Information
    property_number = models.CharField(_('رقم العقار'), max_length=50, unique=True, blank=True)
    title = models.CharField(_('العنوان'), max_length=255)
    slug = models.SlugField(_('الرابط المختصر'), max_length=255, unique=True, blank=True, allow_unicode=True)
    property_type = models.CharField(_('نوع العقار'), max_length=20, choices=PROPERTY_TYPES)
    building_type = models.CharField(_('نوع المبنى'), max_length=20, choices=BUILDING_TYPES, null=True, blank=True)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='available')

    # Deed Information
    deed_number = models.CharField(_('رقم الصك'), max_length=100, unique=True, help_text=_('رقم صك الملكية الرسمي للعقار'))

    # Property Details
    description = models.TextField(_('الوصف'))
    meta_description = models.TextField(_('وصف ميتا'), blank=True)
    search_keywords = models.TextField(_('كلمات البحث'), blank=True)
    size_sqm = models.DecimalField(_('المساحة (متر مربع)'), max_digits=10, decimal_places=2)
    floors = models.PositiveSmallIntegerField(_('عدد الطوابق'), null=True, blank=True)
    year_built = models.PositiveIntegerField(_('سنة البناء'), null=True, blank=True)

    # Location
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name=_('الموقع'), related_name='properties')
    address = models.CharField(_('العنوان التفصيلي'), max_length=255)

    # Financial Information
    market_value = models.DecimalField(_('القيمة السوقية'), max_digits=14, decimal_places=2)
    minimum_bid = models.DecimalField(_('الحد الأدنى للمزايدة'), max_digits=14, decimal_places=2, null=True, blank=True)

    # Features and Amenities
    features = models.JSONField(_('المميزات'), default=list, blank=True)
    amenities = models.JSONField(_('المرافق'), default=list, blank=True)

    # Ownership and Visibility
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='owned_properties', null=True, verbose_name=_('المالك'))
    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)
    is_verified = models.BooleanField(_('موثق'), default=False)
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    availability_date = models.DateField(_('تاريخ التوفر'), null=True, blank=True)

    # Relations - Media field is correctly defined here
    media = GenericRelation(Media, related_query_name='property')

    class Meta:
        verbose_name = _('عقار')
        verbose_name_plural = _('العقارات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_number']),
            models.Index(fields=['deed_number']),
            models.Index(fields=['status']),
            models.Index(fields=['market_value']),
            models.Index(fields=['property_type']),
        ]

    def __str__(self):
        return self.title

    def get_cache_key(self):
        """Generate unique cache key for this property"""
        return f'property_{self.id}'

    def save(self, *args, **kwargs):
        # Auto-generate property number if not provided
        if not self.property_number:
            prefix = self.property_type[:3].upper()
            random_num = random.randint(10000, 99999)
            self.property_number = f"{prefix}-{random_num}"

        # Create slug if not provided
        if not self.slug:
            self.slug = self._generate_unique_slug()
        
        super().save(*args, **kwargs)
        cache.delete(self.get_cache_key())

    def _generate_unique_slug(self):
        """Generate a unique slug for the property"""
        # Handle Arabic text by using a custom approach if needed
        # First try standard slugify
        original_slug = slugify(self.title, allow_unicode=True)
        
        # If slugify produced an empty string (which can happen with only Arabic characters)
        # create a slug from the property number or a random string
        if not original_slug:
            if self.property_number:
                original_slug = f"property-{self.property_number}"
            else:
                # Generate a random string if no property number
                random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
                original_slug = f"property-{random_str}"
        
        unique_slug = original_slug
        counter = 1
        
        while Property.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f"{original_slug}-{counter}"
            counter += 1
        
        return unique_slug

    def get_main_image(self):
        """Get the primary image or first image"""
        primary_image = self.media.filter(media_type='image', is_primary=True, is_deleted=False).first()
        if primary_image:
            return primary_image
        return self.media.filter(media_type='image', is_deleted=False).first()

    def get_all_images(self):
        """Get all images for this property ordered by primary status and order"""
        return self.media.filter(
            media_type='image', 
            is_deleted=False
        ).order_by('-is_primary', 'order', '-created_at')

    def get_all_documents(self):
        """Get all documents for this property"""
        return self.media.filter(
            media_type='document',
            is_deleted=False
        ).order_by('order', '-created_at')

    def add_media(self, file, media_type='image', is_primary=False, name=''):
        """Helper method to easily add media to a property"""
        content_type = ContentType.objects.get_for_model(self.__class__)
        media = Media(
            file=file,
            name=name or os.path.basename(file.name),
            media_type=media_type,
            is_primary=is_primary,
            content_type=content_type,
            object_id=self.id
        )
        media.save()
        return media

    def set_primary_image(self, media_id):
        """Set a specific image as primary, clearing other primary flags"""
        # First reset all media to non-primary
        self.media.filter(media_type='image').update(is_primary=False)
        # Then set the specified one as primary
        self.media.filter(id=media_id, media_type='image').update(is_primary=True)

    def increment_view_count(self):
        """Increment view count efficiently"""
        Property.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])
        return self.view_count

    def to_dict(self):
        """Return a dictionary representation for API responses"""
        main_image_data = None
        main_image_obj = self.get_main_image()
        if main_image_obj:
            main_image_data = main_image_obj.to_dict()

        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'property_number': self.property_number,
            'property_type': {
                'code': self.property_type,
                'name': self.get_property_type_display(),
            },
            'building_type': {
                'code': self.building_type,
                'name': self.get_building_type_display(),
            } if self.building_type else None,
            'status': self.status,
            'status_display': self.get_status_display(),
            'description': self.description,
            'size_sqm': float(self.size_sqm) if self.size_sqm is not None else None,
            'location': {
                'address': self.address,
                'city': self.location.city if self.location else None,
                'state': self.location.state if self.location else None,
                'country': self.location.country if self.location else None,
            } if self.location else None,
            'market_value': float(self.market_value) if self.market_value is not None else None,
            'main_image': main_image_data,
            'media_count': self.media.filter(is_deleted=False).count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
# -------------------------------------------------------------------------
# Room Model
# -------------------------------------------------------------------------
class Room(BaseModel):
    """Room model with integrated room types"""
    ROOM_TYPES = [
        ('bedroom', _('غرفة نوم')),
        ('bathroom', _('حمام')),
        ('kitchen', _('مطبخ')),
        ('living', _('غرفة معيشة')),
        ('dining', _('غرفة طعام')),
        ('office', _('مكتب')),
        ('other', _('أخرى')),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms', verbose_name=_('العقار'))
    name = models.CharField(_('اسم الغرفة'), max_length=100)
    room_type = models.CharField(_('نوع الغرفة'), max_length=20, choices=ROOM_TYPES)
    floor = models.PositiveSmallIntegerField(_('الطابق'), default=1)
    area_sqm = models.DecimalField(_('المساحة (متر مربع)'), max_digits=8, decimal_places=2, null=True, blank=True)
    description = models.TextField(_('الوصف'), blank=True)
    features = models.JSONField(_('المميزات'), default=list, blank=True)
    has_window = models.BooleanField(_('يحتوي على نافذة'), default=False)
    has_bathroom = models.BooleanField(_('يحتوي على حمام'), default=False)

    media = GenericRelation(Media, related_query_name='room')

    class Meta:
        verbose_name = _('غرفة')
        verbose_name_plural = _('الغرف')
        ordering = ['floor', 'room_type']
        indexes = [
            models.Index(fields=['property', 'floor']),
            models.Index(fields=['room_type']),
        ]

    def __str__(self):
        return f"{self.get_room_type_display()} - {self.name} ({self.property.title if self.property else 'N/A'})"

    def to_dict(self):
        """Return a dictionary representation for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'room_type': {
                'code': self.room_type,
                'name': self.get_room_type_display(),
            },
            'floor': self.floor,
            'area_sqm': float(self.area_sqm) if self.area_sqm else None,
            'features': self.features,
            'media': [media_item.to_dict() for media_item in self.media.all()],
        }

# -------------------------------------------------------------------------
# Auction Model
# -------------------------------------------------------------------------
class Auction(BaseModel):
    """Enhanced Auction model with auto-status management"""
    AUCTION_TYPES = [
        ('public', _('عام')),
        ('private', _('خاص')),
        ('sealed', _('مغلق')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('scheduled', _('مجدول')),
        ('live', _('مباشر')),
        ('ended', _('منتهي')),
        ('cancelled', _('ملغي')),
        ('completed', _('مكتمل')),
    ]

    title = models.CharField(_('العنوان'), max_length=255)
    slug = models.SlugField(_('الرابط المختصر'), max_length=255, unique=True, blank=True, allow_unicode=True)
    auction_type = models.CharField(_('نوع المزاد'), max_length=20, choices=AUCTION_TYPES)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='draft')
    description = models.TextField(_('الوصف'))

    start_date = models.DateTimeField(_('تاريخ البدء'))
    end_date = models.DateTimeField(_('تاريخ الانتهاء'))
    registration_deadline = models.DateTimeField(_('موعد انتهاء التسجيل'), null=True, blank=True)

    related_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='auctions', verbose_name=_('العقار'))

    starting_bid = models.DecimalField(_('المزايدة الأولية'), max_digits=14, decimal_places=2)
    current_bid = models.DecimalField(_('المزايدة الحالية'), max_digits=14, decimal_places=2, null=True, blank=True)
    minimum_increment = models.DecimalField(_('الحد الأدنى للزيادة'), max_digits=14, decimal_places=2, default=100.00)
    minimum_participants = models.PositiveIntegerField(_('الحد الأدنى للمشاركين'), default=1)
    auto_extend_minutes = models.PositiveIntegerField(_('تمديد تلقائي (دقائق)'), default=5)

    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)
    
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    bid_count = models.PositiveIntegerField(_('عدد المزايدات'), default=0)
    registered_bidders = models.PositiveIntegerField(_('المزايدين المسجلين'), default=0)

    # Auto-extension tracking
    last_bid_time = models.DateTimeField(_('وقت آخر مزايدة'), null=True, blank=True)
    extension_count = models.PositiveIntegerField(_('عدد التمديدات'), default=0)
    max_extensions = models.PositiveIntegerField(_('الحد الأقصى للتمديدات'), default=3)

    media = GenericRelation(Media, related_query_name='auction')

    class Meta:
        verbose_name = _('مزاد')
        verbose_name_plural = _('المزادات')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['related_property']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Create slug if not provided
        if not self.slug:
            self.slug = self._generate_unique_slug()

        # Update property status if auction is active
        if self.is_published and self.status in ['scheduled', 'live'] and self.related_property:
            self.related_property.status = 'auction'
            self.related_property.save(update_fields=['status'])

        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """Generate a unique slug for the auction"""
        original_slug = slugify(self.title, allow_unicode=True)
        if not original_slug:
            original_slug = f"auction-{random.randint(10000, 99999)}"
            
        unique_slug = original_slug
        counter = 1
        
        while Auction.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f"{original_slug}-{counter}"
            counter += 1
        
        return unique_slug

    def update_status_based_on_time(self):
        """Automatically update auction status based on current time"""
        now = timezone.now()
        old_status = self.status
        
        # Auto-start scheduled auctions
        if self.status == 'scheduled' and self.start_date <= now < self.end_date and self.is_published:
            self.status = 'live'
            logger.info(f"Auto-started auction {self.id}: {self.title}")
        
        # Auto-end live auctions
        elif self.status == 'live' and self.end_date <= now:
            self.status = 'ended'
            logger.info(f"Auto-ended auction {self.id}: {self.title}")
        
        # Save if status changed
        if old_status != self.status:
            self.save(update_fields=['status', 'updated_at'])
            
            # Update property status when auction ends
            if self.status == 'ended' and self.related_property:
                winning_bid = self.bids.filter(status='winning').first()
                if winning_bid:
                    self.related_property.status = 'sold'
                else:
                    self.related_property.status = 'available'
                self.related_property.save(update_fields=['status'])
        
        return self.status

    def is_biddable(self):
        """Enhanced check if auction can accept bids"""
        # Auto-update status first
        self.update_status_based_on_time()
        
        return (
            self.status == 'live' and 
            self.is_published and 
            not self.is_deleted and
            timezone.now() < self.end_date
        )

    def can_accept_bids(self):
        """Alias for backwards compatibility"""
        return self.is_biddable()

    def check_auto_extension(self, new_bid_time=None):
        """Check if auction should be auto-extended due to last-minute bid"""
        if not self.auto_extend_minutes or self.extension_count >= self.max_extensions:
            return False
            
        bid_time = new_bid_time or timezone.now()
        time_until_end = (self.end_date - bid_time).total_seconds() / 60  # minutes
        
        if time_until_end <= self.auto_extend_minutes:
            # Extend auction
            self.end_date = self.end_date + timedelta(minutes=self.auto_extend_minutes)
            self.extension_count += 1
            self.save(update_fields=['end_date', 'extension_count', 'updated_at'])
            logger.info(f"Auto-extended auction {self.id} by {self.auto_extend_minutes} minutes")
            return True
            
        return False

    @property
    def time_remaining(self):
        """Calculate time remaining until auction end"""
        if not self.end_date:
            return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0, "total_seconds": 0}
            
        # Auto-update status to get accurate end time
        self.update_status_based_on_time()
        
        if self.end_date <= timezone.now():
            return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0, "total_seconds": 0}
        
        time_left = self.end_date - timezone.now()
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": time_left.total_seconds()
        }

    def is_active(self):
        """Check if auction is currently active"""
        self.update_status_based_on_time()
        return self.status == 'live' and self.is_published

    def get_current_high_bid(self):
        """Get the current highest bid amount"""
        return self.current_bid or self.starting_bid

    def get_minimum_next_bid(self):
        """Get the minimum amount for the next bid"""
        return self.get_current_high_bid() + self.minimum_increment

    def increment_view_count(self):
        """Increment view count efficiently"""
        Auction.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])
        return self.view_count

    @property
    def registered_bidders_count(self):
        """Returns the number of users registered for this auction."""
        return self.bids.values('bidder').distinct().count()

    def to_dict(self):
        """Return a dictionary representation for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'auction_type': {
                'code': self.auction_type,
                'name': self.get_auction_type_display(),
            },
            'status': self.status,
            'status_display': self.get_status_display(),
            'description': self.description,
            'dates': {
                'start': self.start_date.isoformat() if self.start_date else None,
                'end': self.end_date.isoformat() if self.end_date else None,
                'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            },
            'property': self.related_property.to_dict() if self.related_property else None,
            'bids': {
                'starting': float(self.starting_bid) if self.starting_bid is not None else None,
                'current': float(self.current_bid) if self.current_bid is not None else None,
                'minimum_increment': float(self.minimum_increment) if self.minimum_increment is not None else None,
                'minimum_next': float(self.get_minimum_next_bid()),
                'count': self.bid_count,
            },
            'time_remaining': self.time_remaining,
            'is_active': self.is_active(),
            'is_biddable': self.is_biddable(),
            'auto_extend_info': {
                'minutes': self.auto_extend_minutes,
                'extension_count': self.extension_count,
                'max_extensions': self.max_extensions,
            }
        }
# -------------------------------------------------------------------------
# Bid Model
# -------------------------------------------------------------------------
class Bid(BaseModel):
    """Bid model for auctions"""
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('accepted', _('مقبولة')),
        ('rejected', _('مرفوضة')),
        ('outbid', _('تمت المزايدة بأعلى')),
        ('winning', _('فائزة')),
    ]

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids', verbose_name=_('المزاد'))
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids', verbose_name=_('المزايد'))
    bid_amount = models.DecimalField(_('مبلغ المزايدة'), max_digits=14, decimal_places=2)
    max_bid_amount = models.DecimalField(_('الحد الأقصى للمزايدة'), max_digits=14, decimal_places=2, null=True, blank=True)
    bid_time = models.DateTimeField(_('وقت المزايدة'), default=timezone.now)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    is_verified = models.BooleanField(_('تم التحقق'), default=False)

    class Meta:
        verbose_name = _('مزايدة')
        verbose_name_plural = _('المزايدات')
        ordering = ['-bid_time']
        indexes = [
            models.Index(fields=['auction', '-bid_time']),
            models.Index(fields=['bidder']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        bidder_name = f"{self.bidder.first_name} {self.bidder.last_name}".strip() or self.bidder.email if self.bidder else "N/A Bidder"
        auction_title = self.auction.title if self.auction else "N/A Auction"
        return f"{bidder_name} زايد بمبلغ {self.bid_amount} على {auction_title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.auction:
            # Update auction metadata - use atomic F() expression
            Auction.objects.filter(pk=self.auction.pk).update(
                bid_count=models.F('bid_count') + 1
            )
            
            # Update current bid if this bid is higher
            if not self.auction.current_bid or self.bid_amount > self.auction.current_bid:
                self.auction.current_bid = self.bid_amount
                self.auction.save(update_fields=['current_bid'])
                
                # Handle bid status updates
                if self.status in ('accepted', 'winning'):
                    # Mark previous winning bids as outbid
                    Bid.objects.filter(
                        auction=self.auction,
                        status='winning'
                    ).exclude(id=self.pk).update(status='outbid')
                    
                    # Update this bid to winning if currently just accepted
                    if self.status != 'winning':
                        self.status = 'winning'
                        Bid.objects.filter(pk=self.pk).update(status='winning')

    @property
    def bidder_name(self):
        """Get formatted bidder name"""
        if not self.bidder:
            return "Unknown"
        full_name = f"{self.bidder.first_name} {self.bidder.last_name}".strip()
        return full_name or self.bidder.email

    def to_dict(self):
        """Return a dictionary representation for API responses"""
        return {
            'id': self.id,
            'auction_id': self.auction_id,
            'bidder': {
                'id': self.bidder.id,
                'name': self.bidder_name,
            } if self.bidder else None,
            'amount': float(self.bid_amount) if self.bid_amount is not None else None,
            'max_amount': float(self.max_bid_amount) if self.max_bid_amount is not None else None,
            'status': self.status,
            'status_display': self.get_status_display(),
            'bid_time': self.bid_time.isoformat() if self.bid_time else None,
            'is_verified': self.is_verified,
        }

# -------------------------------------------------------------------------
# message Model
# -------------------------------------------------------------------------

class Message(BaseModel):
    """Message model for property inquiries and communication"""
    
    STATUS_CHOICES = [
        ('unread', _('غير مقروء')),
        ('read', _('مقروء')),
        ('replied', _('تم الرد')),
        ('archived', _('مؤرشف')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('منخفض')),
        ('normal', _('عادي')),
        ('high', _('عالي')),
        ('urgent', _('عاجل')),
    ]
    
    # Core fields
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name=_('المرسل')
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name=_('المستقبل')
    )
    
    # Message content
    subject = models.CharField(_('الموضوع'), max_length=255)
    body = models.TextField(_('محتوى الرسالة'))
    
    # Related property (optional - messages can be about specific properties)
    related_property = models.ForeignKey(
        Property, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='messages',
        verbose_name=_('العقار المرتبط')
    )
    
    # Message metadata
    status = models.CharField(
        _('الحالة'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='unread'
    )
    priority = models.CharField(
        _('الأولوية'), 
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='normal'
    )
    
    # Timestamps
    read_at = models.DateTimeField(_('تاريخ القراءة'), null=True, blank=True)
    replied_at = models.DateTimeField(_('تاريخ الرد'), null=True, blank=True)
    
    # Thread support
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies',
        verbose_name=_('الرسالة الأصلية')
    )
    thread_id = models.UUIDField(_('معرف المحادثة'), default=uuid.uuid4, db_index=True)
    
    # Additional metadata
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    user_agent = models.TextField(_('متصفح المستخدم'), blank=True)
    
    class Meta:
        verbose_name = _('رسالة')
        verbose_name_plural = _('الرسائل')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', '-created_at']),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['thread_id', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['related_property', '-created_at']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.sender} to {self.recipient}"

    def save(self, *args, **kwargs):
        # Set thread_id for new messages
        if not self.pk and not self.parent_message:
            self.thread_id = uuid.uuid4()
        elif self.parent_message:
            self.thread_id = self.parent_message.thread_id
            
        super().save(*args, **kwargs)

    def mark_as_read(self):
        """Mark message as read"""
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])

    def mark_as_replied(self):
        """Mark message as replied"""
        self.status = 'replied'
        self.replied_at = timezone.now()
        self.save(update_fields=['status', 'replied_at'])

    @property 
    def is_read(self):
        return self.status in ['read', 'replied', 'archived']
    
    @property
    def thread_messages(self):
        """Get all messages in this thread"""
        return Message.objects.filter(thread_id=self.thread_id).order_by('created_at')
    
    @property
    def reply_count(self):
        """Get number of replies in thread"""
        return self.replies.count()

    def get_thread_participants(self):
        """Get all unique participants in this thread"""
        messages = Message.objects.filter(thread_id=self.thread_id)
        participants = set()
        for msg in messages:
            participants.add(msg.sender)
            participants.add(msg.recipient)
        return list(participants)

    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'subject': self.subject,
            'body': self.body,
            'status': self.status,
            'status_display': self.get_status_display(),
            'priority': self.priority,
            'priority_display': self.get_priority_display(),
            'sender': {
                'id': self.sender.id,
                'name': f"{self.sender.first_name} {self.sender.last_name}".strip() or self.sender.email,
                'email': self.sender.email,
            },
            'recipient': {
                'id': self.recipient.id,
                'name': f"{self.recipient.first_name} {self.recipient.last_name}".strip() or self.recipient.email,
                'email': self.recipient.email,
            },
            'related_property': {
                'id': self.related_property.id,
                'title': self.related_property.title,
                'slug': self.related_property.slug,
            } if self.related_property else None,
            'thread_id': str(self.thread_id),
            'parent_message_id': self.parent_message.id if self.parent_message else None,
            'reply_count': self.reply_count,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
        }


class MessageAttachment(BaseModel):
    """File attachments for messages"""
    
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        verbose_name=_('الرسالة')
    )
    file = models.FileField(_('الملف'), upload_to='message_attachments/%Y/%m/%d/')
    original_name = models.CharField(_('الاسم الأصلي'), max_length=255)
    file_size = models.PositiveIntegerField(_('حجم الملف'), help_text=_('بالبايت'))
    content_type = models.CharField(_('نوع المحتوى'), max_length=100)
    
    class Meta:
        verbose_name = _('مرفق رسالة')
        verbose_name_plural = _('مرفقات الرسائل')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_name} - {self.message.subject}"

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.original_name:
            self.original_name = self.file.name
        super().save(*args, **kwargs)

    @property
    def file_size_formatted(self):
        """Return formatted file size"""
        if not self.file_size:
            return '0 B'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"




class DashboardMetrics(BaseModel):
    """Store cached dashboard metrics for performance"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboard_metrics')
    metric_type = models.CharField(max_length=50)  # 'properties', 'auctions', 'bids', etc.
    metric_data = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('مقاييس لوحة التحكم')
        verbose_name_plural = _('مقاييس لوحات التحكم')
        unique_together = ['user', 'metric_type']
        
    def __str__(self):
        return f"{self.user.email} - {self.metric_type}"


# -------------------------------------------------------------------------
# Property Management Models
# -------------------------------------------------------------------------

class RentalProperty(BaseModel):
    """Extended property model for rental management"""
    RENTAL_STATUS_CHOICES = [
        ('available', _('متاح للإيجار')),
        ('rented', _('مؤجر')),
        ('maintenance', _('تحت الصيانة')),
        ('unavailable', _('غير متاح')),
    ]
    
    RENTAL_TYPE_CHOICES = [
        ('monthly', _('شهري')),
        ('yearly', _('سنوي')),
        ('daily', _('يومي')),
        ('weekly', _('أسبوعي')),
    ]

    # Link to base property
    base_property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='rental_info', verbose_name=_('العقار'))
    
    # Rental-specific fields
    rental_status = models.CharField(_('حالة الإيجار'), max_length=20, choices=RENTAL_STATUS_CHOICES, default='available')
    rental_type = models.CharField(_('نوع الإيجار'), max_length=20, choices=RENTAL_TYPE_CHOICES, default='monthly')
    monthly_rent = models.DecimalField(_('الإيجار الشهري'), max_digits=12, decimal_places=2)
    security_deposit = models.DecimalField(_('التأمين'), max_digits=12, decimal_places=2, default=0)
    management_fee_percentage = models.DecimalField(_('نسبة رسوم الإدارة'), max_digits=5, decimal_places=2, default=0)
    
    # Utilities and services
    utilities_included = models.BooleanField(_('المرافق مشمولة'), default=False)
    utilities_details = models.JSONField(_('تفاصيل المرافق'), default=dict, blank=True)
    parking_spaces = models.PositiveIntegerField(_('أماكن الوقوف'), default=0)
    furnished = models.BooleanField(_('مفروش'), default=False)
    pets_allowed = models.BooleanField(_('الحيوانات الأليفة مسموحة'), default=False)
    smoking_allowed = models.BooleanField(_('التدخين مسموح'), default=False)
    
    # Availability
    available_from = models.DateField(_('متاح من'), null=True, blank=True)
    minimum_lease_period = models.PositiveIntegerField(_('أقل مدة إيجار (بالأشهر)'), default=12)
    maximum_lease_period = models.PositiveIntegerField(_('أقصى مدة إيجار (بالأشهر)'), default=36)
    
    # Financial tracking
    total_rental_income = models.DecimalField(_('إجمالي الدخل الإيجاري'), max_digits=14, decimal_places=2, default=0)
    last_rent_increase = models.DateField(_('آخر زيادة إيجار'), null=True, blank=True)
    next_rent_review = models.DateField(_('موعد مراجعة الإيجار القادم'), null=True, blank=True)

    class Meta:
        verbose_name = _('عقار إيجاري')
        verbose_name_plural = _('العقارات الإيجارية')
        indexes = [
            models.Index(fields=['rental_status']),
            models.Index(fields=['monthly_rent']),
            models.Index(fields=['available_from']),
        ]

    def __str__(self):
        return f"{self.base_property.title} - {self.get_rental_status_display()}"

    @property
    def current_tenant(self):
        """Get the current active tenant"""
        from django.utils import timezone
        active_lease = self.leases.filter(
            status='active',
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first()
        return active_lease.tenant if active_lease else None

    @property
    def is_occupied(self):
        """Check if property is currently occupied"""
        return self.current_tenant is not None

    @property
    def occupancy_rate(self):
        """Calculate occupancy rate for the current year"""
        from django.utils import timezone
        from datetime import timedelta
        
        current_year = timezone.now().year
        year_start = timezone.datetime(current_year, 1, 1).date()
        year_end = timezone.datetime(current_year, 12, 31).date()
        
        occupied_days = 0
        total_days = (year_end - year_start).days + 1
        
        active_leases = self.leases.filter(
            models.Q(start_date__lte=year_end) & models.Q(end_date__gte=year_start)
        )
        
        for lease in active_leases:
            lease_start = max(lease.start_date, year_start)
            lease_end = min(lease.end_date, year_end)
            occupied_days += (lease_end - lease_start).days + 1
        
        return (occupied_days / total_days) * 100 if total_days > 0 else 0

    def calculate_annual_income(self):
        """Calculate expected annual income"""
        return float(self.monthly_rent) * 12

    def to_dict(self):
        """Return dictionary representation for API responses"""
        base_dict = self.base_property.to_dict()
        base_dict.update({
            'rental_info': {
                'id': self.id,
                'rental_status': self.rental_status,
                'rental_status_display': self.get_rental_status_display(),
                'rental_type': self.rental_type,
                'rental_type_display': self.get_rental_type_display(),
                'monthly_rent': float(self.monthly_rent),
                'security_deposit': float(self.security_deposit),
                'utilities_included': self.utilities_included,
                'parking_spaces': self.parking_spaces,
                'furnished': self.furnished,
                'pets_allowed': self.pets_allowed,
                'smoking_allowed': self.smoking_allowed,
                'available_from': self.available_from.isoformat() if self.available_from else None,
                'minimum_lease_period': self.minimum_lease_period,
                'current_tenant': self.current_tenant.to_dict() if self.current_tenant else None,
                'is_occupied': self.is_occupied,
                'occupancy_rate': round(self.occupancy_rate, 2),
                'annual_income': self.calculate_annual_income(),
            }
        })
        return base_dict


class Tenant(BaseModel):
    """Tenant information and management"""
    TENANT_TYPE_CHOICES = [
        ('individual', _('فردي')),
        ('family', _('عائلة')),
        ('company', _('شركة')),
        ('government', _('حكومي')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('blacklisted', _('مدرج في القائمة السوداء')),
        ('former', _('سابق')),
    ]

    # Link to user account (optional)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='tenant_profile', verbose_name=_('حساب المستخدم'))
    
    # Basic information
    first_name = models.CharField(_('الاسم الأول'), max_length=100)
    last_name = models.CharField(_('اسم العائلة'), max_length=100)
    middle_name = models.CharField(_('الاسم الأوسط'), max_length=100, blank=True)
    tenant_type = models.CharField(_('نوع المستأجر'), max_length=20, choices=TENANT_TYPE_CHOICES, default='individual')
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Contact information
    email = models.EmailField(_('البريد الإلكتروني'), unique=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=17)
    alternative_phone = models.CharField(_('رقم بديل'), max_length=17, blank=True)
    
    # Personal information
    national_id = models.CharField(_('رقم الهوية'), max_length=20, unique=True)
    date_of_birth = models.DateField(_('تاريخ الميلاد'), null=True, blank=True)
    nationality = models.CharField(_('الجنسية'), max_length=50, default='سعودي')
    occupation = models.CharField(_('المهنة'), max_length=100, blank=True)
    employer = models.CharField(_('جهة العمل'), max_length=200, blank=True)
    monthly_income = models.DecimalField(_('الدخل الشهري'), max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Address
    current_address = models.TextField(_('العنوان الحالي'))
    emergency_contact_name = models.CharField(_('اسم الشخص للطوارئ'), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_('هاتف الطوارئ'), max_length=17, blank=True)
    emergency_contact_relation = models.CharField(_('صلة القرابة'), max_length=50, blank=True)
    
    # Company information (if applicable)
    company_name = models.CharField(_('اسم الشركة'), max_length=200, blank=True)
    company_registration = models.CharField(_('رقم السجل التجاري'), max_length=50, blank=True)
    company_address = models.TextField(_('عنوان الشركة'), blank=True)
    
    # Credit and references
    credit_score = models.PositiveIntegerField(_('التقييم الائتماني'), null=True, blank=True)
    references = models.JSONField(_('المراجع'), default=list, blank=True)
    background_check_passed = models.BooleanField(_('تم فحص السجل'), default=False)
    background_check_date = models.DateField(_('تاريخ فحص السجل'), null=True, blank=True)
    
    # Notes and history
    notes = models.TextField(_('ملاحظات'), blank=True)
    move_in_date = models.DateField(_('تاريخ الانتقال'), null=True, blank=True)
    move_out_date = models.DateField(_('تاريخ المغادرة'), null=True, blank=True)
    
    # Financial information
    preferred_payment_method = models.CharField(_('طريقة الدفع المفضلة'), max_length=50, blank=True)
    bank_account_info = models.JSONField(_('معلومات الحساب البنكي'), default=dict, blank=True)

    class Meta:
        verbose_name = _('مستأجر')
        verbose_name_plural = _('المستأجرون')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['national_id']),
            models.Index(fields=['status']),
            models.Index(fields=['tenant_type']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        """Get tenant's full name"""
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, names))

    @property
    def current_lease(self):
        """Get current active lease"""
        from django.utils import timezone
        return self.leases.filter(
            status='active',
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first()

    @property
    def current_property(self):
        """Get currently rented property"""
        lease = self.current_lease
        return lease.rental_property if lease else None

    def get_lease_history(self):
        """Get all lease history for this tenant"""
        return self.leases.all().order_by('-start_date')

    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'tenant_type': self.tenant_type,
            'tenant_type_display': self.get_tenant_type_display(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'national_id': self.national_id,
            'occupation': self.occupation,
            'monthly_income': float(self.monthly_income) if self.monthly_income else None,
            'current_property': self.current_property.base_property.title if self.current_property else None,
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Lease(BaseModel):
    """Lease agreements between tenants and rental properties"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('active', _('نشط')),
        ('expired', _('منتهي')),
        ('terminated', _('مفسوخ')),
        ('renewed', _('تم تجديده')),
    ]
    
    PAYMENT_FREQUENCY_CHOICES = [
        ('monthly', _('شهري')),
        ('quarterly', _('ربع سنوي')),
        ('semi_annually', _('نصف سنوي')),
        ('annually', _('سنوي')),
    ]

    # Relationships
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases', verbose_name=_('المستأجر'))
    rental_property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, related_name='leases', verbose_name=_('العقار'))
    
    # Lease details
    lease_number = models.CharField(_('رقم العقد'), max_length=50, unique=True)
    status = models.CharField(_('حالة العقد'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    start_date = models.DateField(_('تاريخ البداية'))
    end_date = models.DateField(_('تاريخ النهاية'))
    signed_date = models.DateField(_('تاريخ التوقيع'), null=True, blank=True)
    
    # Financial terms
    monthly_rent = models.DecimalField(_('الإيجار الشهري'), max_digits=12, decimal_places=2)
    security_deposit = models.DecimalField(_('مبلغ التأمين'), max_digits=12, decimal_places=2)
    payment_frequency = models.CharField(_('دورية الدفع'), max_length=20, choices=PAYMENT_FREQUENCY_CHOICES, default='monthly')
    payment_due_day = models.PositiveIntegerField(_('يوم استحقاق الدفع'), default=1)
    late_fee_amount = models.DecimalField(_('غرامة التأخير'), max_digits=8, decimal_places=2, default=0)
    late_fee_grace_period = models.PositiveIntegerField(_('مهلة الغرامة (بالأيام)'), default=5)
    
    # Terms and conditions
    terms_and_conditions = models.TextField(_('الشروط والأحكام'))
    special_clauses = models.TextField(_('بنود خاصة'), blank=True)
    renewal_option = models.BooleanField(_('خيار التجديد'), default=True)
    rent_increase_percentage = models.DecimalField(_('نسبة زيادة الإيجار'), max_digits=5, decimal_places=2, default=0)
    
    # Utilities and services
    utilities_included = models.JSONField(_('المرافق المشمولة'), default=list)
    tenant_responsibilities = models.JSONField(_('مسؤوليات المستأجر'), default=list)
    landlord_responsibilities = models.JSONField(_('مسؤوليات المالك'), default=list)
    
    # Documents and attachments
    lease_document = models.FileField(_('وثيقة العقد'), upload_to='leases/%Y/%m/', null=True, blank=True)
    attachments = GenericRelation(Media, related_query_name='lease')
    
    # Renewal tracking
    parent_lease = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='renewals', verbose_name=_('العقد الأصلي'))
    auto_renewal = models.BooleanField(_('التجديد التلقائي'), default=False)
    renewal_notice_period = models.PositiveIntegerField(_('مدة إشعار التجديد (بالأيام)'), default=30)

    class Meta:
        verbose_name = _('عقد إيجار')
        verbose_name_plural = _('عقود الإيجار')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['lease_number']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['tenant']),
            models.Index(fields=['rental_property']),
        ]

    def __str__(self):
        return f"عقد {self.lease_number} - {self.tenant.full_name}"

    def save(self, *args, **kwargs):
        if not self.lease_number:
            self.lease_number = self._generate_lease_number()
        super().save(*args, **kwargs)

    def _generate_lease_number(self):
        """Generate unique lease number"""
        from django.utils import timezone
        year = timezone.now().year
        count = Lease.objects.filter(created_at__year=year).count() + 1
        return f"LSE-{year}-{count:05d}"

    @property
    def duration_months(self):
        """Calculate lease duration in months"""
        if self.start_date and self.end_date:
            return (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
        return 0

    @property
    def total_rent_amount(self):
        """Calculate total rent for the lease period"""
        return float(self.monthly_rent) * self.duration_months

    @property
    def is_active(self):
        """Check if lease is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (self.status == 'active' and 
                self.start_date <= today <= self.end_date)

    @property
    def days_remaining(self):
        """Calculate days remaining in lease"""
        from django.utils import timezone
        if self.end_date:
            days = (self.end_date - timezone.now().date()).days
            return max(0, days)
        return 0

    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'lease_number': self.lease_number,
            'status': self.status,
            'status_display': self.get_status_display(),
            'tenant': self.tenant.to_dict() if self.tenant else None,
            'property': self.rental_property.base_property.title if self.rental_property else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'monthly_rent': float(self.monthly_rent),
            'security_deposit': float(self.security_deposit),
            'duration_months': self.duration_months,
            'total_rent_amount': self.total_rent_amount,
            'is_active': self.is_active,
            'days_remaining': self.days_remaining,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class MaintenanceCategory(BaseModel):
    """Categories for maintenance requests"""
    name = models.CharField(_('اسم الفئة'), max_length=100, unique=True)
    description = models.TextField(_('الوصف'), blank=True)
    icon = models.CharField(_('أيقونة'), max_length=50, blank=True)
    color = models.CharField(_('اللون'), max_length=7, default='#007bff')
    priority_level = models.PositiveIntegerField(_('مستوى الأولوية'), default=3, help_text='1=عاجل, 5=منخفض')
    estimated_cost_range_min = models.DecimalField(_('الحد الأدنى للتكلفة المتوقعة'), max_digits=10, decimal_places=2, default=0)
    estimated_cost_range_max = models.DecimalField(_('الحد الأقصى للتكلفة المتوقعة'), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_('نشط'), default=True)

    class Meta:
        verbose_name = _('فئة صيانة')
        verbose_name_plural = _('فئات الصيانة')
        ordering = ['priority_level', 'name']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'priority_level': self.priority_level,
            'estimated_cost_range': {
                'min': float(self.estimated_cost_range_min),
                'max': float(self.estimated_cost_range_max)
            },
            'is_active': self.is_active,
        }


# -------------------------------------------------------------------------
# Worker/Staff Models for Property Management
# -------------------------------------------------------------------------

class WorkerCategory(BaseModel):
    """Categories/Skills for workers (plumber, electrician, cleaner, etc.)"""
    name = models.CharField(_('اسم الفئة'), max_length=100, unique=True)
    description = models.TextField(_('الوصف'), blank=True)
    icon = models.CharField(_('أيقونة'), max_length=50, blank=True)
    color = models.CharField(_('اللون'), max_length=7, default='#28a745')
    hourly_rate_min = models.DecimalField(_('الحد الأدنى للأجر بالساعة'), max_digits=8, decimal_places=2, default=0)
    hourly_rate_max = models.DecimalField(_('الحد الأقصى للأجر بالساعة'), max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(_('نشط'), default=True)
    
    class Meta:
        verbose_name = _('فئة عامل')
        verbose_name_plural = _('فئات العمال')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Worker(BaseModel):
    """Workers/Staff for property maintenance and management"""
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('دوام كامل')),
        ('part_time', _('دوام جزئي')),
        ('contract', _('مقاول')),
        ('freelance', _('عمل حر')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('inactive', _('غير نشط')),
        ('on_leave', _('في إجازة')),
        ('suspended', _('موقوف')),
    ]
    
    # Personal Information
    first_name = models.CharField(_('الاسم الأول'), max_length=100)
    last_name = models.CharField(_('اسم العائلة'), max_length=100)
    email = models.EmailField(_('البريد الإلكتروني'), unique=True, null=True, blank=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    national_id = models.CharField(_('رقم الهوية'), max_length=50, unique=True)
    
    # Professional Information
    employee_id = models.CharField(_('رقم الموظف'), max_length=20, unique=True, blank=True)
    categories = models.ManyToManyField(WorkerCategory, related_name='workers', verbose_name=_('المهارات/الفئات'))
    employment_type = models.CharField(_('نوع التوظيف'), max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Contact Information  
    address = models.TextField(_('العنوان'), blank=True)
    city = models.CharField(_('المدينة'), max_length=100, blank=True)
    emergency_contact = models.CharField(_('جهة اتصال الطوارئ'), max_length=200, blank=True)
    emergency_phone = models.CharField(_('هاتف الطوارئ'), max_length=20, blank=True)
    
    # Work Information
    hourly_rate = models.DecimalField(_('الأجر بالساعة'), max_digits=8, decimal_places=2, default=0)
    hire_date = models.DateField(_('تاريخ التوظيف'), default=timezone.now)
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='supervised_workers', verbose_name=_('المشرف'))
    
    # Availability
    is_available = models.BooleanField(_('متاح للعمل'), default=True)
    max_concurrent_jobs = models.PositiveIntegerField(_('الحد الأقصى للمهام المتزامنة'), default=3)
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    # Profile Image
    profile_image = models.ImageField(_('صورة الملف الشخصي'), upload_to='workers/profiles/%Y/%m/', null=True, blank=True)
    
    # Ratings and Performance
    rating = models.DecimalField(_('التقييم'), max_digits=3, decimal_places=2, null=True, blank=True, 
                               help_text='من 1.00 إلى 5.00')
    total_jobs_completed = models.PositiveIntegerField(_('إجمالي المهام المكتملة'), default=0)
    
    class Meta:
        verbose_name = _('عامل')
        verbose_name_plural = _('العمال')
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['status', 'is_available']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['national_id']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id or self.national_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def current_active_jobs(self):
        """Get count of current active maintenance jobs"""
        return self.assigned_maintenance.filter(
            status__in=['assigned', 'in_progress']
        ).count()
    
    @property
    def can_take_new_job(self):
        """Check if worker can take a new job based on availability and workload"""
        return (self.is_available and 
                self.status == 'active' and 
                self.current_active_jobs < self.max_concurrent_jobs)
    
    def save(self, *args, **kwargs):
        # Auto-generate employee ID if not provided
        if not self.employee_id:
            # Format: WRK-YYYY-NNNN
            year = timezone.now().year
            last_worker = Worker.objects.filter(
                employee_id__startswith=f'WRK-{year}-'
            ).order_by('employee_id').last()
            
            if last_worker and last_worker.employee_id:
                try:
                    last_num = int(last_worker.employee_id.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            
            self.employee_id = f'WRK-{year}-{new_num:04d}'
        
        super().save(*args, **kwargs)
    
    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'categories': [cat.name for cat in self.categories.all()],
            'employment_type': self.get_employment_type_display(),
            'status': self.get_status_display(),
            'hourly_rate': float(self.hourly_rate),
            'is_available': self.is_available,
            'can_take_new_job': self.can_take_new_job,
            'current_active_jobs': self.current_active_jobs,
            'rating': float(self.rating) if self.rating else None,
            'total_jobs_completed': self.total_jobs_completed,
            'profile_image_url': self.profile_image.url if self.profile_image else None,
        }


class MaintenanceRequest(BaseModel):
    """Maintenance requests for properties"""
    PRIORITY_CHOICES = [
        ('urgent', _('عاجل')),
        ('high', _('عالي')),
        ('medium', _('متوسط')),
        ('low', _('منخفض')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('assigned', _('مُعين')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
        ('on_hold', _('معلق')),
    ]

    # Relationships
    base_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_requests', verbose_name=_('العقار'))
    rental_property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, null=True, blank=True, 
                                      related_name='maintenance_requests', verbose_name=_('العقار الإيجاري'))
    category = models.ForeignKey(MaintenanceCategory, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='requests', verbose_name=_('الفئة'))
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                   related_name='maintenance_requests', verbose_name=_('طالب الصيانة'))
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_maintenance', verbose_name=_('مُعين إلى (مشرف)'))
    assigned_worker = models.ForeignKey('Worker', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='assigned_maintenance', verbose_name=_('العامل المُعين'))
    
    # Request details
    title = models.CharField(_('عنوان الطلب'), max_length=200)
    description = models.TextField(_('وصف المشكلة'))
    priority = models.CharField(_('الأولوية'), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Location within property
    specific_location = models.CharField(_('الموقع المحدد'), max_length=200, blank=True, 
                                       help_text='مثل: غرفة النوم الرئيسية، المطبخ، الحمام')
    
    # Timing
    reported_date = models.DateTimeField(_('تاريخ الإبلاغ'), auto_now_add=True)
    due_date = models.DateTimeField(_('التاريخ المستهدف'), null=True, blank=True)
    started_date = models.DateTimeField(_('تاريخ البدء'), null=True, blank=True)
    completed_date = models.DateTimeField(_('تاريخ الإنجاز'), null=True, blank=True)
    
    # Cost tracking
    estimated_cost = models.DecimalField(_('التكلفة المتوقعة'), max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(_('التكلفة الفعلية'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Contractor information
    contractor_name = models.CharField(_('اسم المقاول'), max_length=200, blank=True)
    contractor_phone = models.CharField(_('هاتف المقاول'), max_length=17, blank=True)
    contractor_email = models.EmailField(_('بريد المقاول'), blank=True)
    
    # Additional details
    tenant_access_required = models.BooleanField(_('يتطلب دخول المستأجر'), default=False)
    tenant_notified = models.BooleanField(_('تم إشعار المستأجر'), default=False)
    emergency_repair = models.BooleanField(_('إصلاح طارئ'), default=False)
    warranty_work = models.BooleanField(_('عمل تحت الضمان'), default=False)
    
    # Work details
    work_description = models.TextField(_('وصف العمل المنجز'), blank=True)
    materials_used = models.JSONField(_('المواد المستخدمة'), default=list, blank=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    # Quality and satisfaction
    quality_rating = models.PositiveIntegerField(_('تقييم الجودة'), null=True, blank=True, 
                                               help_text='من 1 إلى 5')
    tenant_satisfaction = models.PositiveIntegerField(_('رضا المستأجر'), null=True, blank=True, 
                                                    help_text='من 1 إلى 5')
    
    # Media attachments
    attachments = GenericRelation(Media, related_query_name='maintenance_request')

    class Meta:
        verbose_name = _('طلب صيانة')
        verbose_name_plural = _('طلبات الصيانة')
        ordering = ['-reported_date']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['base_property', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['assigned_worker', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['reported_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.base_property.title}"

    @property
    def is_overdue(self):
        """Check if maintenance request is overdue"""
        from django.utils import timezone
        return (self.due_date and 
                self.due_date < timezone.now() and 
                self.status not in ['completed', 'cancelled'])

    @property
    def duration_days(self):
        """Calculate duration from start to completion"""
        if self.started_date and self.completed_date:
            return (self.completed_date.date() - self.started_date.date()).days
        return None

    @property
    def cost_variance(self):
        """Calculate variance between estimated and actual cost"""
        if self.estimated_cost and self.actual_cost:
            return float(self.actual_cost) - float(self.estimated_cost)
        return None

    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'status_display': self.get_status_display(),
            'priority': self.priority,
            'priority_display': self.get_priority_display(),
            'property': {
                'id': self.base_property.id,
                'title': self.base_property.title,
            } if self.base_property else None,
            'category': self.category.to_dict() if self.category else None,
            'requested_by': {
                'id': self.requested_by.id,
                'name': f"{self.requested_by.first_name} {self.requested_by.last_name}",
            } if self.requested_by else None,
            'assigned_to': {
                'id': self.assigned_to.id,
                'name': f"{self.assigned_to.first_name} {self.assigned_to.last_name}",
            } if self.assigned_to else None,
            'assigned_worker': {
                'id': self.assigned_worker.id,
                'employee_id': self.assigned_worker.employee_id,
                'name': self.assigned_worker.full_name,
                'phone': self.assigned_worker.phone,
                'categories': [cat.name for cat in self.assigned_worker.categories.all()],
                'is_available': self.assigned_worker.is_available,
            } if self.assigned_worker else None,
            'specific_location': self.specific_location,
            'reported_date': self.reported_date.isoformat() if self.reported_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'actual_cost': float(self.actual_cost) if self.actual_cost else None,
            'is_overdue': self.is_overdue,
            'emergency_repair': self.emergency_repair,
            'tenant_access_required': self.tenant_access_required,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ExpenseCategory(BaseModel):
    """Categories for property expenses"""
    name = models.CharField(_('اسم الفئة'), max_length=100, unique=True)
    description = models.TextField(_('الوصف'), blank=True)
    icon = models.CharField(_('أيقونة'), max_length=50, blank=True)
    color = models.CharField(_('اللون'), max_length=7, default='#28a745')
    is_tax_deductible = models.BooleanField(_('قابل للخصم الضريبي'), default=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='subcategories', verbose_name=_('الفئة الأب'))

    class Meta:
        verbose_name = _('فئة مصروف')
        verbose_name_plural = _('فئات المصاريف')
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'is_tax_deductible': self.is_tax_deductible,
            'is_active': self.is_active,
            'parent_category': self.parent_category.name if self.parent_category else None,
        }


class Expense(BaseModel):
    """Property-related expenses tracking"""
    EXPENSE_TYPE_CHOICES = [
        ('maintenance', _('صيانة')),
        ('utilities', _('مرافق')),
        ('management', _('إدارة')),
        ('insurance', _('تأمين')),
        ('taxes', _('ضرائب')),
        ('marketing', _('تسويق')),
        ('legal', _('قانونية')),
        ('improvement', _('تحسينات')),
        ('other', _('أخرى')),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('نقد')),
        ('bank_transfer', _('تحويل بنكي')),
        ('check', _('شيك')),
        ('credit_card', _('بطاقة ائتمان')),
        ('debit_card', _('بطاقة خصم')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('approved', _('موافق عليه')),
        ('paid', _('مدفوع')),
        ('rejected', _('مرفوض')),
    ]

    # Relationships
    base_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='expenses', verbose_name=_('العقار'))
    rental_property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='expenses', verbose_name=_('العقار الإيجاري'))
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='expenses', verbose_name=_('الفئة'))
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='expenses', verbose_name=_('طلب الصيانة'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='created_expenses', verbose_name=_('أنشأه'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_expenses', verbose_name=_('وافق عليه'))
    
    # Expense details
    title = models.CharField(_('عنوان المصروف'), max_length=200)
    description = models.TextField(_('الوصف'))
    expense_type = models.CharField(_('نوع المصروف'), max_length=20, choices=EXPENSE_TYPE_CHOICES)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial information
    amount = models.DecimalField(_('المبلغ'), max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(_('مبلغ الضريبة'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('المبلغ الإجمالي'), max_digits=12, decimal_places=2)
    currency = models.CharField(_('العملة'), max_length=3, default='SAR')
    
    # Payment information
    payment_method = models.CharField(_('طريقة الدفع'), max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_date = models.DateField(_('تاريخ الدفع'), null=True, blank=True)
    payment_reference = models.CharField(_('مرجع الدفعة'), max_length=100, blank=True)
    
    # Vendor information
    vendor_name = models.CharField(_('اسم المورد'), max_length=200, blank=True)
    vendor_phone = models.CharField(_('هاتف المورد'), max_length=17, blank=True)
    vendor_email = models.EmailField(_('بريد المورد'), blank=True)
    vendor_address = models.TextField(_('عنوان المورد'), blank=True)
    
    # Documentation
    invoice_number = models.CharField(_('رقم الفاتورة'), max_length=100, blank=True)
    invoice_date = models.DateField(_('تاريخ الفاتورة'), null=True, blank=True)
    receipt_number = models.CharField(_('رقم الإيصال'), max_length=100, blank=True)
    
    # Dates
    expense_date = models.DateField(_('تاريخ المصروف'))
    due_date = models.DateField(_('تاريخ الاستحقاق'), null=True, blank=True)
    
    # Additional information
    is_recurring = models.BooleanField(_('متكرر'), default=False)
    recurring_frequency = models.CharField(_('تكرار'), max_length=20, blank=True, 
                                         help_text='monthly, quarterly, annually')
    is_emergency = models.BooleanField(_('طارئ'), default=False)
    is_tax_deductible = models.BooleanField(_('قابل للخصم الضريبي'), default=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    # Attachments
    attachments = GenericRelation(Media, related_query_name='expense')

    class Meta:
        verbose_name = _('مصروف')
        verbose_name_plural = _('المصاريف')
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['base_property', 'expense_date']),
            models.Index(fields=['status']),
            models.Index(fields=['expense_type']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        # Auto-calculate total amount if not provided
        if not self.total_amount:
            self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if expense payment is overdue"""
        from django.utils import timezone
        return (self.due_date and 
                self.due_date < timezone.now().date() and 
                self.status not in ['paid', 'rejected'])

    @property
    def days_until_due(self):
        """Calculate days until due date"""
        from django.utils import timezone
        if self.due_date:
            return (self.due_date - timezone.now().date()).days
        return None

    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'expense_type': self.expense_type,
            'expense_type_display': self.get_expense_type_display(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'amount': float(self.amount),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'property': {
                'id': self.base_property.id,
                'title': self.base_property.title,
            } if self.base_property else None,
            'category': self.category.to_dict() if self.category else None,
            'vendor_name': self.vendor_name,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_overdue': self.is_overdue,
            'is_recurring': self.is_recurring,
            'is_emergency': self.is_emergency,
            'is_tax_deductible': self.is_tax_deductible,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class PropertyAnalytics(BaseModel):
    """Cached analytics data for properties"""
    base_property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='analytics', verbose_name=_('العقار'))
    rental_property = models.OneToOneField(RentalProperty, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='analytics', verbose_name=_('العقار الإيجاري'))
    
    # Financial metrics
    total_revenue = models.DecimalField(_('إجمالي الإيرادات'), max_digits=14, decimal_places=2, default=0)
    total_expenses = models.DecimalField(_('إجمالي المصاريف'), max_digits=14, decimal_places=2, default=0)
    net_income = models.DecimalField(_('صافي الدخل'), max_digits=14, decimal_places=2, default=0)
    roi_percentage = models.DecimalField(_('نسبة العائد على الاستثمار'), max_digits=5, decimal_places=2, default=0)
    
    # Occupancy metrics
    occupancy_rate = models.DecimalField(_('معدل الإشغال'), max_digits=5, decimal_places=2, default=0)
    vacancy_days = models.PositiveIntegerField(_('أيام الشغور'), default=0)
    tenant_turnover_rate = models.DecimalField(_('معدل دوران المستأجرين'), max_digits=5, decimal_places=2, default=0)
    
    # Maintenance metrics
    maintenance_cost = models.DecimalField(_('تكلفة الصيانة'), max_digits=12, decimal_places=2, default=0)
    maintenance_requests_count = models.PositiveIntegerField(_('عدد طلبات الصيانة'), default=0)
    average_repair_time = models.PositiveIntegerField(_('متوسط وقت الإصلاح (بالأيام)'), default=0)
    
    # Market metrics
    market_rent_estimate = models.DecimalField(_('تقدير الإيجار السوقي'), max_digits=12, decimal_places=2, null=True, blank=True)
    property_appreciation = models.DecimalField(_('تقدير ارتفاع قيمة العقار'), max_digits=5, decimal_places=2, default=0)
    
    # Time period for analytics
    calculation_date = models.DateField(_('تاريخ الحساب'), auto_now=True)
    period_start = models.DateField(_('بداية الفترة'))
    period_end = models.DateField(_('نهاية الفترة'))
    
    # Additional metrics as JSON for flexibility
    additional_metrics = models.JSONField(_('مقاييس إضافية'), default=dict, blank=True)

    class Meta:
        verbose_name = _('تحليلات العقار')
        verbose_name_plural = _('تحليلات العقارات')
        ordering = ['-calculation_date']

    def __str__(self):
        return f"تحليلات {self.base_property.title} - {self.calculation_date}"

    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'property_id': self.base_property.id,
            'total_revenue': float(self.total_revenue),
            'total_expenses': float(self.total_expenses),
            'net_income': float(self.net_income),
            'roi_percentage': float(self.roi_percentage),
            'occupancy_rate': float(self.occupancy_rate),
            'vacancy_days': self.vacancy_days,
            'tenant_turnover_rate': float(self.tenant_turnover_rate),
            'maintenance_cost': float(self.maintenance_cost),
            'maintenance_requests_count': self.maintenance_requests_count,
            'average_repair_time': self.average_repair_time,
            'market_rent_estimate': float(self.market_rent_estimate) if self.market_rent_estimate else None,
            'property_appreciation': float(self.property_appreciation),
            'calculation_date': self.calculation_date.isoformat(),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'additional_metrics': self.additional_metrics,
        }


class Report(BaseModel):
    """Generated reports for properties and analytics"""
    REPORT_TYPE_CHOICES = [
        ('financial', _('مالي')),
        ('occupancy', _('إشغال')),
        ('maintenance', _('صيانة')),
        ('tenant', _('مستأجرين')),
        ('expense', _('مصاريف')),
        ('performance', _('أداء')),
        ('tax', _('ضريبي')),
        ('custom', _('مخصص')),
    ]
    
    STATUS_CHOICES = [
        ('generating', _('قيد الإنشاء')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
    ]

    # Report details
    title = models.CharField(_('عنوان التقرير'), max_length=200)
    report_type = models.CharField(_('نوع التقرير'), max_length=20, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='generating')
    
    # Scope
    properties = models.ManyToManyField(Property, related_name='reports', verbose_name=_('العقارات'))
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='generated_reports', verbose_name=_('أنشأه'))
    
    # Time period
    period_start = models.DateField(_('بداية الفترة'))
    period_end = models.DateField(_('نهاية الفترة'))
    
    # Report data
    report_data = models.JSONField(_('بيانات التقرير'), default=dict)
    summary = models.TextField(_('ملخص'), blank=True)
    
    # Files
    pdf_file = models.FileField(_('ملف PDF'), upload_to='reports/%Y/%m/', null=True, blank=True)
    excel_file = models.FileField(_('ملف Excel'), upload_to='reports/%Y/%m/', null=True, blank=True)
    
    # Generation details
    generation_time = models.DurationField(_('وقت الإنشاء'), null=True, blank=True)
    error_message = models.TextField(_('رسالة الخطأ'), blank=True)

    class Meta:
        verbose_name = _('تقرير')
        verbose_name_plural = _('التقارير')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['generated_by', '-created_at']),
            models.Index(fields=['period_start', 'period_end']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

    def to_dict(self):
        """Return dictionary representation for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'report_type_display': self.get_report_type_display(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'properties_count': self.properties.count(),
            'pdf_file': self.pdf_file.url if self.pdf_file else None,
            'excel_file': self.excel_file.url if self.excel_file else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }