from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend

from .models import Media, Property, Room, Auction, Bid, Location
from .serializers import (
    MediaSerializer, PropertySerializer, RoomSerializer,
    AuctionSerializer, BidSerializer, LocationSerializer
)
from .permissions import (
    IsVerifiedUser, IsAppraiser, IsDataEntry, IsObjectOwner,
    IsPropertyOwner, IsAppraiserOrDataEntry,
    IsPropertyOwnerOrAppraiserOrDataEntry, IsPropertyOwnerOrAppraiser,
    IsAdminUser
)

# Location Views
class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city', 'state', 'country']
    search_fields = ['city', 'state', 'country']

class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsVerifiedUser, IsAdminUser]

# Media Views
class MediaListCreateView(generics.ListCreateAPIView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['media_type', 'is_primary']
    search_fields = ['name']

class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsObjectOwner()]

# Property Views
class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property_type', 'building_type', 'status', 'location__city']
    search_fields = ['title', 'deed_number', 'location__city']

    def get_queryset(self):
        return Property.objects.select_related(
            'owner', 'location'
        ).prefetch_related('rooms').filter(
            is_published=True
        ).order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertySerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Property.objects.select_related(
            'owner', 'location'
        ).prefetch_related('rooms')

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsPropertyOwnerOrAppraiserOrDataEntry()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count when retrieving property details
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class PropertySlugDetailView(PropertyDetailView):
    lookup_field = 'slug'

# Room Views
class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['property', 'room_type', 'floor']
    search_fields = ['name']

    def get_queryset(self):
        return Room.objects.select_related('property')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAppraiserOrDataEntry()]
        return [IsAuthenticated()]

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.select_related('property')
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAppraiserOrDataEntry()]

# Auction Views
class AuctionListCreateView(generics.ListCreateAPIView):
    serializer_class = AuctionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction_type', 'status', 'related_property']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Auction.objects.select_related(
            'related_property'
        ).prefetch_related('bids').filter(
            is_published=True
        ).order_by('-start_date')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsPropertyOwnerOrAppraiser()]
        return [AllowAny()]

class AuctionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AuctionSerializer

    def get_queryset(self):
        return Auction.objects.select_related(
            'related_property'
        ).prefetch_related('bids')

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsObjectOwner()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count when retrieving auction details
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class AuctionSlugDetailView(AuctionDetailView):
    lookup_field = 'slug'

# Bid Views
class BidListCreateView(generics.ListCreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['auction', 'status']
    search_fields = ['auction__title']

    def get_queryset(self):
        return Bid.objects.select_related('auction', 'bidder')

class BidDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.select_related('auction', 'bidder')
    serializer_class = BidSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsObjectOwner()]