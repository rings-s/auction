from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from django.db.models import Max, Sum
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
import uuid
import logging

# Set up logging for debugging
logger = logging.getLogger(__name__)

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        logger.debug(f"حفظ {self.__class__.__name__} مع المعرف: {self.pk}")
        super().save(*args, **kwargs)

class Property(BaseModel):
    """
    Property model representing real estate listings with streamlined
    but comprehensive features for effective property management
    """
    PROPERTY_TYPES = [
        ('land', _('أرض')),
        ('apartment', _('شقة')),
        ('villa', _('فيلا')),
        ('commercial', _('تجاري')),
        ('building', _('مبنى')),
        ('farm', _('مزرعة')),
        ('industrial', _('صناعي')),
        ('office', _('مكتب')),
        ('retail', _('محل تجاري')),
        ('mixed_use', _('متعدد الاستخدامات')),
    ]

    PROPERTY_STATUS = [
        ('draft', _('مسودة')),
        ('pending_approval', _('في انتظار الموافقة')),
        ('active', _('نشط')),
        ('under_contract', _('تحت التعاقد')),
        ('sold', _('مباع')),
        ('inactive', _('غير نشط')),
        ('rejected', _('مرفوض')),
    ]

    PROPERTY_CONDITION = [
        ('excellent', _('ممتاز')),
        ('very_good', _('جيد جدا')),
        ('good', _('جيد')),
        ('fair', _('مقبول')),
        ('poor', _('سيئ')),
        ('under_construction', _('تحت الإنشاء')),
        ('new', _('جديد')),
    ]

    FACING_DIRECTIONS = [
        ('north', _('شمال')),
        ('east', _('شرق')),
        ('south', _('جنوب')),
        ('west', _('غرب')),
        ('northeast', _('شمال شرق')),
        ('southeast', _('جنوب شرق')),
        ('southwest', _('جنوب غرب')),
        ('northwest', _('شمال غرب')),
    ]

    USAGE_TYPES = [
        ('residential', _('سكني')),
        ('commercial', _('تجاري')),
        ('mixed', _('مختلط')),
        ('industrial', _('صناعي')),
        ('agricultural', _('زراعي')),
    ]

    # Basic information
    property_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم العقار'))
    title = models.CharField(max_length=255, verbose_name=_('عنوان العقار'))
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name=_('الرابط المختصر'))
    property_type = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPES,
        verbose_name=_('نوع العقار')
    )
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف تفصيلي'))
    condition = models.CharField(
        max_length=50,
        choices=PROPERTY_CONDITION,
        default='good',
        verbose_name=_('حالة العقار')
    )

    # Ownership details
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_properties',
        verbose_name=_('المالك')
    )
    status = models.CharField(
        max_length=20,
        choices=PROPERTY_STATUS,
        default='draft',
        verbose_name=_('حالة العقار')
    )
    status_history = models.JSONField(default=list, blank=True, null=True, verbose_name=_('سجل حالات العقار'))
    deed_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('رقم الصك'))
    deed_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الصك'))

    # Location information
    address = models.CharField(max_length=255, verbose_name=_('العنوان'))
    city = models.CharField(max_length=100, verbose_name=_('المدينة'))
    district = models.CharField(max_length=100, verbose_name=_('الحي'))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('الرمز البريدي'))
    country = models.CharField(max_length=100, default='Saudi Arabia', verbose_name=_('الدولة'))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_('خط العرض'))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_('خط الطول'))
    location = gis_models.PointField(geography=True, blank=True, null=True, verbose_name=_('الموقع على الخريطة'))
    facing_direction = models.CharField(
        max_length=20,
        choices=FACING_DIRECTIONS,
        blank=True,
        null=True,
        verbose_name=_('اتجاه الواجهة')
    )
    street_details = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('تفاصيل الشوارع'))

    # Property specifications
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('مساحة العقار'))
    built_up_area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('المساحة المبنية'))
    bedrooms = models.PositiveIntegerField(default=0, verbose_name=_('عدد غرف النوم'))
    bathrooms = models.PositiveIntegerField(default=0, verbose_name=_('عدد الحمامات'))
    rooms = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('تفاصيل الغرف'))
    floor_number = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('رقم الطابق'))
    total_floors = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('إجمالي الطوابق'))
    year_built = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('سنة البناء'))

    # Balconies and outdoor spaces
    outdoor_spaces = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('المساحات الخارجية'))

    # Financial details
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('القيمة التقديرية'))
    asking_price = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, verbose_name=_('السعر المطلوب'))
    price_per_sqm = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, verbose_name=_('السعر لكل متر مربع'))
    rental_details = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('تفاصيل الإيجار'))

    # Parking details
    parking = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('تفاصيل مواقف السيارات'))

    # Media files
    images = models.JSONField(default=list, blank=True, null=True, verbose_name=_('صور العقار'))
    videos = models.JSONField(default=list, blank=True, null=True, verbose_name=_('فيديوهات العقار'))
    virtual_tours = models.JSONField(default=list, blank=True, null=True, verbose_name=_('جولات افتراضية'))
    documents = models.JSONField(default=list, blank=True, null=True, verbose_name=_('مستندات العقار'))
    floor_plans = models.JSONField(default=list, blank=True, null=True, verbose_name=_('مخططات الطوابق'))

    # Features and amenities
    features = models.JSONField(default=list, blank=True, null=True, verbose_name=_('المميزات'))
    amenities = models.JSONField(default=list, blank=True, null=True, verbose_name=_('المرافق'))

    # Building services and infrastructure
    building_services = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('خدمات المبنى'))
    infrastructure = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('البنية التحتية'))

    # Current and potential usage
    current_usage = models.CharField(
        max_length=30,
        choices=USAGE_TYPES,
        blank=True,
        null=True,
        verbose_name=_('الاستخدام الحالي')
    )
    optimal_usage = models.CharField(
        max_length=30,
        choices=USAGE_TYPES,
        blank=True,
        null=True,
        verbose_name=_('الاستخدام الأمثل')
    )

    # Surrounding landmarks and services
    surroundings = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('المحيط'))

    # Verification and approvals
    is_verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_properties',
        verbose_name=_('تم التحقق بواسطة')
    )
    verification_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التحقق'))
    verification_details = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('تفاصيل التحقق'))

    # Auction and visibility settings
    is_featured = models.BooleanField(default=False, verbose_name=_('مميز'))
    is_published = models.BooleanField(default=False, verbose_name=_('منشور'))
    publish_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ النشر'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد المشاهدات'))

    # Administrative
    reference_ids = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('أرقام مرجعية'))

    class Meta:
        db_table = 'properties'
        verbose_name = _('عقار')
        verbose_name_plural = _('العقارات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_type']),
            models.Index(fields=['city', 'district']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured', 'is_published']),
            models.Index(fields=['year_built']),
            models.Index(fields=['area']),
            models.Index(fields=['estimated_value']),
            models.Index(fields=['bedrooms', 'bathrooms']),
        ]

    def __str__(self):
        return f"{self.property_number} - {self.title}"

    def save(self, *args, **kwargs):
        try:
            # Create Point object from lat/long if provided
            if self.latitude and self.longitude and not self.location:
                self.location = Point(float(self.longitude), float(self.latitude), srid=4326)

            # Set publish date when published
            if self.is_published and not self.publish_date:
                self.publish_date = timezone.now()

            # Generate slug if not provided
            if not self.slug:
                from django.utils.text import slugify
                import random
                import string
                base_slug = slugify(self.title)
                random_str = ''.join(random.choices(string.digits, k=6))
                self.slug = f"{base_slug}-{random_str}"

            # Calculate price per sqm if not provided
            if self.estimated_value and self.area and not self.price_per_sqm:
                self.price_per_sqm = self.estimated_value / self.area

            # Add status history entry if status has changed
            if self.pk:
                old_instance = Property.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    if not self.status_history:
                        self.status_history = []

                    self.status_history.append({
                        'status': self.status,
                        'previous_status': old_instance.status,
                        'date': timezone.now().isoformat(),
                        'user': getattr(kwargs.get('user', None), 'id', None)
                    })

            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"خطأ في حفظ العقار {self.property_number}: {str(e)}")
            raise

    @property
    def main_image_url(self):
        """Get the main image URL from the images JSONField"""
        if not self.images:
            return None

        for img in self.images:
            if img.get('is_primary'):
                return img.get('path')

        # Return first image if no primary is set
        return self.images[0].get('path') if self.images else None

    @property
    def has_auction(self):
        """Check if property has an active auction"""
        return self.auctions.filter(status__in=['draft', 'pending', 'active']).exists()

    def recommended_properties(self, limit=5):
        """Find similar/recommended properties based on core attributes"""
        return Property.objects.filter(
            property_type=self.property_type,
            city=self.city,
            is_published=True
        ).exclude(pk=self.pk).filter(
            area__range=(self.area * 0.8, self.area * 1.2)
        ).order_by('-is_featured', '-views_count')[:limit]


