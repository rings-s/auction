from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
import uuid, os, random
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class BaseModel(models.Model):
    is_deleted = models.BooleanField(_('محذوف'), default=False)
    deleted_at = models.DateTimeField(_('تاريخ الحذف'), null=True, blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

class Media(BaseModel):
    MEDIA_TYPES = [
        ('image', _('صورة')), ('document', _('مستند')),
        ('video', _('فيديو')), ('other', _('أخرى')),
    ]

    file = models.FileField(_('الملف'), upload_to='uploads/%Y/%m/%d/')
    name = models.CharField(_('الاسم'), max_length=255, blank=True)
    media_type = models.CharField(_('نوع الوسائط'), max_length=10, choices=MEDIA_TYPES, default='image')
    is_primary = models.BooleanField(_('صورة رئيسية'), default=False)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('وسائط')
        verbose_name_plural = _('وسائط')
        ordering = ['order', '-created_at']
        indexes = [models.Index(fields=['content_type', 'object_id'])]

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)
        
        if self.media_type == 'image' and self.file and not self.pk:
            try:
                img = Image.open(self.file)
                if img.height > 1200 or img.width > 1200:
                    output_size = (1200, 1200)
                    img.thumbnail(output_size)
                    output = BytesIO()
                    img_format = 'JPEG' if self.file.name.lower().endswith('.jpg') else 'PNG'
                    img.save(output, format=img_format, quality=85)
                    output.seek(0)
                    self.file.save(self.file.name, ContentFile(output.read()), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)

    def get_dimensions(self):
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
        return self.file.size if self.file else 0

    def to_dict(self):
        dimensions = self.get_dimensions() if self.media_type == 'image' else None
        return {
            'id': self.id, 'url': self.file.url if self.file else None,
            'name': self.name, 'type': self.media_type, 'size': self.file_size,
            'dimensions': dimensions, 'is_primary': self.is_primary,
        }

class Location(BaseModel):
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
        indexes = [models.Index(fields=['city', 'state'])]
        
    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"

    @property
    def coordinates(self):
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None

