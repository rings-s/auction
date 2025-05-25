import logging
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework import permissions as drf_permissions
from rest_framework.permissions import SAFE_METHODS
from django.utils import timezone
from django.db import transaction, models
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
import django_filters.rest_framework as drf_django_filters
from rest_framework.views import APIView

from .models import Media, Property, Room, Auction, Bid, Location, Message
from .serializers import (
    MediaSerializer, PropertySerializer, RoomSerializer, AuctionSerializer, 
    BidSerializer, LocationSerializer, MessageSerializer, MessageReplySerializer
)
from .permissions import (
    IsVerifiedUser, IsObjectOwner, IsPropertyOwnerOrAppraiserOrDataEntry,
    IsPropertyOwnerOrAppraiser, IsAdminUser, IsMediaManager, 
    IsMessageParticipant, CanSendMessages, IsAppraiserOrDataEntry
)
from .filters import AuctionFilterSet, PropertyFilterSet

logger = logging.getLogger(__name__)

class BaseListCreateView(generics.ListCreateAPIView):
    filter_backends = [drf_django_filters.DjangoFilterBackend, filters.SearchFilter]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class BaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

# Location Views
class LocationListCreateView(BaseListCreateView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filterset_fields = ['city', 'state', 'country']
    search_fields = ['city', 'state', 'country']

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated()] if self.request.method == 'POST' else [drf_permissions.AllowAny()]