class Auction(BaseModel):
    """Auction model for property auctions"""
    AUCTION_STATUS = [
        ('draft', _('مسودة')),
        ('pending', _('قيد الانتظار')),
        ('active', _('مفتوح')),
        ('extended', _('ممدد')),
        ('closed', _('مغلق')),
        ('sold', _('مُباع')),
        ('cancelled', _('ملغي')),
    ]

    AUCTION_TYPES = [
        ('public', _('عام')),
        ('private', _('خاص')),
        ('online', _('إلكتروني')),
        ('onsite', _('حضوري')),
        ('hybrid', _('مختلط')),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('المعرف العالمي'))
    related_property = models.ForeignKey(
        'Property',
        on_delete=models.PROTECT,
        related_name='auctions',
        verbose_name=_('العقار')
    )
    title = models.CharField(max_length=255, verbose_name=_('عنوان المزاد'))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('الرابط المختصر'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف المزاد'))

    # Auction configuration
    auction_type = models.CharField(
        max_length=50,
        choices=AUCTION_TYPES,
        default='online',
        verbose_name=_('نوع المزاد')
    )
    status = models.CharField(
        max_length=20,
        choices=AUCTION_STATUS,
        default='draft',
        verbose_name=_('حالة المزاد')
    )

    # Ownership and management
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_auctions',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    auctioneer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='managed_auctions',
        verbose_name=_('منظم المزاد')
    )

    # Dates and duration
    start_date = models.DateTimeField(verbose_name=_('تاريخ بدء المزاد'))
    end_date = models.DateTimeField(verbose_name=_('تاريخ انتهاء المزاد'))
    auto_extend = models.BooleanField(default=True, verbose_name=_('تمديد تلقائي'))
    extension_minutes = models.PositiveIntegerField(default=10, verbose_name=_('دقائق التمديد'))

    # Pricing and bidding rules
    starting_price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('سعر البدء'))
    reserve_price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('السعر الاحتياطي'))
    min_bid_increment = models.DecimalField(max_digits=14, decimal_places=2, default=100, verbose_name=_('الحد الأدنى للزيادة'))
    deposit_amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, verbose_name=_('مبلغ التأمين'))
    deposit_required = models.BooleanField(default=False, verbose_name=_('مطلوب تأمين'))

    # Commission and fees
    buyer_premium_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, verbose_name=_('نسبة عمولة المشتري'))
    seller_commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=2.5, verbose_name=_('نسبة عمولة البائع'))

    # Results
    current_bid = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, verbose_name=_('المزايدة الحالية'))
    winning_bid = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, verbose_name=_('المزايدة الفائزة'))
    winning_bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='won_auctions',
        verbose_name=_('المزايد الفائز')
    )
    end_reason = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('سبب الإنهاء'))

    # Location for onsite auctions (replaced PointField with standard fields)
    location_address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('عنوان الموقع'))
    location_latitude = models.FloatField(blank=True, null=True, verbose_name=_('خط عرض الموقع'))
    location_longitude = models.FloatField(blank=True, null=True, verbose_name=_('خط طول الموقع'))
    location_details = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('تفاصيل الموقع'))

    # Participation requirements
    terms_conditions = models.TextField(blank=True, null=True, verbose_name=_('الشروط والأحكام'))
    participation_requirements = models.TextField(blank=True, null=True, verbose_name=_('متطلبات المشاركة'))

    # Media
    images = models.JSONField(default=list, blank=True, null=True, verbose_name=_('صور المزاد'))
    videos = models.JSONField(default=list, blank=True, null=True, verbose_name=_('فيديوهات المزاد'))
    documents = models.JSONField(default=list, blank=True, null=True, verbose_name=_('مستندات المزاد'))

    # Private auction settings
    is_private = models.BooleanField(default=False, verbose_name=_('مزاد خاص'))
    invited_bidders = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='invited_auctions',
        blank=True,
        verbose_name=_('المزايدين المدعوين')
    )

    # Visibility and promotion
    is_featured = models.BooleanField(default=False, verbose_name=_('مزاد مميز'))
    is_published = models.BooleanField(default=False, verbose_name=_('منشور'))
    publish_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ النشر'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('عدد المشاهدات'))

    class Meta:
        db_table = 'auctions'
        verbose_name = _('مزاد')
        verbose_name_plural = _('المزادات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['is_featured', 'is_published']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Initialize current bid with starting price if not set
        if self.current_bid is None:
            self.current_bid = self.starting_price

        # Set publish date if published
        if self.is_published and not self.publish_date:
            self.publish_date = timezone.now()

        # Store location details in JSON field if coordinates are provided
        if self.location_latitude is not None and self.location_longitude is not None:
            if not self.location_details:
                self.location_details = {}
            self.location_details.update({
                'latitude': float(self.location_latitude),
                'longitude': float(self.location_longitude),
                'updated_at': timezone.now().isoformat()
            })

        super().save(*args, **kwargs)

    @property
    def highest_bid(self):
        """Get the highest bid for this auction"""
        return self.bids.aggregate(Max('bid_amount'))['bid_amount__max'] or self.starting_price

    @property
    def bid_count(self):
        """Get the number of bids for this auction"""
        return self.bids.count()

    @property
    def unique_bidders_count(self):
        """Get the number of unique bidders for this auction"""
        return self.bids.values('bidder').distinct().count()

    @property
    def time_remaining(self):
        """Get the remaining time for the auction in seconds"""
        if self.status != 'active':
            return 0

        now = timezone.now()
        if now > self.end_date:
            return 0

        return (self.end_date - now).total_seconds()

    @property
    def is_active(self):
        """Check if auction is currently active"""
        if self.status != 'active':
            return False

        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def featured_image_url(self):
        """Get the featured image URL"""
        if not self.images:
            return self.related_property.main_image_url

        for img in self.images:
            if img.get('is_featured'):
                return img.get('path')

        # Return first image if no featured image
        return self.images[0].get('path') if self.images else self.related_property.main_image_url

    @property
    def location_coordinates(self):
        """Compatibility method to return coordinates as a dictionary"""
        if self.location_latitude is not None and self.location_longitude is not None:
            return {
                'latitude': self.location_latitude,
                'longitude': self.location_longitude
            }
        return None

class Document(BaseModel):
    """Model for property and auction related documents"""
    DOCUMENT_TYPES = [
        ('deed', _('صك ملكية')),
        ('inspection', _('تقرير فحص')),
        ('appraisal', _('تقرير تقييم')),
        ('coastal_assessment', _('تقييم ساحلي')),
        ('legal', _('مستند قانوني')),
        ('contract', _('عقد')),
        ('identity', _('إثبات هوية')),
        ('financial', _('مستند مالي')),
        ('other', _('أخرى')),
    ]

    VERIFICATION_STATUS = [
        ('pending', _('معلق')),
        ('verified', _('تم التحقق')),
        ('rejected', _('مرفوض')),
    ]

    document_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم المستند'))
    title = models.CharField(max_length=255, verbose_name=_('عنوان المستند'))
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, verbose_name=_('نوع المستند'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف المستند'))

    # Related models - renamed 'property' to 'related_property'
    related_property = models.ForeignKey(
        'Property',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='property_documents',
        verbose_name=_('العقار المرتبط')
    )
    auction = models.ForeignKey(
        'Auction',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='auction_documents',
        verbose_name=_('المزاد المرتبط')
    )
    contract = models.ForeignKey(
        'Contract',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='contract_documents',
        verbose_name=_('العقد المرتبط')
    )

    # Document files as JSONField for API flexibility
    files = models.JSONField(default=list, blank=True, null=True, verbose_name=_('ملفات المستند'))

    # Ownership and verification
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='uploaded_documents',
        verbose_name=_('تم الرفع بواسطة')
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending',
        verbose_name=_('حالة التحقق')
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_documents',
        verbose_name=_('تم التحقق بواسطة')
    )
    verification_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التحقق'))
    verification_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات التحقق'))

    # Additional metadata as JSONField
    metadata = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('بيانات وصفية'))

    # Expiry and validity
    issue_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الإصدار'))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الانتهاء'))

    class Meta:
        db_table = 'documents'
        verbose_name = _('مستند')
        verbose_name_plural = _('المستندات')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_document_type_display()}: {self.title}"

    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    @property
    def main_file_url(self):
        """Get the main file URL"""
        if not self.files:
            return None
        return self.files[0].get('path') if self.files else None



