from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from .models import *

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




@admin.register(DashboardMetrics)
class DashboardMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'metric_type', 'last_updated')
    list_filter = ('metric_type', 'last_updated')
    search_fields = ('user__email', 'metric_type')
    readonly_fields = ('last_updated',)
    
    def has_add_permission(self, request):
        return False  # Metrics are auto-generated

# -------------------------------------------------------------------------
# Property Management Models Admin
# -------------------------------------------------------------------------

class TenantInline(admin.TabularInline):
    model = Tenant
    extra = 0
    fields = ('full_name', 'email', 'phone', 'status')
    readonly_fields = ('created_at',)

class LeaseInline(admin.TabularInline):
    model = Lease
    extra = 0
    fields = ('lease_number', 'tenant', 'start_date', 'end_date', 'monthly_rent', 'status')
    readonly_fields = ('lease_number', 'created_at')

class MaintenanceRequestInline(admin.TabularInline):
    model = MaintenanceRequest
    extra = 0
    fields = ('title', 'priority', 'status', 'reported_date', 'due_date')
    readonly_fields = ('reported_date',)

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0
    fields = ('title', 'expense_type', 'amount', 'expense_date', 'status')
    readonly_fields = ('created_at',)

@admin.register(RentalProperty)
class RentalPropertyAdmin(admin.ModelAdmin):
    list_display = ('base_property_title', 'rental_status', 'monthly_rent', 'rental_type', 'available_from', 'current_tenant_name')
    list_filter = ('rental_status', 'rental_type', 'furnished', 'pets_allowed')
    search_fields = ('base_property__title', 'base_property__property_number')
    readonly_fields = ('total_rental_income', 'created_at', 'updated_at')
    inlines = [LeaseInline]  # MaintenanceRequestInline and ExpenseInline removed - no direct FK relationship
    
    def base_property_title(self, obj):
        return obj.base_property.title if obj.base_property else '-'
    base_property_title.short_description = 'Property'
    
    def current_tenant_name(self, obj):
        tenant = obj.current_tenant
        return tenant.full_name if tenant else '-'
    current_tenant_name.short_description = 'Current Tenant'

