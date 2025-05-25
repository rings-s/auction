from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from .models import Media, Location, Property, Room, Auction, Bid

class MediaInline(GenericTabularInline):
    model = Media
    extra = 1
    fields = ('file', 'name', 'media_type', 'is_primary', 'order')
    classes = ('collapse',)

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('name', 'room_type', 'floor', 'area_sqm', 'has_window')
    classes = ('collapse',)

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    fields = ('bidder', 'bid_amount', 'status', 'bid_time')
    readonly_fields = ('bidder', 'bid_amount', 'bid_time')
    can_delete = False
    max_num = 10

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'media_type', 'content_type', 'file_preview', 'is_primary', 'created_at')
    list_filter = ('media_type', 'is_primary', 'content_type')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    def file_preview(self, obj):
        if obj.media_type == 'image' and obj.file:
            return format_html('<img src="{}" width="100" height="auto" />', obj.file.url)
        return '-'

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country', 'property_count', 'created_at')
    list_filter = ('country', 'state')
    search_fields = ('city', 'state', 'country')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(property_count=Count('properties'))
    
    def property_count(self, obj):
        return obj.property_count

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'status', 'market_value', 'owner', 'is_verified', 'view_count')
    list_filter = ('property_type', 'building_type', 'status', 'is_verified', 'is_published')
    search_fields = ('title', 'property_number', 'deed_number')
    readonly_fields = ('property_number', 'slug', 'view_count', 'created_at', 'updated_at')
    inlines = [RoomInline, MediaInline]
    actions = ['mark_as_verified', 'mark_as_published']
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    
    def mark_as_published(self, request, queryset):
        queryset.update(is_published=True)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_link', 'room_type', 'floor', 'area_sqm')
    list_filter = ('room_type', 'floor', 'has_window')
    search_fields = ('name', 'property__title')
    inlines = [MediaInline]
    
    def property_link(self, obj):
        if obj.property:
            return format_html('<a href="../property/{}/change/">{}</a>', obj.property.id, obj.property.title)
        return '-'

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'auction_type', 'status', 'start_date', 'current_bid_display', 'bid_count', 'is_active_display')
    list_filter = ('auction_type', 'status', 'is_published')
    search_fields = ('title', 'related_property__title')
    readonly_fields = ('slug', 'current_bid', 'bid_count', 'view_count', 'created_at')
    inlines = [BidInline, MediaInline]
    actions = ['mark_as_published', 'cancel_auctions']
    
    def current_bid_display(self, obj):
        if obj.current_bid:
            return f"{obj.current_bid:,} SAR"
        return f"{obj.starting_bid:,} SAR (Starting)"
    
    def is_active_display(self, obj):
        is_active = obj.is_active()
        return format_html('<span style="color: {}">●</span> {}', 
                         'green' if is_active else 'red',
                         _('نشط') if is_active else _('غير نشط'))
    
    def mark_as_published(self, request, queryset):
        queryset.update(is_published=True)
    
    def cancel_auctions(self, request, queryset):
        queryset.update(status='cancelled')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction_link', 'bidder', 'bid_amount', 'status', 'bid_time', 'is_verified')
    list_filter = ('status', 'is_verified', 'bid_time')
    search_fields = ('bidder__email', 'auction__title')
    readonly_fields = ('bid_time', 'created_at')
    actions = ['mark_as_verified']
    
    def auction_link(self, obj):
        if obj.auction:
            return format_html('<a href="../auction/{}/change/">{}</a>', obj.auction.id, obj.auction.title)
        return '-'
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)