class Bid(BaseModel):
    """Bid model for auction bids"""
    BID_STATUS = [
        ('pending', _('معلق')),
        ('accepted', _('مقبول')),
        ('rejected', _('مرفوض')),
        ('winning', _('فائز')),
        ('outbid', _('تم تجاوزه')),
        ('cancelled', _('ملغي')),
    ]

    auction = models.ForeignKey(
        'Auction',
        on_delete=models.CASCADE,
        related_name='bids',
        verbose_name=_('المزاد')
    )
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bids',
        verbose_name=_('المزايد')
    )
    bid_amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('قيمة العطاء'))
    bid_time = models.DateTimeField(auto_now_add=True, verbose_name=_('وقت تقديم العطاء'))
    status = models.CharField(
        max_length=20,
        choices=BID_STATUS,
        default='pending',
        verbose_name=_('حالة العطاء')
    )

    # For auto bidding
    max_bid_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True, null=True,
        verbose_name=_('الحد الأقصى للمزايدة التلقائية')
    )
    is_auto_bid = models.BooleanField(default=False, verbose_name=_('مزايدة تلقائية'))

    # For bid tracking
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('عنوان IP'))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_('معلومات المتصفح'))
    device_info = models.JSONField(default=dict, blank=True, null=True, verbose_name=_('معلومات الجهاز'))

    # Admin notes
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))

    class Meta:
        db_table = 'bids'
        verbose_name = _('عطاء')
        verbose_name_plural = _('العطاءات')
        ordering = ['-bid_amount', 'bid_time']
        indexes = [
            models.Index(fields=['auction', 'bid_amount']),
            models.Index(fields=['auction', 'bidder']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.bid_amount} من {self.bidder} للمزاد {self.auction.title}"

    def save(self, *args, **kwargs):
        # Check if this is the highest bid and update auction
        highest_bid = self.auction.highest_bid

        if self.bid_amount > highest_bid and self.status in ['pending', 'accepted']:
            self.auction.current_bid = self.bid_amount
            self.auction.save(update_fields=['current_bid', 'updated_at'])

            # Mark previous winning bid as outbid
            previous_winning = Bid.objects.filter(
                auction=self.auction,
                status='winning'
            ).first()

            if previous_winning:
                previous_winning.status = 'outbid'
                previous_winning.save(update_fields=['status', 'updated_at'])

        super().save(*args, **kwargs)


class Contract(BaseModel):
    """Contract model for auction sales contracts"""
    CONTRACT_STATUS = [
        ('draft', _('مسودة')),
        ('pending_review', _('قيد المراجعة')),
        ('pending_buyer', _('بانتظار المشتري')),
        ('pending_seller', _('بانتظار البائع')),
        ('pending_payment', _('بانتظار الدفع')),
        ('signed', _('موقع')),
        ('active', _('نشط')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغى')),
        ('disputed', _('متنازع عليه')),
    ]

    PAYMENT_METHODS = [
        ('bank_transfer', _('تحويل بنكي')),
        ('cash', _('نقدي')),
        ('check', _('شيك')),
        ('installment', _('تقسيط')),
        ('escrow', _('ضمان')),
    ]

    contract_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم العقد'))
    title = models.CharField(max_length=255, verbose_name=_('عنوان العقد'))

    # Related models - renamed 'property' to 'related_property'
    auction = models.OneToOneField(
        'Auction',
        on_delete=models.PROTECT,
        related_name='contract',
        verbose_name=_('المزاد')
    )
    related_property = models.ForeignKey(
        'Property',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name=_('العقار')
    )

    # Parties
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='buyer_contracts',
        verbose_name=_('المشتري')
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='seller_contracts',
        verbose_name=_('البائع')
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='agent_contracts',
        verbose_name=_('الوكيل العقاري')
    )

    # Contract details
    status = models.CharField(
        max_length=20,
        choices=CONTRACT_STATUS,
        default='draft',
        verbose_name=_('حالة العقد')
    )
    contract_date = models.DateField(verbose_name=_('تاريخ العقد'))
    effective_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ السريان'))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الانتهاء'))

    # Financial details
    contract_amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('قيمة العقد'))
    deposit_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('قيمة العربون'))
    commission_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('قيمة العمولة'))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('قيمة الضريبة'))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('المبلغ الإجمالي'))
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, verbose_name=_('طريقة الدفع'))
    payment_terms = models.TextField(verbose_name=_('شروط الدفع'))

    # Documents and files
    files = models.JSONField(default=list, blank=True, null=True, verbose_name=_('ملفات العقد'))

    # Contract content
    terms_conditions = models.TextField(blank=True, null=True, verbose_name=_('الشروط والأحكام'))
    special_conditions = models.TextField(blank=True, null=True, verbose_name=_('شروط خاصة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))

    # Signatures and verification
    buyer_signed = models.BooleanField(default=False, verbose_name=_('وقّع المشتري'))
    seller_signed = models.BooleanField(default=False, verbose_name=_('وقّع البائع'))
    agent_signed = models.BooleanField(default=False, verbose_name=_('وقّع الوكيل'))
    buyer_signature_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ توقيع المشتري'))
    seller_signature_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ توقيع البائع'))
    agent_signature_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ توقيع الوكيل'))

    # Verification
    is_verified = models.BooleanField(default=False, verbose_name=_('تم التحقق'))
    verification_authority = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('جهة التوثيق'))
    verification_date = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التوثيق'))

    class Meta:
        db_table = 'contracts'
        verbose_name = _('عقد')
        verbose_name_plural = _('العقود')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['contract_date']),
            models.Index(fields=['buyer', 'seller']),
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    def save(self, *args, **kwargs):
        # Calculate total amount if not set
        if not self.total_amount:
            self.total_amount = (
                self.contract_amount +
                self.commission_amount +
                self.tax_amount
            )

        # Mark as signed if all parties have signed
        if self.buyer_signed and self.seller_signed:
            if not self.agent or self.agent_signed:
                if self.status in ['pending_buyer', 'pending_seller']:
                    self.status = 'signed'

        super().save(*args, **kwargs)

    @property
    def is_fully_signed(self):
        """Check if contract is fully signed"""
        if not self.buyer_signed or not self.seller_signed:
            return False

        if self.agent and not self.agent_signed:
            return False

        return True

    @property
    def main_file_url(self):
        """Get the main contract file URL"""
        if not self.files:
            return None

        for file in self.files:
            if file.get('file_type') == 'contract':
                return file.get('path')

        # Return first file if no contract file
        return self.files[0].get('path') if self.files else None


