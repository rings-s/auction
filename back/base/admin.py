from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count, Sum, Max
from .models import Media, Location, Property, Room, Auction, Bid


class MediaInline(GenericTabularInline):
    model = Media
    extra = 1
    fields = ('file', 'name', 'media_type', 'is_primary', 'order')
    classes = ('collapse',)


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('name', 'room_type', 'floor', 'area_sqm', 'has_window', 'has_bathroom')
    classes = ('collapse',)


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    fields = ('bidder', 'bid_amount', 'status', 'bid_time')
    readonly_fields = ('bidder', 'bid_amount', 'bid_time')
    can_delete = False
    max_num = 10
    classes = ('collapse',)
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'media_type', 'content_type', 'object_id', 'file_preview', 'is_primary', 'created_at')
    list_filter = ('media_type', 'is_primary', 'content_type')
    search_fields = ('name',)
    readonly_fields = ('file_preview', 'created_at', 'updated_at')
    
    def file_preview(self, obj):
        if obj.media_type == 'image' and obj.file:
            return format_html('<img src="{}" width="100" height="auto" />', obj.file.url)
        return '-'
    file_preview.short_description = _('معاينة')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'state', 'country', 'postal_code', 'property_count', 'created_at')
    list_filter = ('country', 'state', 'city')
    search_fields = ('city', 'state', 'country', 'postal_code')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(property_count=Count('properties'))
        return queryset
    
    def property_count(self, obj):
        return obj.property_count
    property_count.short_description = _('عدد العقارات')
    property_count.admin_order_field = 'property_count'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_number', 'title', 'get_property_type_display', 'get_building_type_display', 'status', 
                   'size_sqm', 'location_display', 'market_value', 'owner', 'is_verified', 'view_count')
    list_filter = ('property_type', 'building_type', 'status', 'is_verified', 'is_published', 'is_featured')
    search_fields = ('title', 'property_number', 'deed_number', 'address', 'description')
    readonly_fields = ('property_number', 'slug', 'view_count', 'created_at', 'updated_at')
    inlines = [RoomInline, MediaInline]
    fieldsets = (
        (_('Basic Information'), {
            'fields': (('title', 'property_number', 'slug'), ('property_type', 'building_type', 'status'))
        }),
        (_('Property Details'), {
            'fields': ('description', 'meta_description', 'search_keywords', 'deed_number', 
                       ('size_sqm', 'floors', 'year_built'))
        }),
        (_('Location'), {
            'fields': ('location', 'address')
        }),
        (_('Financial'), {
            'fields': (('market_value', 'minimum_bid'),)
        }),
        (_('Features & Amenities'), {
            'fields': ('features', 'amenities'),
            'classes': ('collapse',)
        }),
        (_('Ownership & Settings'), {
            'fields': (('owner', 'is_verified'), ('is_published', 'is_featured'), 
                       'availability_date', 'view_count')
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def location_display(self, obj):
        if obj.location:
            return f"{obj.location.city}, {obj.location.state}"
        return '-'
    location_display.short_description = _('الموقع')
    
    actions = ['mark_as_verified', 'mark_as_featured', 'mark_as_published']
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_as_verified.short_description = _('تمييز كموثق')
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = _('تمييز كمميز')
    
    def mark_as_published(self, request, queryset):
        queryset.update(is_published=True)
    mark_as_published.short_description = _('نشر العقارات المحددة')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'property_link', 'get_room_type_display', 'floor', 'area_sqm', 'has_window', 'has_bathroom')
    list_filter = ('room_type', 'floor', 'has_window', 'has_bathroom')
    search_fields = ('name', 'description', 'property__title')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MediaInline]
    
    def property_link(self, obj):
        if obj.property:
            url = f"../property/{obj.property.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.property.title)
        return '-'
    property_link.short_description = _('العقار')


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_auction_type_display', 'status', 'property_link', 
                   'start_date', 'end_date', 'current_bid_display', 'bid_count', 'is_active_display')
    list_filter = ('auction_type', 'status', 'is_published', 'is_featured')
    search_fields = ('title', 'description', 'related_property__title')
    readonly_fields = ('slug', 'current_bid', 'bid_count', 'view_count', 
                      'registered_bidders', 'created_at', 'updated_at')
    inlines = [BidInline, MediaInline]
    fieldsets = (
        (_('Basic Information'), {
            'fields': (('title', 'slug'), ('auction_type', 'status'))
        }),
        (_('Description'), {
            'fields': ('description',)
        }),
        (_('Property'), {
            'fields': ('related_property',)
        }),
        (_('Auction Dates'), {
            'fields': (('start_date', 'end_date'), 'registration_deadline')
        }),
        (_('Bidding Information'), {
            'fields': (('starting_bid', 'current_bid'), ('minimum_increment', 'minimum_participants'), 
                       'auto_extend_minutes')
        }),
        (_('Settings'), {
            'fields': (('is_published', 'is_featured'), ('bid_count', 'view_count', 'registered_bidders'))
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def property_link(self, obj):
        if obj.related_property:
            url = f"../property/{obj.related_property.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.related_property.title)
        return '-'
    property_link.short_description = _('العقار')
    
    def current_bid_display(self, obj):
        if obj.current_bid:
            return f"{obj.current_bid:,} SAR"
        elif obj.starting_bid:
            return f"{obj.starting_bid:,} SAR (Starting)"
        return '-'
    current_bid_display.short_description = _('المزايدة الحالية')
    
    def is_active_display(self, obj):
        is_active = obj.is_active()
        return format_html('<span style="color: {}">●</span> {}', 
                         'green' if is_active else 'red',
                         _('نشط') if is_active else _('غير نشط'))
    is_active_display.short_description = _('نشط')
    
    actions = ['mark_as_published', 'mark_as_featured', 'cancel_auctions']
    
    def mark_as_published(self, request, queryset):
        queryset.update(is_published=True)
    mark_as_published.short_description = _('نشر المزادات المحددة')
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = _('تمييز كمميز')
    
    def cancel_auctions(self, request, queryset):
        queryset.update(status='cancelled')
    cancel_auctions.short_description = _('إلغاء المزادات المحددة')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction_link', 'bidder', 'bid_amount', 'status', 'bid_time', 'is_verified')
    list_filter = ('status', 'is_verified', 'bid_time')
    search_fields = ('bidder__email', 'bidder__first_name', 'bidder__last_name', 'auction__title')
    readonly_fields = ('bid_time', 'created_at', 'updated_at')
    
    def auction_link(self, obj):
        if obj.auction:
            url = f"../auction/{obj.auction.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.auction.title)
        return '-'
    auction_link.short_description = _('المزاد')
    
    actions = ['mark_as_accepted', 'mark_as_rejected', 'mark_as_verified']
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(status='accepted')
    mark_as_accepted.short_description = _('تمييز كمقبولة')
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = _('تمييز كمرفوضة')
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_as_verified.short_description = _('تمييز كموثقة')