class Property(BaseModel):
    PROPERTY_TYPES = [
        ('residential', _('سكني')), ('commercial', _('تجاري')), ('industrial', _('صناعي')),
        ('land', _('أرض')), ('agricultural', _('زراعي')), ('mixed_use', _('متعدد الاستخدامات')),
    ]
    
    BUILDING_TYPES = [
        ('apartment', _('شقة')), ('villa', _('فيلا')), ('house', _('منزل')),
        ('office', _('مكتب')), ('retail', _('محل تجاري')), ('warehouse', _('مستودع')), ('other', _('أخرى')),
    ]
    
    STATUS_CHOICES = [
        ('available', _('متاح')), ('under_contract', _('تحت العقد')),
        ('sold', _('مباع')), ('auction', _('في المزاد')),
    ]

    property_number = models.CharField(_('رقم العقار'), max_length=50, unique=True, blank=True)
    title = models.CharField(_('العنوان'), max_length=255)
    slug = models.SlugField(_('الرابط المختصر'), max_length=255, unique=True, blank=True, allow_unicode=True)
    property_type = models.CharField(_('نوع العقار'), max_length=20, choices=PROPERTY_TYPES)
    building_type = models.CharField(_('نوع المبنى'), max_length=20, choices=BUILDING_TYPES, null=True, blank=True)
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='available')
    deed_number = models.CharField(_('رقم الصك'), max_length=100, unique=True, help_text=_('رقم صك الملكية الرسمي للعقار'))
    description = models.TextField(_('الوصف'))
    meta_description = models.TextField(_('وصف ميتا'), blank=True)
    search_keywords = models.TextField(_('كلمات البحث'), blank=True)
    size_sqm = models.DecimalField(_('المساحة (متر مربع)'), max_digits=10, decimal_places=2)
    floors = models.PositiveSmallIntegerField(_('عدد الطوابق'), null=True, blank=True)
    year_built = models.PositiveIntegerField(_('سنة البناء'), null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name=_('الموقع'), related_name='properties')
    address = models.CharField(_('العنوان التفصيلي'), max_length=255)
    market_value = models.DecimalField(_('القيمة السوقية'), max_digits=14, decimal_places=2)
    minimum_bid = models.DecimalField(_('الحد الأدنى للمزايدة'), max_digits=14, decimal_places=2, null=True, blank=True)
    features = models.JSONField(_('المميزات'), default=list, blank=True)
    amenities = models.JSONField(_('المرافق'), default=list, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='owned_properties', null=True, verbose_name=_('المالك'))
    is_published = models.BooleanField(_('منشور'), default=False)
    is_featured = models.BooleanField(_('مميز'), default=False)
    is_verified = models.BooleanField(_('موثق'), default=False)
    view_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)
    availability_date = models.DateField(_('تاريخ التوفر'), null=True, blank=True)

    media = GenericRelation(Media, related_query_name='property')

    class Meta:
        verbose_name = _('عقار')
        verbose_name_plural = _('العقارات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_number']), models.Index(fields=['deed_number']),
            models.Index(fields=['status']), models.Index(fields=['market_value']),
            models.Index(fields=['property_type']), models.Index(fields=['location', 'property_type']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.property_number:
            prefix = self.property_type[:3].upper()
            self.property_number = f"{prefix}-{random.randint(10000, 99999)}"
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)
        cache.delete(f'property_{self.id}')

    def _generate_unique_slug(self):
        original_slug = slugify(self.title, allow_unicode=True)
        if not original_slug:
            original_slug = f"property-{self.property_number or random.randint(10000, 99999)}"
        
        unique_slug = original_slug
        counter = 1
        while Property.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f"{original_slug}-{counter}"
            counter += 1
        return unique_slug

    def get_main_image(self):
        return (self.media.filter(media_type='image', is_primary=True, is_deleted=False).first() or
                self.media.filter(media_type='image', is_deleted=False).first())

    def get_all_images(self):
        return self.media.filter(media_type='image', is_deleted=False).order_by('-is_primary', 'order', '-created_at')

    def increment_view_count(self):
        Property.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])
        return self.view_count

    def to_dict(self):
        main_image = self.get_main_image()
        return {
            'id': self.id, 'title': self.title, 'slug': self.slug, 'property_number': self.property_number,
            'property_type': {'code': self.property_type, 'name': self.get_property_type_display()},
            'building_type': {'code': self.building_type, 'name': self.get_building_type_display()} if self.building_type else None,
            'status': self.status, 'status_display': self.get_status_display(), 'description': self.description,
            'size_sqm': float(self.size_sqm) if self.size_sqm else None,
            'location': {
                'address': self.address, 'city': self.location.city if self.location else None,
                'state': self.location.state if self.location else None, 'country': self.location.country if self.location else None,
            } if self.location else None,
            'market_value': float(self.market_value) if self.market_value else None,
            'main_image': main_image.to_dict() if main_image else None,
            'media_count': self.media.filter(is_deleted=False).count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Room(BaseModel):
    ROOM_TYPES = [
        ('bedroom', _('غرفة نوم')), ('bathroom', _('حمام')), ('kitchen', _('مطبخ')),
        ('living', _('غرفة معيشة')), ('dining', _('غرفة طعام')), ('office', _('مكتب')), ('other', _('أخرى')),
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
        indexes = [models.Index(fields=['property', 'floor']), models.Index(fields=['room_type'])]

    def __str__(self):
        return f"{self.get_room_type_display()} - {self.name} ({self.property.title})"

class Auction(BaseModel):
    AUCTION_TYPES = [
        ('public', _('عام')), ('private', _('خاص')), ('sealed', _('مغلق')), ('dutch', _('هولندي')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')), ('scheduled', _('مجدول')), ('live', _('مباشر')),
        ('ended', _('منتهي')), ('cancelled', _('ملغي')), ('completed', _('مكتمل')),
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
            models.Index(fields=['slug']), models.Index(fields=['status']),
            models.Index(fields=['start_date']), models.Index(fields=['related_property']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        if self.is_published and self.status in ['scheduled', 'live'] and self.related_property:
            self.related_property.status = 'auction'
            self.related_property.save(update_fields=['status'])
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        original_slug = slugify(self.title, allow_unicode=True)
        unique_slug = original_slug
        counter = 1
        while Auction.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f"{original_slug}-{counter}"
            counter += 1
        return unique_slug

    @property
    def time_remaining(self):
        if not self.end_date or self.end_date <= timezone.now():
            return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0, "total_seconds": 0}
        time_left = self.end_date - timezone.now()
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds, "total_seconds": time_left.total_seconds()}

    def is_active(self):
        now = timezone.now()
        return (self.status == 'live' and self.start_date <= now and self.end_date > now and self.is_published)

    def can_accept_bids(self):
        return self.is_active() and not self.is_deleted

    def increment_view_count(self):
        Auction.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])
        return self.view_count

class Bid(BaseModel):
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')), ('accepted', _('مقبولة')), ('rejected', _('مرفوضة')),
        ('outbid', _('تمت المزايدة بأعلى')), ('winning', _('فائزة')),
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
            models.Index(fields=['bidder']), models.Index(fields=['status']),
        ]

    def __str__(self):
        bidder_name = f"{self.bidder.first_name} {self.bidder.last_name}".strip() or self.bidder.email if self.bidder else "N/A"
        return f"{bidder_name} زايد بمبلغ {self.bid_amount} على {self.auction.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.auction:
            Auction.objects.filter(pk=self.auction.pk).update(bid_count=models.F('bid_count') + 1)
            if not self.auction.current_bid or self.bid_amount > self.auction.current_bid:
                self.auction.current_bid = self.bid_amount
                self.auction.save(update_fields=['current_bid'])

    @property
    def bidder_name(self):
        if not self.bidder:
            return "Unknown"
        return f"{self.bidder.first_name} {self.bidder.last_name}".strip() or self.bidder.email