class Payment(BaseModel):
    """Payment model for contract payments"""
    PAYMENT_STATUS = [
        ('pending', _('معلق')),
        ('processing', _('قيد المعالجة')),
        ('completed', _('مكتمل')),
        ('failed', _('فاشل')),
        ('refunded', _('مسترد')),
        ('cancelled', _('ملغى')),
        ('disputed', _('متنازع عليه')),
    ]

    PAYMENT_TYPES = [
        ('deposit', _('عربون')),
        ('installment', _('قسط')),
        ('full_payment', _('دفعة كاملة')),
        ('commission', _('عمولة')),
        ('tax', _('ضريبة')),
        ('fee', _('رسوم')),
    ]

    PAYMENT_METHODS = [
        ('bank_transfer', _('تحويل بنكي')),
        ('cash', _('نقدي')),
        ('check', _('شيك')),
        ('credit_card', _('بطاقة ائتمان')),
        ('online', _('دفع إلكتروني')),
    ]

    payment_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الدفعة'))

    # Related models
    contract = models.ForeignKey(
        'Contract',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name=_('العقد')
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments_made',
        verbose_name=_('الدافع')
    )
    payee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments_received',
        verbose_name=_('المستلم')
    )

    # Payment details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name=_('نوع الدفعة'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name=_('طريقة الدفع'))
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('المبلغ'))
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_('العملة'))
    payment_date = models.DateTimeField(verbose_name=_('تاريخ الدفع'))
    due_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الاستحقاق'))

    # Status
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name=_('حالة الدفعة')
    )
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التأكيد'))
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='confirmed_payments',
        verbose_name=_('تم التأكيد بواسطة')
    )

    # Payment details
    transaction_reference = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('مرجع المعاملة'))
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اسم البنك'))
    account_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اسم الحساب'))
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('رقم الحساب'))
    check_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('رقم الشيك'))

    # Receipt and files
    files = models.JSONField(default=list, blank=True, null=True, verbose_name=_('ملفات الدفعة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))

    class Meta:
        db_table = 'payments'
        verbose_name = _('دفعة')
        verbose_name_plural = _('الدفعات')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['contract', 'payment_type']),
        ]

    def __str__(self):
        return f"{self.payment_number} - {self.amount} {self.currency}"

    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.status == 'pending' and self.due_date:
            return self.due_date < timezone.now().date()
        return False

    @property
    def receipt_url(self):
        """Get receipt file URL"""
        if not self.files:
            return None

        for file in self.files:
            if file.get('file_type') == 'receipt':
                return file.get('path')

        return self.files[0].get('path') if self.files else None


