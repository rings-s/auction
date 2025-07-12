from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import (
    FinancialTransaction, PropertyExpense, RentalProperty, Lease,
    MaintenanceRequest, Vendor, ContractTemplate, Contract, PropertyAnalytics
)

# -------------------------------------------------------------------------
# Financial Management Admin
# -------------------------------------------------------------------------

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_type', 'amount', 'status', 'payer', 'payee', 'due_date', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at', 'due_date')
    search_fields = ('description', 'reference_number', 'payer__email', 'payee__email')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('transaction_id', 'transaction_type', 'amount', 'status')
        }),
        (_('Parties'), {
            'fields': ('payer', 'payee')
        }),
        (_('Details'), {
            'fields': ('description', 'reference_number', 'due_date', 'related_property')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PropertyExpense)
class PropertyExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'category', 'expense_date', 'related_property', 'vendor_name', 'created_by')
    list_filter = ('category', 'expense_date', 'created_at')
    search_fields = ('description', 'vendor_name', 'invoice_number', 'related_property__title')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    date_hierarchy = 'expense_date'
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('description', 'amount', 'category', 'expense_date')
        }),
        (_('Vendor Details'), {
            'fields': ('vendor_name', 'vendor_contact', 'invoice_number')
        }),
        (_('Property & User'), {
            'fields': ('related_property', 'created_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# -------------------------------------------------------------------------
# Rental Management Admin
# -------------------------------------------------------------------------

@admin.register(RentalProperty)
class RentalPropertyAdmin(admin.ModelAdmin):
    list_display = ('get_property_title', 'monthly_rent', 'security_deposit', 'is_currently_rented', 'available_date', 'property_manager')
    list_filter = ('is_currently_rented', 'rental_type', 'available_date', 'created_at')
    search_fields = ('base_property__title', 'base_property__address', 'property_manager__email')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 30
    
    def get_property_title(self, obj):
        return obj.base_property.title if obj.base_property else 'N/A'
    get_property_title.short_description = _('Property Title')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('base_property', 'rental_type', 'monthly_rent', 'security_deposit')
        }),
        (_('Property Details'), {
            'fields': ('bedrooms', 'bathrooms', 'furnished', 'pets_allowed')
        }),
        (_('Availability'), {
            'fields': ('is_currently_rented', 'available_date')
        }),
        (_('Management'), {
            'fields': ('property_manager',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('lease_number', 'get_property_title', 'tenant', 'landlord', 'start_date', 'end_date', 'monthly_rent', 'status')
    list_filter = ('status', 'start_date', 'end_date', 'created_at')
    search_fields = ('lease_number', 'tenant__email', 'landlord__email', 'rental_property__base_property__title')
    readonly_fields = ('lease_number', 'created_at', 'updated_at')
    list_per_page = 30
    date_hierarchy = 'start_date'
    
    def get_property_title(self, obj):
        return obj.rental_property.base_property.title if obj.rental_property and obj.rental_property.base_property else 'N/A'
    get_property_title.short_description = _('Property')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('lease_number', 'rental_property', 'status')
        }),
        (_('Parties'), {
            'fields': ('tenant', 'landlord')
        }),
        (_('Lease Terms'), {
            'fields': ('start_date', 'end_date', 'monthly_rent', 'security_deposit')
        }),
        (_('Additional Terms'), {
            'fields': ('lease_terms', 'special_conditions')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# -------------------------------------------------------------------------
# Maintenance Management Admin
# -------------------------------------------------------------------------

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'title', 'priority', 'status', 'requested_by', 'assigned_to', 'scheduled_date')
    list_filter = ('priority', 'status', 'category', 'created_at', 'scheduled_date')
    search_fields = ('request_number', 'title', 'description', 'requested_by__email', 'related_property__title')
    readonly_fields = ('request_number', 'created_at', 'updated_at')
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def get_priority_color(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red',
            'emergency': 'darkred'
        }
        color = colors.get(obj.priority, 'black')
        return format_html(f'<span style="color: {color};">{obj.get_priority_display()}</span>')
    get_priority_color.short_description = _('Priority')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('request_number', 'title', 'description', 'category', 'priority')
        }),
        (_('Property & People'), {
            'fields': ('related_property', 'requested_by', 'assigned_to')
        }),
        (_('Status & Scheduling'), {
            'fields': ('status', 'scheduled_date', 'completed_date')
        }),
        (_('Cost Information'), {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        (_('Additional Info'), {
            'fields': ('vendor_notes', 'internal_notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'vendor_type', 'rating', 'is_active', 'is_preferred')
    list_filter = ('vendor_type', 'is_active', 'is_preferred', 'rating', 'created_at')
    search_fields = ('company_name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 30
    
    fieldsets = (
        (_('Company Information'), {
            'fields': ('company_name', 'vendor_type', 'description')
        }),
        (_('Contact Information'), {
            'fields': ('contact_person', 'email', 'phone', 'address')
        }),
        (_('Business Details'), {
            'fields': ('license_number', 'insurance_info', 'rating')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_preferred')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# -------------------------------------------------------------------------
# Contract Management Admin
# -------------------------------------------------------------------------

@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('contract_type', 'is_active', 'created_at')
    search_fields = ('name', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 30
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'contract_type')
        }),
        (_('Template Content'), {
            'fields': ('template_content',)
        }),
        (_('Status & Creator'), {
            'fields': ('is_active', 'created_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'title', 'primary_party', 'secondary_party', 'status', 'effective_date', 'expiration_date')
    list_filter = ('status', 'effective_date', 'expiration_date', 'created_at')
    search_fields = ('contract_number', 'title', 'primary_party__email', 'secondary_party__email')
    readonly_fields = ('contract_number', 'created_at', 'updated_at')
    list_per_page = 30
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('contract_number', 'title', 'template')
        }),
        (_('Parties'), {
            'fields': ('primary_party', 'secondary_party')
        }),
        (_('Contract Details'), {
            'fields': ('content', 'status')
        }),
        (_('Dates'), {
            'fields': ('effective_date', 'expiration_date')
        }),
        (_('Signatures'), {
            'fields': ('primary_signed', 'secondary_signed', 'signed_date')
        }),
        (_('Related Information'), {
            'fields': ('related_property', 'lease')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# -------------------------------------------------------------------------
# Analytics Admin
# -------------------------------------------------------------------------

@admin.register(PropertyAnalytics)
class PropertyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('get_property_title', 'occupancy_rate', 'total_income_ytd', 'total_expenses_ytd', 'net_income_ytd', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('base_property__title', 'base_property__address')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 30
    
    def get_property_title(self, obj):
        return obj.base_property.title if obj.base_property else 'N/A'
    get_property_title.short_description = _('Property')
    
    fieldsets = (
        (_('Property'), {
            'fields': ('base_property',)
        }),
        (_('Financial Metrics'), {
            'fields': ('total_income_ytd', 'total_expenses_ytd', 'net_income_ytd')
        }),
        (_('Occupancy Metrics'), {
            'fields': ('occupancy_rate', 'vacancy_days_ytd')
        }),
        (_('Maintenance Metrics'), {
            'fields': ('maintenance_requests_ytd', 'maintenance_cost_ytd')
        }),
        (_('Performance Metrics'), {
            'fields': ('roi_percentage', 'performance_score')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