class LocationDetailView(BaseDetailView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    
    def get_permissions(self):
        return [drf_permissions.AllowAny()] if self.request.method in SAFE_METHODS else [IsAdminUser()]

# Media Views
class MediaListCreateView(BaseListCreateView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer
    filterset_fields = ['media_type', 'is_primary']
    search_fields = ['name']

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated()] if self.request.method == 'POST' else [drf_permissions.AllowAny()]

class MediaDetailView(BaseDetailView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer

    def get_permissions(self):
        return [drf_permissions.AllowAny()] if self.request.method in SAFE_METHODS else [drf_permissions.IsAuthenticated(), IsMediaManager()]

# Property Views
class PropertyListCreateView(BaseListCreateView):
    serializer_class = PropertySerializer
    filterset_class = PropertyFilterSet
    search_fields = ['title', 'deed_number', 'location__city']

    def get_queryset(self):
        return Property.objects.select_related('owner', 'location').prefetch_related('rooms').filter(is_published=True).order_by('-created_at')

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()] if self.request.method == 'POST' else [drf_permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PropertyDetailView(BaseDetailView):
    serializer_class = PropertySerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Property.objects.select_related('owner', 'location').prefetch_related('rooms')

    def get_permissions(self):
        return [drf_permissions.AllowAny()] if self.request.method in SAFE_METHODS else [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiserOrDataEntry()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class PropertySlugDetailView(PropertyDetailView):
    lookup_field = 'slug'

# Room Views
class RoomListCreateView(BaseListCreateView):
    queryset = Room.objects.select_related('property', 'property__owner', 'property__location')
    serializer_class = RoomSerializer
    filterset_fields = ['property', 'room_type', 'name']
    search_fields = ['name', 'description']

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated()] if self.request.method == 'POST' else [drf_permissions.AllowAny()]

class RoomDetailView(BaseDetailView):
    queryset = Room.objects.select_related('property', 'property__owner', 'property__location')
    serializer_class = RoomSerializer

    def get_permissions(self):
        return [drf_permissions.AllowAny()] if self.request.method in SAFE_METHODS else [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiserOrDataEntry()]

# Auction Views
class AuctionListCreateView(BaseListCreateView):
    serializer_class = AuctionSerializer
    filterset_class = AuctionFilterSet
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Auction.objects.select_related('related_property', 'related_property__location').prefetch_related('media', 'bids').order_by('-created_at')

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiser()] if self.request.method == 'POST' else [drf_permissions.AllowAny()]

class AuctionDetailView(BaseDetailView):
    serializer_class = AuctionSerializer

    def get_queryset(self):
        return Auction.objects.select_related('related_property').prefetch_related('bids')

    def get_permissions(self):
        return [drf_permissions.AllowAny()] if self.request.method in SAFE_METHODS else [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiser()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class AuctionSlugDetailView(AuctionDetailView):
    lookup_field = 'slug'

# Bid Views
class BidListCreateView(BaseListCreateView):
    serializer_class = BidSerializer
    permission_classes = [drf_permissions.IsAuthenticated, IsVerifiedUser]
    filterset_fields = ['auction', 'status']
    search_fields = ['auction__title']

    def get_queryset(self):
        return Bid.objects.select_related('auction', 'bidder').order_by('-bid_time')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        auction_id = request.data.get('auction')
        bid_amount = request.data.get('bid_amount')
        
        if not all([auction_id, bid_amount]):
            return Response({'error': 'Auction and bid amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bid_amount = float(bid_amount)
            if bid_amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response({'error': 'Invalid bid amount'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auction = Auction.objects.get(id=auction_id)
        except Auction.DoesNotExist:
            return Response({'error': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)

        if not auction.can_accept_bids():
            return Response({'error': 'Auction is not accepting bids'}, status=status.HTTP_400_BAD_REQUEST)

        current_bid = auction.current_bid or auction.starting_bid
        minimum_required = float(current_bid) + float(auction.minimum_increment)
        
        if bid_amount < minimum_required:
            return Response({'error': f'Bid must be at least ${minimum_required:,.2f}'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bid = serializer.save(bidder=request.user, ip_address=request.META.get('REMOTE_ADDR'), is_verified=request.user.is_verified)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BidDetailView(BaseDetailView):
    queryset = Bid.objects.select_related('auction', 'bidder')
    serializer_class = BidSerializer

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated()] if self.request.method in SAFE_METHODS else [IsObjectOwner()]

# Message Views
class MessageListCreateView(BaseListCreateView):
    serializer_class = MessageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, CanSendMessages]
    filterset_fields = ['status', 'priority', 'related_property']
    search_fields = ['subject', 'body', 'sender__email', 'recipient__email']
    ordering_fields = ['created_at', 'read_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(models.Q(sender=user) | models.Q(recipient=user)).select_related('sender', 'recipient', 'related_property')
        
        box_type = self.request.query_params.get('box', 'all')
        if box_type == 'inbox':
            queryset = queryset.filter(recipient=user)
        elif box_type == 'sent':
            queryset = queryset.filter(sender=user)
        elif box_type == 'unread':
            queryset = queryset.filter(recipient=user, status='unread')
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessageDetailView(BaseDetailView):
    serializer_class = MessageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, IsMessageParticipant]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(models.Q(sender=user) | models.Q(recipient=user)).select_related('sender', 'recipient', 'related_property')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.recipient == request.user and instance.status == 'unread':
            instance.mark_as_read()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class MessageReplyView(generics.CreateAPIView):
    serializer_class = MessageReplySerializer
    permission_classes = [drf_permissions.IsAuthenticated, CanSendMessages]

class PropertyOwnerContactView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [drf_permissions.IsAuthenticated, CanSendMessages]

    def create(self, request, *args, **kwargs):
        property_id = kwargs.get('property_id')
        
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not property_obj.owner or property_obj.owner == request.user:
            return Response({'error': 'Cannot send message to yourself or property has no owner'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        data['related_property'] = property_obj.id
        data['subject'] = data.get('subject', f"Inquiry about {property_obj.title}")
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, recipient=property_obj.owner)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageStatsView(APIView):
    """API endpoint to get message statistics for user"""
    permission_classes = [drf_permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        stats = {
            'total_messages': Message.objects.filter(
                models.Q(sender=user) | models.Q(recipient=user)
            ).count(),
            'unread_count': Message.objects.filter(
                recipient=user, status='unread'
            ).count(),
            'sent_count': Message.objects.filter(sender=user).count(),
            'received_count': Message.objects.filter(recipient=user).count(),
            'threads_count': Message.objects.filter(
                models.Q(sender=user) | models.Q(recipient=user),
                parent_message__isnull=True
            ).values('thread_id').distinct().count()
        }
        
        return create_response(data=stats)