class Transaction(BaseModel):
    """Transaction model for financial transactions"""
    TRANSACTION_TYPES = [
        ('deposit', _('عربون')),
        ('payment', _('دفعة')),
        ('refund', _('استرداد')),
        ('commission', _('عمولة')),
        ('fee', _('رسوم')),
        ('tax', _('ضريبة')),
        ('withdrawal', _('سحب')),
        ('transfer', _('تحويل')),
    ]

    TRANSACTION_STATUS = [
        ('pending', _('معلق')),
        ('processing', _('قيد المعالجة')),
        ('completed', _('مكتمل')),
        ('failed', _('فاشل')),
        ('cancelled', _('ملغى')),
        ('disputed', _('متنازع عليه')),
    ]

    transaction_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم المعاملة'))
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name=_('نوع المعاملة'))
    description = models.TextField(verbose_name=_('وصف المعاملة'))

    # Financial details
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_('المبلغ'))
    currency = models.CharField(max_length=3, default='SAR', verbose_name=_('العملة'))
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1.0, verbose_name=_('سعر الصرف'))
    fee_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('مبلغ الرسوم'))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name=_('مبلغ الضريبة'))

    # Users involved
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='outgoing_transactions',
        verbose_name=_('من المستخدم')
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='incoming_transactions',
        verbose_name=_('إلى المستخدم')
    )

    # Related models
    payment = models.ForeignKey(
        'Payment',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions',
        verbose_name=_('الدفعة المرتبطة')
    )
    auction = models.ForeignKey(
        'Auction',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions',
        verbose_name=_('المزاد المرتبط')
    )
    contract = models.ForeignKey(
        'Contract',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions',
        verbose_name=_('العقد المرتبط')
    )

    # Transaction details
    transaction_date = models.DateTimeField(verbose_name=_('تاريخ المعاملة'))
    status = models.CharField(
        max_length=20,
        choices=TRANSACTION_STATUS,
        default='pending',
        verbose_name=_('حالة المعاملة')
    )
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('المرجع'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))

    # Transaction processing
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ المعالجة'))
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='processed_transactions',
        verbose_name=_('تمت المعالجة بواسطة')
    )

    class Meta:
        db_table = 'transactions'
        verbose_name = _('معاملة مالية')
        verbose_name_plural = _('معاملات مالية')
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['from_user', 'to_user']),
        ]

    def __str__(self):
        return f"{self.transaction_number} - {self.amount} {self.currency}"

    @property
    def total_amount(self):
        """Calculate total amount including fees and taxes"""
        return self.amount + self.fee_amount + self.tax_amount


