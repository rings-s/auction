from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Property, Document, Auction, Bid, Contract,
    Payment, Transaction, MessageThread, Message,
    ThreadParticipant, Notification, PropertyView
)


# Inline admins
class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    classes = ['collapse']
    fields = ('document_number', 'title', 'document_type', 'verification_status')
    readonly_fields = ('document_number',)

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    classes = ['collapse']
    fields = ('bidder', 'bid_amount', 'bid_time', 'status')
    readonly_fields = ('bid_time',)

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    classes = ['collapse']
    fields = ('sender', 'subject', 'sent_at', 'status')
    readonly_fields = ('sent_at',)

class ThreadParticipantInline(admin.TabularInline):
    model = ThreadParticipant
    extra = 0
    classes = ['collapse']
    fields = ('user', 'role', 'is_active', 'is_muted')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    classes = ['collapse']
    fields = ('payment_number', 'payment_type', 'amount', 'payment_date', 'status')
    readonly_fields = ('payment_number',)

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    classes = ['collapse']
    fields = ('transaction_number', 'transaction_type', 'amount', 'transaction_date', 'status')
    readonly_fields = ('transaction_number',)

@admin.register(Property)
class PropertyAdmin(GISModelAdmin):
    list_display = ('property_number', 'title', 'property_type', 'city', 'district', 'bedrooms', 'bathrooms', 'area', 'status', 'is_published', 'main_image_url')
    list_filter = ('property_type', 'city', 'status', 'is_published', 'is_featured', 'is_verified')
    search_fields = ('property_number', 'title', 'address', 'city', 'district')
    readonly_fields = ('created_at', 'updated_at', 'verification_date')
    list_select_related = ('owner', 'verified_by')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('property_number', 'title', 'slug', 'property_type', 'description', 'condition')
        }),
        (_('Ownership Details'), {
            'fields': ('owner', 'status', 'deed_number', 'deed_date')
        }),
        (_('Location Information'), {
            'fields': ('address', 'city', 'district', 'postal_code', 'country', 'latitude', 'longitude', 'location',
                      'facing_direction')
        }),
        (_('Property Specifications'), {
            'fields': ('area', 'built_up_area', 'bedrooms', 'bathrooms', 'floor_number', 'total_floors', 'year_built')
        }),
        (_('Financial Details'), {
            'fields': ('estimated_value', 'asking_price', 'price_per_sqm')
        }),
        (_('JSON Fields'), {
            'classes': ('collapse',),
            'fields': ('rooms', 'outdoor_spaces', 'rental_details', 'parking', 'images', 'videos', 'virtual_tours',
                      'documents', 'floor_plans', 'features', 'amenities', 'building_services', 'infrastructure',
                      'street_details', 'surroundings', 'reference_ids', 'status_history')
        }),
        (_('Usage'), {
            'fields': ('current_usage', 'optimal_usage')
        }),
        (_('Verification and Approvals'), {
            'fields': ('is_verified', 'verified_by', 'verification_date', 'verification_details')
        }),
        (_('Visibility Settings'), {
            'fields': ('is_featured', 'is_published', 'publish_date', 'views_count')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [DocumentInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'verified_by')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_number', 'title', 'document_type', 'related_property', 'auction', 'verification_status', 'is_expired')
    list_filter = ('document_type', 'verification_status')
    search_fields = ('document_number', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('related_property', 'auction', 'contract', 'uploaded_by', 'verified_by')
    fieldsets = (
        (_('Document Information'), {
            'fields': ('document_number', 'title', 'document_type', 'description')
        }),
        (_('Related Models'), {
            'fields': ('related_property', 'auction', 'contract')
        }),
        (_('Files'), {
            'fields': ('files', 'metadata')
        }),
        (_('Ownership and Verification'), {
            'fields': ('uploaded_by', 'verification_status', 'verified_by', 'verification_date', 'verification_notes')
        }),
        (_('Expiry and Validity'), {
            'fields': ('issue_date', 'expiry_date')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('get_uuid', 'title', 'related_property', 'auction_type', 'status', 'start_date', 'end_date', 'current_bid', 'is_active', 'highest_bid', 'bid_count')
    list_filter = ('auction_type', 'status', 'is_private', 'is_published', 'is_featured')
    search_fields = ('title', 'description', 'related_property__title', 'related_property__property_number')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    list_select_related = ('related_property', 'created_by', 'auctioneer', 'winning_bidder')
    fieldsets = (
        (_('Auction Information'), {
            'fields': ('uuid', 'related_property', 'title', 'slug', 'description', 'auction_type', 'status')
        }),
        (_('Ownership and Management'), {
            'fields': ('created_by', 'auctioneer')
        }),
        (_('Dates and Duration'), {
            'fields': ('start_date', 'end_date', 'auto_extend', 'extension_minutes')
        }),
        (_('Pricing and Bidding Rules'), {
            'fields': ('starting_price', 'reserve_price', 'min_bid_increment', 'deposit_amount', 'deposit_required')
        }),
        (_('Commission and Fees'), {
            'fields': ('buyer_premium_percent', 'seller_commission_percent')
        }),
        (_('Results'), {
            'fields': ('current_bid', 'winning_bid', 'winning_bidder', 'end_reason')
        }),
        (_('Location for Onsite Auctions'), {
            'classes': ('collapse',),
            'fields': ('location_address', 'location_latitude', 'location_longitude', 'location_details')
        }),
        (_('Participation Requirements'), {
            'classes': ('collapse',),
            'fields': ('terms_conditions', 'participation_requirements')
        }),
        (_('Media'), {
            'classes': ('collapse',),
            'fields': ('images', 'videos', 'documents')
        }),
        (_('Private Auction Settings'), {
            'fields': ('is_private',)
        }),
        (_('Visibility and Promotion'), {
            'fields': ('is_featured', 'is_published', 'publish_date', 'views_count')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [BidInline, DocumentInline]

    def get_uuid(self, obj):
        return str(obj.uuid)
    get_uuid.short_description = _('UUID')
    get_uuid.admin_order_field = 'uuid'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            if 'invited_bidders' not in form.base_fields:
                from django.forms import ModelMultipleChoiceField
                from django.contrib.auth import get_user_model
                User = get_user_model()
                form.base_fields['invited_bidders'] = ModelMultipleChoiceField(
                    queryset=User.objects.all(),
                    required=False,
                    label=_('المزايدين المدعوين')
                )
        return form

@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ('auction', 'view_type', 'location', 'size_sqm', 'condition')
    list_filter = ('view_type',)
    search_fields = ('location', 'address', 'legal_description')
    list_select_related = ('auction',)
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('auction', 'view_type', 'size_sqm', 'location', 'address')
        }),
        (_('View Details'), {
            'fields': ('elevation', 'view_direction', 'condition')
        }),
        (_('Legal Information'), {
            'fields': ('legal_description',)
        }),
        (_('Additional Information'), {
            'fields': ('historical_views', 'images')
        }),
    )

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction', 'bidder', 'bid_amount', 'bid_time', 'status', 'is_auto_bid')
    list_filter = ('status', 'is_auto_bid', 'bid_time')
    search_fields = ('bidder__username', 'auction__title', 'auction__related_property__title')
    readonly_fields = ('bid_time', 'created_at', 'updated_at')
    list_select_related = ('auction', 'bidder')
    fieldsets = (
        (_('Bid Information'), {
            'fields': ('auction', 'bidder', 'bid_amount', 'bid_time', 'status')
        }),
        (_('Auto Bidding'), {
            'fields': ('max_bid_amount', 'is_auto_bid')
        }),
        (_('Tracking Information'), {
            'classes': ('collapse',),
            'fields': ('ip_address', 'user_agent', 'device_info')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'title', 'auction', 'buyer', 'seller', 'contract_amount', 'contract_date', 'status', 'is_fully_signed')
    list_filter = ('status', 'is_verified', 'payment_method', 'contract_date')
    search_fields = ('contract_number', 'title', 'buyer__username', 'seller__username', 'related_property__title')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('auction', 'related_property', 'buyer', 'seller', 'agent')
    fieldsets = (
        (_('Contract Information'), {
            'fields': ('contract_number', 'title', 'auction', 'related_property')
        }),
        (_('Parties'), {
            'fields': ('buyer', 'seller', 'agent')
        }),
        (_('Contract Details'), {
            'fields': ('status', 'contract_date', 'effective_date', 'expiry_date')
        }),
        (_('Financial Details'), {
            'fields': ('contract_amount', 'deposit_amount', 'commission_amount', 'tax_amount', 'total_amount', 'payment_method', 'payment_terms')
        }),
        (_('Files'), {
            'classes': ('collapse',),
            'fields': ('files',)
        }),
        (_('Content'), {
            'classes': ('collapse',),
            'fields': ('terms_conditions', 'special_conditions', 'notes')
        }),
        (_('Signatures and Verification'), {
            'fields': ('buyer_signed', 'seller_signed', 'agent_signed', 'buyer_signature_date', 'seller_signature_date', 'agent_signature_date')
        }),
        (_('Verification'), {
            'fields': ('is_verified', 'verification_authority', 'verification_date')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [PaymentInline, DocumentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'contract', 'payment_type', 'payment_method', 'amount', 'currency', 'payment_date', 'status', 'is_overdue')
    list_filter = ('payment_type', 'payment_method', 'status', 'currency')
    search_fields = ('payment_number', 'payer__username', 'payee__username', 'contract__contract_number')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('contract', 'payer', 'payee', 'confirmed_by')
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('payment_number', 'contract', 'payment_type', 'payment_method')
        }),
        (_('Financial Details'), {
            'fields': ('amount', 'currency', 'payment_date', 'due_date')
        }),
        (_('Parties'), {
            'fields': ('payer', 'payee')
        }),
        (_('Status'), {
            'fields': ('status', 'confirmed_at', 'confirmed_by')
        }),
        (_('Payment Details'), {
            'classes': ('collapse',),
            'fields': ('transaction_reference', 'bank_name', 'account_name', 'account_number', 'check_number')
        }),
        (_('Files and Notes'), {
            'classes': ('collapse',),
            'fields': ('files', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [TransactionInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_number', 'transaction_type', 'amount', 'currency', 'from_user', 'to_user', 'transaction_date', 'status')
    list_filter = ('transaction_type', 'status', 'currency')
    search_fields = ('transaction_number', 'description', 'from_user__username', 'to_user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('from_user', 'to_user', 'payment', 'auction', 'contract', 'processed_by')
    fieldsets = (
        (_('Transaction Information'), {
            'fields': ('transaction_number', 'transaction_type', 'description')
        }),
        (_('Financial Details'), {
            'fields': ('amount', 'currency', 'exchange_rate', 'fee_amount', 'tax_amount')
        }),
        (_('Users Involved'), {
            'fields': ('from_user', 'to_user')
        }),
        (_('Related Models'), {
            'fields': ('payment', 'auction', 'contract')
        }),
        (_('Transaction Details'), {
            'fields': ('transaction_date', 'status', 'reference', 'notes')
        }),
        (_('Processing'), {
            'fields': ('processed_at', 'processed_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'thread_type', 'related_property', 'related_auction', 'is_active', 'is_resolved', 'last_message_at', 'message_count')
    list_filter = ('thread_type', 'is_active', 'is_resolved')
    search_fields = ('subject',)
    readonly_fields = ('created_at', 'updated_at', 'last_message_at')
    list_select_related = ('related_property', 'related_auction', 'related_contract', 'resolved_by')
    fieldsets = (
        (_('Thread Information'), {
            'fields': ('subject', 'thread_type')
        }),
        (_('Related Models'), {
            'fields': ('related_property', 'related_auction', 'related_contract')
        }),
        (_('Thread Status'), {
            'fields': ('is_active', 'is_resolved', 'resolved_at', 'resolved_by')
        }),
        (_('Activity Tracking'), {
            'fields': ('last_message_at',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [ThreadParticipantInline, MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'sender', 'subject', 'message_type', 'status', 'sent_at', 'has_attachments')
    list_filter = ('message_type', 'status', 'is_system_message', 'is_important')
    search_fields = ('subject', 'content', 'sender__username')
    readonly_fields = ('sent_at', 'created_at', 'updated_at')
    list_select_related = ('thread', 'sender', 'related_property', 'related_auction', 'related_contract', 'parent_message')
    fieldsets = (
        (_('Message Information'), {
            'fields': ('thread', 'sender', 'subject', 'content', 'message_type', 'status')
        }),
        (_('Read Receipts'), {
            'fields': ('sent_at', 'delivered_at', 'read_at')
        }),
        (_('Related Objects'), {
            'fields': ('related_property', 'related_auction', 'related_contract')
        }),
        (_('Nested Messages'), {
            'fields': ('parent_message',)
        }),
        (_('Attachments'), {
            'classes': ('collapse',),
            'fields': ('attachments',)
        }),
        (_('Flags'), {
            'fields': ('is_system_message', 'is_important')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(ThreadParticipant)
class ThreadParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'user', 'role', 'is_active', 'is_muted', 'last_read_at', 'has_unread_messages', 'unread_count')
    list_filter = ('role', 'is_active', 'is_muted')
    search_fields = ('thread__subject', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('thread', 'user')
    fieldsets = (
        (_('Participant Information'), {
            'fields': ('thread', 'user', 'role')
        }),
        (_('Participant Status'), {
            'fields': ('is_active', 'is_muted', 'last_read_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'notification_type', 'title', 'channel', 'is_read', 'is_sent', 'created_at')
    list_filter = ('notification_type', 'channel', 'is_read', 'is_sent')
    search_fields = ('title', 'content', 'recipient__username')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('recipient', 'related_property', 'related_auction', 'related_bid', 'related_contract', 'related_payment', 'related_message')
    fieldsets = (
        (_('Notification Information'), {
            'fields': ('recipient', 'notification_type', 'title', 'content', 'channel')
        }),
        (_('Related Entities'), {
            'fields': ('related_property', 'related_auction', 'related_bid', 'related_contract', 'related_payment', 'related_message')
        }),
        (_('Status'), {
            'fields': ('is_read', 'read_at', 'is_sent', 'sent_at')
        }),
        (_('Display Properties'), {
            'fields': ('icon', 'color', 'action_url')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


# Change admin site title, header, and subtitle
admin.site.site_title = _("auction")
admin.site.site_header = _("auction")
admin.site.index_title = _("auction")