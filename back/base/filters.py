# back/base/filters.py
from django_filters import rest_framework as filters
from .models import Auction, Property

class PropertyFilterSet(filters.FilterSet):
    # Existing filters
    min_price = filters.NumberFilter(field_name="market_value", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="market_value", lookup_expr='lte')
    min_size = filters.NumberFilter(field_name="size_sqm", lookup_expr='gte')
    max_size = filters.NumberFilter(field_name="size_sqm", lookup_expr='lte')
    
    # Additional aliases for backwards compatibility (optional)
    market_value__gte = filters.NumberFilter(field_name="market_value", lookup_expr='gte')
    market_value__lte = filters.NumberFilter(field_name="market_value", lookup_expr='lte')
    size_sqm__gte = filters.NumberFilter(field_name="size_sqm", lookup_expr='gte')
    size_sqm__lte = filters.NumberFilter(field_name="size_sqm", lookup_expr='lte')
    
    city = filters.CharFilter(field_name="location__city", lookup_expr='icontains')
    state = filters.CharFilter(field_name="location__state", lookup_expr='icontains')
    
    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('market_value', 'market_value'),
            ('size_sqm', 'size_sqm'),
            ('view_count', 'view_count'),
        )
    )

    class Meta:
        model = Property
        fields = {
            'property_type': ['exact'],
            'building_type': ['exact'],
            'status': ['exact'],
            'is_featured': ['exact'],
            'is_verified': ['exact'],
        }

class AuctionFilterSet(filters.FilterSet):
    # Existing filters
    min_price = filters.NumberFilter(field_name="starting_bid", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="starting_bid", lookup_expr='lte')
    
    # Additional aliases for backwards compatibility (optional)
    starting_bid__gte = filters.NumberFilter(field_name="starting_bid", lookup_expr='gte')
    starting_bid__lte = filters.NumberFilter(field_name="starting_bid", lookup_expr='lte')
    
    property_city = filters.CharFilter(field_name="related_property__location__city", lookup_expr='icontains')

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('end_date', 'end_date'),
            ('starting_bid', 'starting_bid'),
            ('bid_count', 'bid_count'),
        )
    )

    class Meta:
        model = Auction
        fields = {
            'auction_type': ['exact'],
            'status': ['exact'],
            'related_property': ['exact'],
        }