class MessageThread(BaseModel):
    """Message thread model for organizing messages into conversations"""
    THREAD_TYPES = [
        ('inquiry', _('استفسار')),
        ('negotiation', _('تفاوض')),
        ('support', _('دعم')),
        ('notification', _('إشعار')),
        ('private', _('خاص')),
    ]

    subject = models.CharField(max_length=255, verbose_name=_('الموضوع'))
    thread_type = models.CharField(
        max_length=20,
        choices=THREAD_TYPES,
        default='inquiry',
        verbose_name=_('نوع المحادثة')
    )

    # Related models
    related_property = models.ForeignKey(
        'Property',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='message_threads',
        verbose_name=_('العقار المرتبط')
    )
    related_auction = models.ForeignKey(
        'Auction',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='message_threads',
        verbose_name=_('المزاد المرتبط')
    )
    related_contract = models.ForeignKey(
        'Contract',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='message_threads',
        verbose_name=_('العقد المرتبط')
    )

    # Participants
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ThreadParticipant',
        related_name='message_threads',
        verbose_name=_('المشاركون')
    )

    # Thread status
    is_active = models.BooleanField(default=True, verbose_name=_('نشطة'))
    is_resolved = models.BooleanField(default=False, verbose_name=_('تم الحل'))
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الحل'))
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resolved_threads',
        verbose_name=_('تم الحل بواسطة')
    )

    # Activity tracking
    last_message_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ آخر رسالة'))

    class Meta:
        db_table = 'message_threads'
        verbose_name = _('محادثة')
        verbose_name_plural = _('محادثات')
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['thread_type']),
            models.Index(fields=['is_active', 'is_resolved']),
        ]

    def __str__(self):
        return f"{self.subject} ({self.get_thread_type_display()})"

    @property
    def message_count(self):
        """Get number of messages in thread"""
        return self.messages.count()

    @property
    def unread_count(self):
        """Get number of unread messages in thread"""
        return self.messages.filter(status__in=['sent', 'delivered']).count()

    @property
    def last_message(self):
        """Get last message in thread"""
        return self.messages.order_by('-sent_at').first()


