# core/filters.py
from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta
from .models import (
    FinancialTransaction, PropertyExpense, RentalProperty, 
    Lease, MaintenanceRequest, Vendor, Contract
)

class FinancialTransactionFilterSet(filters.FilterSet):
    """Filter set for financial transactions"""
    
    # Amount filters
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr='lte')
    amount_range = filters.RangeFilter(field_name="amount")
    
    # Date filters
    due_date_from = filters.DateFilter(field_name="due_date", lookup_expr='gte')
    due_date_to = filters.DateFilter(field_name="due_date", lookup_expr='lte')
    paid_date_from = filters.DateFilter(field_name="paid_date", lookup_expr='gte')
    paid_date_to = filters.DateFilter(field_name="paid_date", lookup_expr='lte')
    
    # Status filters
    is_overdue = filters.BooleanFilter(method='filter_overdue')
    
    # Property filters
    property_title = filters.CharFilter(field_name="related_property__title", lookup_expr='icontains')
    property_location = filters.CharFilter(field_name="related_property__location__city", lookup_expr='icontains')
    
    # User filters
    payer_name = filters.CharFilter(method='filter_payer_name')
    payee_name = filters.CharFilter(method='filter_payee_name')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('due_date', 'due_date'),
            ('paid_date', 'paid_date'),
            ('amount', 'amount'),
            ('status', 'status'),
        )
    )

    class Meta:
        model = FinancialTransaction
        fields = {
            'transaction_type': ['exact', 'in'],
            'status': ['exact', 'in'],
            'related_property': ['exact'],
        }

    def filter_overdue(self, queryset, name, value):
        """Filter overdue transactions"""
        if value:
            return queryset.filter(
                due_date__lt=timezone.now().date(),
                status='pending'
            )
        return queryset

    def filter_payer_name(self, queryset, name, value):
        """Filter by payer name"""
        return queryset.filter(
            payer__first_name__icontains=value
        ).union(
            queryset.filter(payer__last_name__icontains=value)
        ).union(
            queryset.filter(payer__email__icontains=value)
        )

    def filter_payee_name(self, queryset, name, value):
        """Filter by payee name"""
        return queryset.filter(
            payee__first_name__icontains=value
        ).union(
            queryset.filter(payee__last_name__icontains=value)
        ).union(
            queryset.filter(payee__email__icontains=value)
        )

