from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Category, Subcategory, Auction, RealEstate, Vehicle, Machinery, Factory,
    HeavyVehicleAuction, Bid, Transaction, Document, Contract,
    ContractTermRevision, AuctionTimer, Message, PaymentMethod, Notification
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('category', 'name')

class AuctionTimerInline(admin.StackedInline):
    model = AuctionTimer
    extra = 0

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'subcategory', 'seller', 'status', 'start_time', 'end_time', 'current_price')
    list_filter = ('status', 'category', 'subcategory', 'currency')
    search_fields = ('title', 'description', 'seller__email')
    readonly_fields = ('id',)
    inlines = [AuctionTimerInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'category', 'subcategory', 'seller')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Pricing', {
            'fields': ('current_price', 'reserve_price', 'minimum_bid_increment', 'currency')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Images', {
            'fields': ('main_image', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5')
        }),
    )

@admin.register(RealEstate)
class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('auction', 'property_type', 'location', 'size_sqm', 'year_built')
    list_filter = ('property_type',)
    search_fields = ('location', 'address', 'auction__title')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('auction', 'make', 'model', 'year', 'mileage', 'condition')
    list_filter = ('condition', 'make', 'year')
    search_fields = ('make', 'model', 'vin', 'registration_number')

@admin.register(Machinery)
class MachineryAdmin(admin.ModelAdmin):
    list_display = ('auction', 'machine_type', 'manufacturer', 'model_number', 'year_manufactured')
    list_filter = ('machine_type', 'manufacturer')
    search_fields = ('machine_type', 'manufacturer', 'model_number')

@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ('auction', 'location', 'total_area_sqm', 'built_up_area_sqm')
    search_fields = ('location', 'address')

@admin.register(HeavyVehicleAuction)
class HeavyVehicleAuctionAdmin(admin.ModelAdmin):
    list_display = ('auction', 'vehicle_type', 'make', 'model', 'year', 'load_capacity')
    list_filter = ('vehicle_type', 'make')
    search_fields = ('make', 'model', 'registration_number')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('auction__title', 'bidder__email')
    readonly_fields = ('id', 'ip_address')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'auction', 'winner', 'amount', 'payment_type', 'status')
    list_filter = ('status', 'payment_type', 'payment_method')
    search_fields = ('reference_number', 'winner__email', 'auction__title')
    readonly_fields = ('id',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'auction', 'winner', 'winning_bid')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'payment_type', 'payment_method', 'status')
        }),
        ('Payment Processing', {
            'fields': ('reference_number', 'payment_proof', 'payment_date')
        }),
        ('External Payment IDs', {
            'fields': ('stripe_payment_id', 'paypal_transaction_id')
        }),
        ('Escrow Details', {
            'fields': ('escrow_agent',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'metadata')
        }),
    )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'auction', 'document_type', 'verification_status', 'uploaded_by')
    list_filter = ('document_type', 'verification_status')
    search_fields = ('title', 'description', 'auction__title')
    readonly_fields = ('id',)

    def get_file_preview(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "No file uploaded"
    get_file_preview.short_description = 'File Preview'

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'auction', 'seller', 'buyer', 'contract_type', 'status')
    list_filter = ('status', 'contract_type')
    search_fields = ('contract_number', 'seller__email', 'buyer__email')
    readonly_fields = ('id',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'contract_number', 'auction', 'contract_type', 'status')
        }),
        ('Parties', {
            'fields': ('seller', 'buyer', 'seller_legal_rep', 'buyer_legal_rep')
        }),
        ('Contract Details', {
            'fields': ('contract_value', 'deposit_amount', 'start_date', 'end_date')
        }),
        ('Signatures', {
            'fields': ('seller_signature_date', 'buyer_signature_date')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'review_date', 'review_notes')
        }),
    )

@admin.register(ContractTermRevision)
class ContractTermRevisionAdmin(admin.ModelAdmin):
    list_display = ('contract', 'terms_type', 'version_number', 'is_current_version', 'revised_by', 'approval_date')
    list_filter = ('terms_type', 'is_current_version')
    search_fields = ('contract__contract_number', 'terms_content', 'revision_reason')

    fieldsets = (
        ('Basic Information', {
            'fields': ('contract', 'terms_type', 'version_number', 'is_current_version')
        }),
        ('Content', {
            'fields': ('terms_content', 'revision_reason')
        }),
        ('Approval', {
            'fields': ('revised_by', 'approved_by', 'approval_date')
        }),
    )

@admin.register(AuctionTimer)
class AuctionTimerAdmin(admin.ModelAdmin):
    list_display = ('auction', 'duration', 'start_time', 'end_time', 'is_extended')
    list_filter = ('duration', 'is_extended')
    search_fields = ('auction__title',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('auction', 'duration', 'custom_duration')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Extension Settings', {
            'fields': ('auto_extend', 'extension_threshold', 'extension_duration')
        }),
        ('Extension Status', {
            'fields': ('is_extended', 'extension_count', 'last_extension')
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room_id', 'content_preview', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__email', 'content', 'room_id')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'created_at')
    list_filter = ('method_type', 'created_at')
    search_fields = ('user__email', 'method_type')
    readonly_fields = ('created_at', 'modified_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'message_preview', 'read', 'created_at')
    list_filter = ('notification_type', 'read', 'created_at')
    search_fields = ('user__email', 'message', 'notification_type')
    readonly_fields = ('id', 'created_at')
    
    def message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    message_preview.short_description = 'Message'

admin.site.site_title = 'Gudit Platform'
admin.site.site_header = 'Gudit Auctions Platform'
admin.site.index_title = 'Welcome to Gudit Auctions Platform'