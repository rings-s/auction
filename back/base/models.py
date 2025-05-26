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
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
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
    
    """Auction model with integrated auction types"""
    AUCTION_TYPES = [
        ('public', _('عام')),
        ('private', _('خاص')),
        ('sealed', _('مغلق')),
        ('dutch', _('هولندي')),
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
    auto_extend_minutes = models.PositiveIntegerField(_('تمديد تلقائي (دقائق)'), default=0)

    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)
    
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    bid_count = models.PositiveIntegerField(_('عدد المزايدات'), default=0)
    registered_bidders = models.PositiveIntegerField(_('المزايدين المسجلين'), default=0)

    media = GenericRelation(Media, related_query_name='auction')

    class Meta:
        verbose_name = _('مزاد')
        verbose_name_plural = _('المزادات')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['related_property']),
        ]

    @property
    def registered_bidders_count(self):
        """Returns the number of users registered for this auction."""
        return self.registered_users.count()

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
        unique_slug = original_slug
        counter = 1
        
        while Auction.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f"{original_slug}-{counter}"
            counter += 1
        
        return unique_slug

    @property
    def time_remaining(self):
        """Calculate time remaining until auction end"""
        if not self.end_date or self.end_date <= timezone.now():
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
        now = timezone.now()
        return (
            self.status == 'live' and 
            self.start_date <= now and 
            self.end_date > now and 
            self.is_published
        )

    def can_accept_bids(self):
        """Check if auction can accept new bids"""
        return self.is_active() and not self.is_deleted

    def increment_view_count(self):
        """Increment view count efficiently"""
        Auction.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])
        return self.view_count

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
                'count': self.bid_count,
            },
            'time_remaining': self.time_remaining,
            'is_active': self.is_active(),
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