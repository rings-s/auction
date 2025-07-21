# back/base/filters.py
from django_filters import rest_framework as filters
from .models import Auction, Property, RentalProperty, MaintenanceRequest, Expense, Worker



class PropertyFilterSet(filters.FilterSet):
    # Existing filters
    min_price = filters.NumberFilter(field_name="market_value", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="market_value", lookup_expr='lte')
    min_size = filters.NumberFilter(field_name="size_sqm", lookup_expr='gte')
    max_size = filters.NumberFilter(field_name="size_sqm", lookup_expr='lte')
    
    city = filters.CharFilter(field_name="location__city", lookup_expr='icontains')
    state = filters.CharFilter(field_name="location__state", lookup_expr='icontains')
    
    class Meta:
        model = Property
        fields = {
            'property_type': ['exact'],
            'building_type': ['exact'],
            'status': ['exact'],
            'is_featured': ['exact'],
            'is_verified': ['exact'],
            'owner': ['exact'],
        }

class AuctionFilterSet(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="starting_bid", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="starting_bid", lookup_expr='lte')
    property_city = filters.CharFilter(field_name="related_property__location__city", lookup_expr='icontains')
    
    class Meta:
        model = Auction
        fields = {
            'auction_type': ['exact'],
            'status': ['exact'],
            'related_property': ['exact'],
        }

class RentalPropertyFilterSet(filters.FilterSet):
    min_rent = filters.NumberFilter(field_name="monthly_rent", lookup_expr='gte')
    max_rent = filters.NumberFilter(field_name="monthly_rent", lookup_expr='lte')
    city = filters.CharFilter(field_name="base_property__location__city", lookup_expr='icontains')
    
    class Meta:
        model = RentalProperty
        fields = {
            'rental_status': ['exact'],
            'rental_type': ['exact'],
            'furnished': ['exact'],
            'pets_allowed': ['exact'],
        }

class MaintenanceRequestFilterSet(filters.FilterSet):
    reported_after = filters.DateFilter(field_name="reported_date", lookup_expr='gte')
    reported_before = filters.DateFilter(field_name="reported_date", lookup_expr='lte')
    
    class Meta:
        model = MaintenanceRequest
        fields = {
            'status': ['exact'],
            'priority': ['exact'],
            'category': ['exact'],
            'maintenance_property': ['exact'],
            'emergency_repair': ['exact'],
        }

class ExpenseFilterSet(filters.FilterSet):
    expense_after = filters.DateFilter(field_name="expense_date", lookup_expr='gte')
    expense_before = filters.DateFilter(field_name="expense_date", lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr='lte')
    
    class Meta:
        model = Expense
        fields = {
            'status': ['exact'],
            'expense_type': ['exact'],
            'category': ['exact'],
            'expense_property': ['exact'],
            'is_recurring': ['exact'],
        }

class WorkerFilterSet(filters.FilterSet):
    class Meta:
        model = Worker
        fields = {
            'status': ['exact'],
            'employment_type': ['exact'],
            'is_available': ['exact'],
            'categories': ['exact'],
            'management_company': ['exact'],
        }