class PropertyExpenseFilterSet(filters.FilterSet):
    """Filter set for property expenses"""
    
    # Amount filters
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr='lte')
    amount_range = filters.RangeFilter(field_name="amount")
    
    # Date filters
    expense_date_from = filters.DateFilter(field_name="expense_date", lookup_expr='gte')
    expense_date_to = filters.DateFilter(field_name="expense_date", lookup_expr='lte')
    this_month = filters.BooleanFilter(method='filter_this_month')
    this_year = filters.BooleanFilter(method='filter_this_year')
    
    # Property filters
    property_title = filters.CharFilter(field_name="related_property__title", lookup_expr='icontains')
    property_location = filters.CharFilter(field_name="related_property__location__city", lookup_expr='icontains')
    
    # Vendor filters
    vendor_name = filters.CharFilter(field_name="vendor_name", lookup_expr='icontains')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('expense_date', 'expense_date'),
            ('amount', 'amount'),
            ('category', 'category'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = PropertyExpense
        fields = {
            'category': ['exact', 'in'],
            'is_recurring': ['exact'],
            'related_property': ['exact'],
        }

    def filter_this_month(self, queryset, name, value):
        """Filter expenses from this month"""
        if value:
            now = timezone.now()
            return queryset.filter(
                expense_date__year=now.year,
                expense_date__month=now.month
            )
        return queryset

    def filter_this_year(self, queryset, name, value):
        """Filter expenses from this year"""
        if value:
            return queryset.filter(expense_date__year=timezone.now().year)
        return queryset

class RentalPropertyFilterSet(filters.FilterSet):
    """Filter set for rental properties"""
    
    # Rent filters
    min_rent = filters.NumberFilter(field_name="monthly_rent", lookup_expr='gte')
    max_rent = filters.NumberFilter(field_name="monthly_rent", lookup_expr='lte')
    rent_range = filters.RangeFilter(field_name="monthly_rent")
    
    # Property features
    min_bedrooms = filters.NumberFilter(field_name="bedrooms", lookup_expr='gte')
    max_bedrooms = filters.NumberFilter(field_name="bedrooms", lookup_expr='lte')
    min_bathrooms = filters.NumberFilter(field_name="bathrooms", lookup_expr='gte')
    max_bathrooms = filters.NumberFilter(field_name="bathrooms", lookup_expr='lte')
    
    # Location filters
    city = filters.CharFilter(field_name="base_property__location__city", lookup_expr='icontains')
    state = filters.CharFilter(field_name="base_property__location__state", lookup_expr='icontains')
    
    # Availability filters
    available_from = filters.DateFilter(field_name="available_date", lookup_expr='gte')
    available_to = filters.DateFilter(field_name="available_date", lookup_expr='lte')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('monthly_rent', 'monthly_rent'),
            ('available_date', 'available_date'),
            ('bedrooms', 'bedrooms'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = RentalProperty
        fields = {
            'rental_type': ['exact', 'in'],
            'furnished': ['exact'],
            'pets_allowed': ['exact'],
            'is_currently_rented': ['exact'],
            'base_property__property_type': ['exact'],
        }

class LeaseFilterSet(filters.FilterSet):
    """Filter set for lease agreements"""
    
    # Date filters
    start_date_from = filters.DateFilter(field_name="start_date", lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name="start_date", lookup_expr='lte')
    end_date_from = filters.DateFilter(field_name="end_date", lookup_expr='gte')
    end_date_to = filters.DateFilter(field_name="end_date", lookup_expr='lte')
    
    # Status filters
    expiring_soon = filters.BooleanFilter(method='filter_expiring_soon')
    active = filters.BooleanFilter(method='filter_active')
    
    # Rent filters
    min_rent = filters.NumberFilter(field_name="monthly_rent", lookup_expr='gte')
    max_rent = filters.NumberFilter(field_name="monthly_rent", lookup_expr='lte')
    
    # Property filters
    property_title = filters.CharFilter(field_name="rental_property__base_property__title", lookup_expr='icontains')
    property_location = filters.CharFilter(field_name="rental_property__base_property__location__city", lookup_expr='icontains')
    
    # Party filters
    tenant_name = filters.CharFilter(method='filter_tenant_name')
    landlord_name = filters.CharFilter(method='filter_landlord_name')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('start_date', 'start_date'),
            ('end_date', 'end_date'),
            ('monthly_rent', 'monthly_rent'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = Lease
        fields = {
            'status': ['exact', 'in'],
            'tenant_signed': ['exact'],
            'landlord_signed': ['exact'],
        }

    def filter_expiring_soon(self, queryset, name, value):
        """Filter leases expiring in next 30 days"""
        if value:
            thirty_days = timezone.now().date() + timedelta(days=30)
            return queryset.filter(
                end_date__lte=thirty_days,
                status='active'
            )
        return queryset

    def filter_active(self, queryset, name, value):
        """Filter active leases"""
        if value:
            today = timezone.now().date()
            return queryset.filter(
                status='active',
                start_date__lte=today,
                end_date__gte=today
            )
        return queryset

    def filter_tenant_name(self, queryset, name, value):
        """Filter by tenant name"""
        return queryset.filter(
            tenant__first_name__icontains=value
        ).union(
            queryset.filter(tenant__last_name__icontains=value)
        )

    def filter_landlord_name(self, queryset, name, value):
        """Filter by landlord name"""
        return queryset.filter(
            landlord__first_name__icontains=value
        ).union(
            queryset.filter(landlord__last_name__icontains=value)
        )

class MaintenanceRequestFilterSet(filters.FilterSet):
    """Filter set for maintenance requests"""
    
    # Date filters
    requested_date_from = filters.DateFilter(field_name="requested_date", lookup_expr='gte')
    requested_date_to = filters.DateFilter(field_name="requested_date", lookup_expr='lte')
    scheduled_date_from = filters.DateFilter(field_name="scheduled_date", lookup_expr='gte')
    scheduled_date_to = filters.DateFilter(field_name="scheduled_date", lookup_expr='lte')
    
    # Cost filters
    min_estimated_cost = filters.NumberFilter(field_name="estimated_cost", lookup_expr='gte')
    max_estimated_cost = filters.NumberFilter(field_name="estimated_cost", lookup_expr='lte')
    min_actual_cost = filters.NumberFilter(field_name="actual_cost", lookup_expr='gte')
    max_actual_cost = filters.NumberFilter(field_name="actual_cost", lookup_expr='lte')
    
    # Property filters
    property_title = filters.CharFilter(field_name="related_property__title", lookup_expr='icontains')
    property_location = filters.CharFilter(field_name="related_property__location__city", lookup_expr='icontains')
    
    # User filters
    requested_by_name = filters.CharFilter(method='filter_requested_by_name')
    assigned_to_name = filters.CharFilter(method='filter_assigned_to_name')
    
    # Status filters
    urgent = filters.BooleanFilter(method='filter_urgent')
    overdue = filters.BooleanFilter(method='filter_overdue')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('priority', 'priority'),
            ('status', 'status'),
            ('scheduled_date', 'scheduled_date'),
            ('estimated_cost', 'estimated_cost'),
            ('actual_cost', 'actual_cost'),
        )
    )

    class Meta:
        model = MaintenanceRequest
        fields = {
            'category': ['exact', 'in'],
            'priority': ['exact', 'in'],
            'status': ['exact', 'in'],
            'related_property': ['exact'],
        }

    def filter_urgent(self, queryset, name, value):
        """Filter urgent requests"""
        if value:
            return queryset.filter(priority__in=['high', 'emergency'])
        return queryset

    def filter_overdue(self, queryset, name, value):
        """Filter overdue maintenance requests"""
        if value:
            return queryset.filter(
                scheduled_date__lt=timezone.now().date(),
                status__in=['submitted', 'in_progress']
            )
        return queryset

    def filter_requested_by_name(self, queryset, name, value):
        """Filter by requester name"""
        return queryset.filter(
            requested_by__first_name__icontains=value
        ).union(
            queryset.filter(requested_by__last_name__icontains=value)
        )

    def filter_assigned_to_name(self, queryset, name, value):
        """Filter by assigned person name"""
        return queryset.filter(
            assigned_to__first_name__icontains=value
        ).union(
            queryset.filter(assigned_to__last_name__icontains=value)
        )

class VendorFilterSet(filters.FilterSet):
    """Filter set for vendors"""
    
    # Rating filters
    min_rating = filters.NumberFilter(field_name="rating", lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name="rating", lookup_expr='lte')
    
    # Cost filters
    min_hourly_rate = filters.NumberFilter(field_name="hourly_rate", lookup_expr='gte')
    max_hourly_rate = filters.NumberFilter(field_name="hourly_rate", lookup_expr='lte')
    
    # Search filters
    search = filters.CharFilter(method='filter_search')
    company_name = filters.CharFilter(field_name="company_name", lookup_expr='icontains')
    contact_person = filters.CharFilter(field_name="contact_person", lookup_expr='icontains')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('company_name', 'company_name'),
            ('rating', 'rating'),
            ('hourly_rate', 'hourly_rate'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = Vendor
        fields = {
            'vendor_type': ['exact', 'in'],
            'is_active': ['exact'],
            'is_preferred': ['exact'],
        }

    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            company_name__icontains=value
        ).union(
            queryset.filter(contact_person__icontains=value)
        ).union(
            queryset.filter(vendor_type__icontains=value)
        )

class ContractFilterSet(filters.FilterSet):
    """Filter set for contracts"""
    
    # Date filters
    effective_date_from = filters.DateFilter(field_name="effective_date", lookup_expr='gte')
    effective_date_to = filters.DateFilter(field_name="effective_date", lookup_expr='lte')
    expiration_date_from = filters.DateFilter(field_name="expiration_date", lookup_expr='gte')
    expiration_date_to = filters.DateFilter(field_name="expiration_date", lookup_expr='lte')
    
    # Status filters
    expiring_soon = filters.BooleanFilter(method='filter_expiring_soon')
    fully_signed = filters.BooleanFilter(method='filter_fully_signed')
    
    # Property filters
    property_title = filters.CharFilter(field_name="related_property__title", lookup_expr='icontains')
    
    # Party filters
    primary_party_name = filters.CharFilter(method='filter_primary_party_name')
    secondary_party_name = filters.CharFilter(method='filter_secondary_party_name')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('effective_date', 'effective_date'),
            ('expiration_date', 'expiration_date'),
            ('created_at', 'created_at'),
            ('status', 'status'),
        )
    )

    class Meta:
        model = Contract
        fields = {
            'status': ['exact', 'in'],
            'template__contract_type': ['exact', 'in'],
            'primary_signed': ['exact'],
            'secondary_signed': ['exact'],
        }

    def filter_expiring_soon(self, queryset, name, value):
        """Filter contracts expiring in next 30 days"""
        if value:
            thirty_days = timezone.now().date() + timedelta(days=30)
            return queryset.filter(
                expiration_date__lte=thirty_days,
                status__in=['signed', 'pending']
            )
        return queryset

    def filter_fully_signed(self, queryset, name, value):
        """Filter fully signed contracts"""
        if value:
            return queryset.filter(
                primary_signed=True,
                secondary_signed=True
            )
        return queryset

    def filter_primary_party_name(self, queryset, name, value):
        """Filter by primary party name"""
        return queryset.filter(
            primary_party__first_name__icontains=value
        ).union(
            queryset.filter(primary_party__last_name__icontains=value)
        )

    def filter_secondary_party_name(self, queryset, name, value):
        """Filter by secondary party name"""
        return queryset.filter(
            secondary_party__first_name__icontains=value
        ).union(
            queryset.filter(secondary_party__last_name__icontains=value)
        )