class Message(BaseModel):
    """Message model for communication between users"""
    MESSAGE_TYPES = [
        ('inquiry', _('استفسار')),
        ('offer', _('عرض')),
        ('negotiation', _('تفاوض')),
        ('notification', _('إشعار')),
        ('update', _('تحديث')),
        ('support', _('دعم')),
    ]

    MESSAGE_STATUS = [
        ('sent', _('مرسلة')),
        ('delivered', _('تم التسليم')),
        ('read', _('مقروءة')),
        ('replied', _('تم الرد')),
        ('archived', _('مؤرشفة')),
    ]

    thread = models.ForeignKey(
        'MessageThread',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('المحادثة')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('المرسل')
    )
    subject = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('الموضوع'))
    content = models.TextField(verbose_name=_('المحتوى'))
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='inquiry',
        verbose_name=_('نوع الرسالة')
    )
    status = models.CharField(
        max_length=20,
        choices=MESSAGE_STATUS,
        default='sent',
        verbose_name=_('حالة الرسالة')
    )

    # Read receipts
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإرسال'))
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ التسليم'))
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ القراءة'))

    # Related objects
    related_property = models.ForeignKey(
        'Property',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messages',
        verbose_name=_('العقار المرتبط')
    )
    related_auction = models.ForeignKey(
        'Auction',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messages',
        verbose_name=_('المزاد المرتبط')
    )
    related_contract = models.ForeignKey(
        'Contract',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messages',
        verbose_name=_('العقد المرتبط')
    )

    # Nested messages
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='replies',
        verbose_name=_('الرسالة الأصلية')
    )

    # Attachments
    attachments = models.JSONField(default=list, blank=True, null=True, verbose_name=_('المرفقات'))

    # Flags
    is_system_message = models.BooleanField(default=False, verbose_name=_('رسالة نظام'))
    is_important = models.BooleanField(default=False, verbose_name=_('هامة'))

    class Meta:
        db_table = 'messages'
        verbose_name = _('رسالة')
        verbose_name_plural = _('الرسائل')
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['thread', 'sent_at']),
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['is_system_message']),
        ]

    def __str__(self):
        return f"{self.subject or 'رسالة'} من {self.sender}"

    @property
    def has_attachments(self):
        """Check if message has attachments"""
        return bool(self.attachments)


class ThreadParticipant(BaseModel):
    """Model for thread participants"""
    PARTICIPANT_ROLES = [
        ('owner', _('مالك')),
        ('member', _('عضو')),
        ('observer', _('مراقب')),
        ('support', _('دعم')),
        ('admin', _('مدير')),
    ]

    thread = models.ForeignKey(
        'MessageThread',
        on_delete=models.CASCADE,
        related_name='thread_participants',
        verbose_name=_('المحادثة')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='thread_memberships',
        verbose_name=_('المستخدم')
    )
    role = models.CharField(
        max_length=20,
        choices=PARTICIPANT_ROLES,
        default='member',
        verbose_name=_('الدور')
    )

    # Participant status
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    is_muted = models.BooleanField(default=False, verbose_name=_('صامت'))
    last_read_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ آخر قراءة'))

    class Meta:
        db_table = 'thread_participants'
        verbose_name = _('مشارك في محادثة')
        verbose_name_plural = _('مشاركون في محادثة')
        unique_together = ['thread', 'user']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user} في محادثة {self.thread.subject}"

    @property
    def has_unread_messages(self):
        """Check if participant has unread messages"""
        if not self.last_read_at:
            return self.thread.messages.exclude(sender=self.user).exists()

        return self.thread.messages.filter(
            sent_at__gt=self.last_read_at
        ).exclude(sender=self.user).exists()

    @property
    def unread_count(self):
        """Count unread messages for this participant"""
        if not self.last_read_at:
            return self.thread.messages.exclude(sender=self.user).count()

        return self.thread.messages.filter(
            sent_at__gt=self.last_read_at
        ).exclude(sender=self.user).count()