@admin.register(MaintenanceCategory)
class MaintenanceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_property_title', 'priority', 'status', 'reported_date', 'due_date', 'assigned_to', 'assigned_worker_name')
    list_filter = ('priority', 'status', 'reported_date', 'due_date', 'assigned_worker__categories')
    search_fields = ('title', 'description', 'maintenance_property__title', 'assigned_worker__first_name', 'assigned_worker__last_name', 'assigned_worker__employee_id')
    readonly_fields = ('reported_date', 'created_at', 'updated_at')
    actions = ['mark_as_completed', 'assign_to_me']
    
    def base_property_title(self, obj):
        return obj.maintenance_property.title if obj.maintenance_property else '-'
    base_property_title.short_description = 'Property'
    
    def assigned_worker_name(self, obj):
        if obj.assigned_worker:
            return format_html('<a href="../worker/{}/change/">{} ({})</a>', 
                             obj.assigned_worker.id, obj.assigned_worker.full_name, obj.assigned_worker.employee_id)
        return '-'
    assigned_worker_name.short_description = _('Assigned Worker')
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = 'Mark selected requests as completed'
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user)
    assign_to_me.short_description = 'Assign selected requests to me'

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_property_title', 'expense_type', 'amount', 'currency', 'status', 'expense_date')
    list_filter = ('expense_type', 'status', 'currency', 'expense_date')
    search_fields = ('title', 'description', 'base_property__title', 'vendor_name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    actions = ['mark_as_paid', 'mark_as_approved']
    
    def base_property_title(self, obj):
        return obj.base_property.title if obj.base_property else '-'
    base_property_title.short_description = 'Property'
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = 'Mark selected expenses as paid'
    
    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved')
    mark_as_approved.short_description = 'Mark selected expenses as approved'

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status', 'tenant_type', 'current_property_title', 'created_at')
    list_filter = ('status', 'tenant_type', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'national_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LeaseInline]
    
    def current_property_title(self, obj):
        current_prop = obj.current_property
        return current_prop.base_property.title if current_prop else '-'
    current_property_title.short_description = 'Current Property'

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('lease_number', 'tenant_name', 'property_title', 'start_date', 'end_date', 'monthly_rent', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('lease_number', 'tenant__first_name', 'tenant__last_name', 'rental_property__base_property__title')
    readonly_fields = ('lease_number', 'created_at', 'updated_at')
    
    def tenant_name(self, obj):
        return obj.tenant.full_name if obj.tenant else '-'
    tenant_name.short_description = 'Tenant'
    
    def property_title(self, obj):
        return obj.rental_property.base_property.title if obj.rental_property else '-'
    property_title.short_description = 'Property'

@admin.register(PropertyAnalytics)
class PropertyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('base_property_title', 'total_revenue', 'total_expenses', 'net_income', 'roi_percentage', 'occupancy_rate')
    list_filter = ('calculation_date',)
    search_fields = ('base_property__title',)
    readonly_fields = ('calculation_date', 'created_at', 'updated_at')
    
    def base_property_title(self, obj):
        return obj.base_property.title if obj.base_property else '-'
    base_property_title.short_description = 'Property'
    
    def has_add_permission(self, request):
        return False  # Analytics are auto-generated

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'status', 'period_start', 'period_end', 'generated_by', 'created_at')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('title', 'summary', 'generated_by__email')
    readonly_fields = ('generation_time', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False  # Reports are auto-generated


# -------------------------------------------------------------------------
# Accounts Models Admin (BankAccount, Payment, UserProfile)
# -------------------------------------------------------------------------

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('bank_account_name', 'bank_name', 'user_name', 'iban_number', 'is_primary', 'is_verified', 'created_at')
    list_filter = ('is_primary', 'is_verified', 'bank_name', 'created_at')
    search_fields = ('bank_account_name', 'bank_name', 'iban_number', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Account Information'), {
            'fields': ('user', 'bank_account_name', 'bank_name')
        }),
        (_('Banking Details'), {
            'fields': ('iban_number', 'account_number', 'swift_code')
        }),
        (_('Status'), {
            'fields': ('is_primary', 'is_verified')
        }),
        (_('Additional Information'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_verified', 'mark_as_primary']
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    user_name.short_description = _('User')
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_as_verified.short_description = _('Mark selected accounts as verified')
    
    def mark_as_primary(self, request, queryset):
        for account in queryset:
            # Ensure only one primary account per user
            BankAccount.objects.filter(user=account.user, is_primary=True).update(is_primary=False)
            account.is_primary = True
            account.save()
    mark_as_primary.short_description = _('Mark selected accounts as primary')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user_name', 'amount_display', 'payment_type', 'status', 'payment_date', 'property_title', 'is_overdue_display')
    list_filter = ('payment_type', 'status', 'currency', 'payment_date', 'due_date')
    search_fields = ('payment_id', 'user__email', 'user__first_name', 'user__last_name', 'description', 'property_reference__title')
    readonly_fields = ('payment_id', 'is_overdue', 'days_overdue', 'created_at', 'updated_at')
    date_hierarchy = 'payment_date'
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('payment_id', 'user', 'amount', 'currency', 'payment_type', 'status')
        }),
        (_('Dates'), {
            'fields': ('payment_date', 'due_date')
        }),
        (_('References'), {
            'fields': ('property_reference', 'tenant_reference', 'bank_account')
        }),
        (_('Description'), {
            'fields': ('description', 'notes')
        }),
        (_('Status Information'), {
            'fields': ('is_overdue', 'days_overdue'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_paid', 'mark_as_pending', 'mark_as_overdue']
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    user_name.short_description = _('User')
    
    def amount_display(self, obj):
        return f"{obj.amount:,} {obj.currency}"
    amount_display.short_description = _('Amount')
    
    def property_title(self, obj):
        if obj.property_reference:
            return format_html('<a href="../../../base/property/{}/change/">{}</a>', 
                             obj.property_reference.id, obj.property_reference.title)
        return '-'
    property_title.short_description = _('Property')
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">● {} {}</span>', 
                             _('Overdue'), f"({obj.days_overdue} days)" if obj.days_overdue else "")
        return format_html('<span style="color: green;">●</span> {}', _('On Time'))
    is_overdue_display.short_description = _('Status')
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = _('Mark selected payments as paid')
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = _('Mark selected payments as pending')
    
    def mark_as_overdue(self, request, queryset):
        queryset.update(status='overdue')
    mark_as_overdue.short_description = _('Mark selected payments as overdue')

# UserProfile is registered in accounts/admin.py - removed duplicate registration


# -------------------------------------------------------------------------
# Worker/Staff Models Admin
# -------------------------------------------------------------------------

@admin.register(WorkerCategory)
class WorkerCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'hourly_rate_range', 'worker_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Category Information'), {
            'fields': ('name', 'description')
        }),
        (_('Visual Settings'), {
            'fields': ('icon', 'color'),
            'classes': ('collapse',)
        }),
        (_('Rate Information'), {
            'fields': ('hourly_rate_min', 'hourly_rate_max'),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(worker_count=Count('workers'))
    
    def worker_count(self, obj):
        return obj.worker_count
    worker_count.short_description = _('Number of Workers')
    
    def hourly_rate_range(self, obj):
        if obj.hourly_rate_min and obj.hourly_rate_max:
            return f"{obj.hourly_rate_min} - {obj.hourly_rate_max} SAR"
        return '-'
    hourly_rate_range.short_description = _('Hourly Rate Range')

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'phone', 'employment_type', 'status', 'hourly_rate', 'is_available', 'active_jobs_count', 'rating', 'hire_date')
    list_filter = ('employment_type', 'status', 'is_available', 'categories', 'hire_date', 'city')
    search_fields = ('first_name', 'last_name', 'employee_id', 'national_id', 'email', 'phone')
    readonly_fields = ('employee_id', 'current_active_jobs', 'can_take_new_job', 'total_jobs_completed', 'created_at', 'updated_at', 'profile_image_preview')
    filter_horizontal = ('categories',)
    date_hierarchy = 'hire_date'
    fieldsets = (
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'national_id')
        }),
        (_('Employment Details'), {
            'fields': ('employee_id', 'employment_type', 'status', 'hire_date', 'supervisor')
        }),
        (_('Skills and Categories'), {
            'fields': ('categories',)
        }),
        (_('Profile Image'), {
            'fields': ('profile_image', 'profile_image_preview'),
            'classes': ('collapse',)
        }),
        (_('Contact Information'), {
            'fields': ('address', 'city', 'emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        (_('Work Information'), {
            'fields': ('hourly_rate', 'is_available', 'max_concurrent_jobs', 'notes')
        }),
        (_('Performance Metrics'), {
            'fields': ('rating', 'total_jobs_completed', 'current_active_jobs', 'can_take_new_job'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_available', 'mark_as_unavailable', 'mark_as_active', 'mark_as_inactive']
    
    def active_jobs_count(self, obj):
        count = obj.current_active_jobs
        color = 'red' if count >= obj.max_concurrent_jobs else 'green'
        return format_html('<span style="color: {};">{}</span>', color, count)
    active_jobs_count.short_description = _('Active Jobs')
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.profile_image.url)
        return '-'
    profile_image_preview.short_description = _('Profile Image Preview')
    
    def mark_as_available(self, request, queryset):
        queryset.update(is_available=True)
    mark_as_available.short_description = _('Mark selected workers as available')
    
    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = _('Mark selected workers as unavailable')
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = _('Mark selected workers as active')
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')
    mark_as_inactive.short_description = _('Mark selected workers as inactive')