class Message(BaseModel):
    STATUS_CHOICES = [
        ('unread', _('غير مقروء')), ('read', _('مقروء')), ('replied', _('تم الرد')), ('archived', _('مؤرشف')),
    ]
    PRIORITY_CHOICES = [
        ('low', _('منخفض')), ('normal', _('عادي')), ('high', _('عالي')), ('urgent', _('عاجل')),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name=_('المرسل'))
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', verbose_name=_('المستقبل'))
    subject = models.CharField(_('الموضوع'), max_length=255)
    body = models.TextField(_('محتوى الرسالة'))
    related_property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages', verbose_name=_('العقار المرتبط'))
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='unread')
    priority = models.CharField(_('الأولوية'), max_length=20, choices=PRIORITY_CHOICES, default='normal')
    read_at = models.DateTimeField(_('تاريخ القراءة'), null=True, blank=True)
    replied_at = models.DateTimeField(_('تاريخ الرد'), null=True, blank=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name=_('الرسالة الأصلية'))
    thread_id = models.UUIDField(_('معرف المحادثة'), default=uuid.uuid4, db_index=True)
    ip_address = models.GenericIPAddressField(_('عنوان IP'), null=True, blank=True)
    user_agent = models.TextField(_('متصفح المستخدم'), blank=True)
    
    class Meta:
        verbose_name = _('رسالة')
        verbose_name_plural = _('الرسائل')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', '-created_at']), models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['thread_id', '-created_at']), models.Index(fields=['status', '-created_at']),
            models.Index(fields=['related_property', '-created_at']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.sender} to {self.recipient}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.parent_message:
            self.thread_id = uuid.uuid4()
        elif self.parent_message:
            self.thread_id = self.parent_message.thread_id
        super().save(*args, **kwargs)

    def mark_as_read(self):
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])

    def mark_as_replied(self):
        self.status = 'replied'
        self.replied_at = timezone.now()
        self.save(update_fields=['status', 'replied_at'])

    @property 
    def is_read(self):
        return self.status in ['read', 'replied', 'archived']

class MessageAttachment(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments', verbose_name=_('الرسالة'))
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