class Notification(BaseModel):
    """Notification model for system notifications"""
    NOTIFICATION_TYPES = [
        ('auction_start', _('بدء مزاد')),
        ('auction_end', _('انتهاء مزاد')),
        ('new_bid', _('عطاء جديد')),
        ('outbid', _('تم تجاوز العطاء')),
        ('winning_bid', _('عطاء فائز')),
        ('auction_status', _('تغيير حالة المزاد')),
        ('property_listed', _('إدراج عقار جديد')),
        ('property_status', _('تغيير حالة العقار')),
        ('payment', _('دفعة جديدة')),
        ('contract_status', _('تغيير حالة العقد')),
        ('message', _('رسالة جديدة')),
        ('system', _('إشعار نظام')),
    ]

    CHANNELS = [
        ('app', _('تطبيق')),
        ('email', _('بريد إلكتروني')),
        ('sms', _('رسالة نصية')),
        ('push', _('إشعار فوري')),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('المستلم')
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        verbose_name=_('نوع الإشعار')
    )
    title = models.CharField(max_length=255, verbose_name=_('العنوان'))
    content = models.TextField(verbose_name=_('المحتوى'))
    channel = models.CharField(
        max_length=20,
        choices=CHANNELS,
        default='app',
        verbose_name=_('قناة الإشعار')
    )

    # Related entities
    related_property = models.ForeignKey(
        'Property',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications',
        verbose_name=_('العقار المرتبط')
    )
    related_auction = models.ForeignKey(
        'Auction',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications',
        verbose_name=_('المزاد المرتبط')
    )
    related_bid = models.ForeignKey(
        'Bid',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications',
        verbose_name=_('العطاء المرتبط')
    )
    related_contract = models.ForeignKey(
        'Contract',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications',
        verbose_name=_('العقد المرتبط')
    )
    related_payment = models.ForeignKey(
        'Payment',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications',
        verbose_name=_('الدفعة المرتبطة')
    )
    related_message = models.ForeignKey(
        'Message',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications',
        verbose_name=_('الرسالة المرتبطة')
    )

    # Status
    is_read = models.BooleanField(default=False, verbose_name=_('تمت القراءة'))
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ القراءة'))
    is_sent = models.BooleanField(default=False, verbose_name=_('تم الإرسال'))
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name=_('تاريخ الإرسال'))

    # Display properties
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الأيقونة'))
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('اللون'))
    action_url = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('رابط العمل'))

    class Meta:
        db_table = 'notifications'
        verbose_name = _('إشعار')
        verbose_name_plural = _('إشعارات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.title} لـ {self.recipient}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])



class PropertyView(models.Model):
    VIEW_TYPE_CHOICES = (
        ('OCEAN', _('إطلالة على المحيط')),  # Ocean View
        ('MOUNTAIN', _('إطلالة على الجبل')),  # Mountain View
        ('CITY', _('إطلالة على المدينة')),  # City View
        ('FOREST', _('إطلالة على الغابة')),  # Forest View
        ('LAKE', _('إطلالة على البحيرة')),  # Lake View
        ('CUSTOM', _('إطلالة مخصصة')),  # Custom View
    )

    auction = models.OneToOneField(
        'base.Auction',  # Adjust app name if different
        on_delete=models.CASCADE,
        related_name='property_view',
        verbose_name=_('المزاد')  # Auction
    )
    view_type = models.CharField(
        max_length=20,
        choices=VIEW_TYPE_CHOICES,
        verbose_name=_('نوع الإطلالة')  # View Type
    )
    size_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('المساحة (متر مربع)')  # Size (sqm)
    )
    location = models.CharField(
        max_length=255,
        verbose_name=_('الموقع')  # Location
    )
    address = models.TextField(
        verbose_name=_('العنوان')  # Address
    )
    elevation = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('الارتفاع')  # Elevation
    )
    view_direction = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('اتجاه الإطلالة')  # View Direction
    )
    legal_description = models.TextField(
        verbose_name=_('الوصف القانوني')  # Legal Description
    )
    condition = models.TextField(
        verbose_name=_('الحالة')  # Condition
    )
    historical_views = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('الإطلالات التاريخية')  # Historical Views
    )
    images = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('الصور')  # Images
    )

    class Meta:
        verbose_name = _('عرض العقار')  # Property View
        verbose_name_plural = _('عروض العقارات')  # Property Views
        indexes = [
            models.Index(fields=['view_type']),
            models.Index(fields=['location']),
        ]
        ordering = ['-id']

    def __str__(self):
        return f"{self.get_view_type_display()} في {self.location}"  # at {location}

    def clean(self):
        if self.size_sqm <= 0:
            raise ValidationError(_('يجب أن تكون المساحة أكبر من الصفر'))  # Size must be greater than zero
