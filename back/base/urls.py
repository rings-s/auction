from django.urls import path
from . import views

# Arabic slug converter
class ArabicSlugConverter:
    regex = r'[-\w\u0600-\u06FF]+'
    
    def to_python(self, value):
        if not value:
            raise ValueError("Invalid slug value")
        return value
    
    def to_url(self, value):
        if not value:
            raise ValueError("Invalid slug value")
        return value

from django.urls import register_converter
register_converter(ArabicSlugConverter, 'arabicslug')

urlpatterns = [
    # Locations
    path('locations/', views.LocationListCreateView.as_view(), name='locations'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location'),
    
    # Media
    path('media/', views.MediaListCreateView.as_view(), name='media'),
    path('media/<int:pk>/', views.MediaDetailView.as_view(), name='media-detail'),
    
    # Properties
    path('properties/', views.PropertyListCreateView.as_view(), name='properties'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property'),
    path('properties/<arabicslug:slug>/', views.PropertySlugDetailView.as_view(), name='property-by-slug'),
    
    # Rooms
    path('rooms/', views.RoomListCreateView.as_view(), name='rooms'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room'),
    
    # Auctions
    path('auctions/', views.AuctionListCreateView.as_view(), name='auctions'),
    path('auctions/<int:pk>/', views.AuctionDetailView.as_view(), name='auction'),
    path('auctions/<arabicslug:slug>/', views.AuctionSlugDetailView.as_view(), name='auction-by-slug'),
    
    # Bids
    path('bids/', views.BidListCreateView.as_view(), name='bids'),
    path('bids/<int:pk>/', views.BidDetailView.as_view(), name='bid'),
]