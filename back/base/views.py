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

from .models import *
from .serializers import *
from .permissions import *
from .filters import AuctionFilterSet, PropertyFilterSet


from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, Sum, Avg, Max, Min
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model

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
class MediaListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing media files or uploading new ones.
    Media can be linked to various models (Property, Auction, etc.) via GenericForeignKey.
    """
    queryset = Media.objects.select_related('content_type') # Optimizes DB query by fetching related ContentType.
    serializer_class = MediaSerializer
    permission_classes = [drf_permissions.AllowAny] # Base permission, refined by get_permissions for POST.
    filter_backends = [drf_django_filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['media_type', 'is_primary']
    search_fields = ['name']

    def get_permissions(self):
        if self.request.method == 'POST':
            # Authenticated users can upload media.
            return [drf_permissions.IsAuthenticated()] 
        # Anyone can list media.
        return [drf_permissions.AllowAny()] 

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def create(self, request, *args, **kwargs):
        """Custom create logic to automatically set the media owner to the logged-in user."""
        try:
            # Log the incoming data for debugging
            print(f"Media create - FILES: {request.FILES}")
            print(f"Media create - DATA: {request.data}")
            
            # If the model field is sent without app_label, add "base." prefix
            content_type_str = request.data.get('content_type_str')
            if content_type_str and '.' not in content_type_str:
                # List known content types to help with debugging
                content_types = ContentType.objects.all()
                print(f"Available content types: {[(ct.app_label, ct.model) for ct in content_types]}")
                
                # For any model in the base app, add the base. prefix
                base_app_models = ['property', 'room', 'auction', 'bid', 'location', 'media']
                if content_type_str.lower() in base_app_models:
                    request.data['content_type_str'] = f'base.{content_type_str.lower()}'
                    print(f"Updated content_type_str from '{content_type_str}' to 'base.{content_type_str.lower()}'")
                    
            # Continue with normal handling
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=request.user) # Sets the owner during save.
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"Error in MediaListCreateView.create: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response(
                {"error": {"message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )

class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for managing a specific media file.
    """
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.AllowAny()] 
        # For write operations (PUT, PATCH, DELETE), use custom IsMediaManager permission.
        return [drf_permissions.IsAuthenticated(), IsMediaManager()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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
        # Remove the is_published filter to show all auctions
        queryset = Auction.objects.select_related('related_property', 'related_property__location').prefetch_related('media', 'bids')
        
        # Auto-update status for all auctions
        for auction in queryset:
            auction.update_status_based_on_time()
        
        return queryset.order_by('-created_at')
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

class AuctionStatusView(APIView):
    """Simple endpoint to check and update auction status"""
    permission_classes = [drf_permissions.AllowAny]
    
    def get(self, request, auction_id):
        try:
            auction = Auction.objects.get(id=auction_id)
            old_status = auction.status
            auction.update_status_based_on_time()
            
            return Response({
                'id': auction.id,
                'status': auction.status,
                'status_display': auction.get_status_display(),
                'is_biddable': auction.is_biddable(),
                'is_active': auction.is_active(),
                'time_remaining': auction.time_remaining,
                'current_bid': float(auction.get_current_high_bid()),
                'minimum_next_bid': float(auction.get_minimum_next_bid()),
                'status_changed': old_status != auction.status
            })
        except Auction.DoesNotExist:
            return Response({'error': 'Auction not found'}, status=404)


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
        
        # Basic validation
        try:
            auction = Auction.objects.select_for_update().get(id=auction_id)
            bid_amount = float(bid_amount)
        except (Auction.DoesNotExist, ValueError, TypeError):
            return Response({
                'error': 'Invalid auction or bid amount',
                'code': 'INVALID_REQUEST'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if auction can accept bids (includes auto-activation)
        if not auction.is_biddable():
            return Response({
                'error': f'Auction is {auction.get_status_display().lower()} and not accepting bids',
                'code': 'AUCTION_NOT_ACTIVE',
                'auction_status': auction.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate minimum bid
        current_high = auction.current_bid or auction.starting_bid
        min_bid = float(current_high) + float(auction.minimum_increment)
        
        if bid_amount < min_bid:
            return Response({
                'error': f'Minimum bid is ${min_bid:,.2f}',
                'code': 'BID_TOO_LOW',
                'minimum_bid': min_bid,
                'current_bid': float(current_high)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the bid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bid = serializer.save(
            bidder=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            is_verified=getattr(request.user, 'is_verified', False),
            status='accepted'  # Auto-accept valid bids
        )
        
        return Response({
            'message': 'Bid placed successfully',
            'bid': serializer.data,
            'auction_status': auction.status
        }, status=status.HTTP_201_CREATED)




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

    def create(self, request, *args, **kwargs):
        logger.info(f"MessageListCreateView create called. Request data: {request.data}")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"MessageListCreateView create successful. Response data: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Exception in MessageListCreateView create: {type(e).__name__} - {str(e)}", exc_info=True)
            # Re-raise the exception to let DRF handle it or be caught by a custom handler
            raise

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
        # ADD THIS LINE - provide the recipient_email that the serializer expects
        data['recipient_email'] = property_obj.owner.email
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # Remove the manual recipient setting since the serializer handles it now
        serializer.save(sender=request.user)
        
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
        
        return Response(data=stats)







class UserDashboardView(APIView):
    """Main dashboard view for authenticated users"""
    permission_classes = [drf_permissions.IsAuthenticated, CanAccessDashboard]
    
    def get(self, request):
        user = request.user
        
        # Get user-accessible data based on role
        properties = user.get_accessible_properties()
        auctions = user.get_accessible_auctions()
        bids = user.get_accessible_bids()
        
        # Calculate date ranges
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Property statistics
        property_stats = {
            'total_properties': properties.count(),
            'published_properties': properties.filter(is_published=True).count(),
            'draft_properties': properties.filter(is_published=False).count(),
            'featured_properties': properties.filter(is_featured=True).count(),
            'verified_properties': properties.filter(is_verified=True).count(),
            'properties_value': properties.aggregate(Sum('market_value'))['market_value__sum'] or 0,
        }
        
        # Auction statistics
        auction_stats = {
            'total_auctions': auctions.count(),
            'active_auctions': auctions.filter(status='live').count(),
            'scheduled_auctions': auctions.filter(status='scheduled').count(),
            'ended_auctions': auctions.filter(status='ended').count(),
        }
        
        # Bid statistics
        bid_stats = {
            'total_bids': bids.count(),
            'winning_bids': bids.filter(status='winning').count(),
            'total_bid_amount': bids.aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0,
        }
        
        # Activity statistics
        activity_stats = {
            'recent_properties': properties.filter(created_at__gte=week_ago).count(),
            'recent_auctions': auctions.filter(created_at__gte=week_ago).count(),
            'recent_bids': bids.filter(created_at__gte=week_ago).count(),
            'messages_unread': Message.objects.filter(recipient=user, status='unread').count(),
        }
        
        # Role-specific stats
        role_stats = {}
        if user.role in ['appraiser', 'data_entry']:
            role_stats.update({
                'properties_this_month': properties.filter(created_at__gte=month_ago).count(),
                'auctions_this_month': auctions.filter(created_at__gte=month_ago).count(),
                'avg_property_value': properties.aggregate(Avg('market_value'))['market_value__avg'] or 0,
            })
        
        # Combine all stats
        dashboard_data = {
            'user_priority': user.get_dashboard_priority(),
            'user_role': user.role,
            'user_role_display': user.get_role_display(),
            **property_stats,
            **auction_stats,
            **bid_stats,
            **activity_stats,
            **role_stats,
        }
        
        serializer = UserDashboardStatsSerializer(dashboard_data)
        return Response(serializer.data)

class SystemDashboardView(APIView):
    """System-wide dashboard for admins and appraisers"""
    permission_classes = [drf_permissions.IsAuthenticated, CanAccessAdvancedDashboard]
    
    def get(self, request):
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # User statistics
        user_stats = {
            'total_users': User.objects.count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'active_users_today': User.objects.filter(last_login__date=today).count(),
            'new_users_this_week': User.objects.filter(date_joined__gte=week_ago).count(),
        }
        
        # Property statistics
        properties = Property.objects.all()
        property_stats = {
            'total_properties': properties.count(),
            'published_properties': properties.filter(is_published=True).count(),
            'properties_this_month': properties.filter(created_at__gte=month_ago).count(),
            'avg_property_value': properties.aggregate(Avg('market_value'))['market_value__avg'] or 0,
            'highest_property_value': properties.aggregate(Max('market_value'))['market_value__max'] or 0,
        }
        
        # Auction statistics
        auctions = Auction.objects.all()
        auction_stats = {
            'total_auctions': auctions.count(),
            'active_auctions': auctions.filter(status='live').count(),
            'completed_auctions': auctions.filter(status='completed').count(),
            'total_auction_value': auctions.aggregate(Sum('current_bid'))['current_bid__sum'] or 0,
        }
        
        # Bid statistics
        bids = Bid.objects.all()
        bid_stats = {
            'total_bids': bids.count(),
            'unique_bidders': bids.values('bidder').distinct().count(),
            'total_bid_value': bids.aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0,
            'avg_bid_amount': bids.aggregate(Avg('bid_amount'))['bid_amount__avg'] or 0,
        }
        
        # Activity statistics
        activity_stats = {
            'bids_today': bids.filter(created_at__date=today).count(),
            'auctions_ending_soon': auctions.filter(
                end_date__gte=now,
                end_date__lte=now + timedelta(hours=24),
                status='live'
            ).count(),
            'pending_verifications': properties.filter(is_verified=False).count(),
        }
        
        # Geographic statistics
        top_cities = Location.objects.annotate(
            property_count=Count('properties')
        ).filter(property_count__gt=0).order_by('-property_count')[:5]
        
        top_cities_data = [
            {'city': loc.city, 'state': loc.state, 'count': loc.property_count}
            for loc in top_cities
        ]
        
        # Combine all stats
        dashboard_data = {
            **user_stats,
            **property_stats,
            **auction_stats,
            **bid_stats,
            **activity_stats,
            'top_cities': top_cities_data,
        }
        
        serializer = SystemDashboardStatsSerializer(dashboard_data)
        return Response(serializer.data)

class RecentActivityView(APIView):
    """Recent activity feed for dashboard"""
    permission_classes = [drf_permissions.IsAuthenticated, CanAccessDashboard]
    
    def get(self, request):
        user = request.user
        limit = int(request.query_params.get('limit', 20))
        
        activities = []
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        # Get recent properties based on user access
        properties = user.get_accessible_properties().filter(created_at__gte=week_ago)
        for prop in properties[:10]:
            activities.append({
                'activity_type': 'property',
                'title': f'New Property: {prop.title}',
                'description': f'Property added in {prop.location.city if prop.location else "Unknown"}',
                'timestamp': prop.created_at,
                'related_id': prop.id,
                'related_slug': prop.slug,
                'priority': 'medium' if prop.is_featured else 'low',
                'user_name': f'{prop.owner.first_name} {prop.owner.last_name}' if prop.owner else 'Unknown'
            })
        
        # Get recent auctions
        auctions = user.get_accessible_auctions().filter(created_at__gte=week_ago)
        for auction in auctions[:10]:
            priority = 'high' if auction.status == 'live' else 'medium'
            activities.append({
                'activity_type': 'auction',
                'title': f'Auction: {auction.title}',
                'description': f'Status: {auction.get_status_display()}',
                'timestamp': auction.created_at,
                'related_id': auction.id,
                'related_slug': auction.slug,
                'priority': priority,
            })
        
        # Get recent bids
        bids = user.get_accessible_bids().filter(created_at__gte=week_ago)
        for bid in bids[:10]:
            priority = 'urgent' if bid.status == 'winning' else 'medium'
            activities.append({
                'activity_type': 'bid',
                'title': f'Bid: ${bid.bid_amount:,.2f}',
                'description': f'On {bid.auction.title}',
                'timestamp': bid.created_at,
                'related_id': bid.id,
                'priority': priority,
                'user_name': bid.bidder_name
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        activities = activities[:limit]
        
        serializer = RecentActivitySerializer(activities, many=True)
        return Response(serializer.data)

class DashboardPropertiesView(generics.ListAPIView):
    """Properties for dashboard with pagination"""
    serializer_class = PropertyDashboardSerializer
    permission_classes = [drf_permissions.IsAuthenticated, CanAccessDashboard]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'property_number', 'location__city']
    ordering_fields = ['created_at', 'market_value', 'view_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = user.get_accessible_properties().select_related('location')
        
        # Filter by status if requested
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by verification status
        verified = self.request.query_params.get('verified')
        if verified is not None:
            queryset = queryset.filter(is_verified=verified.lower() == 'true')
            
        return queryset

class DashboardAuctionsView(generics.ListAPIView):
    """Auctions for dashboard with pagination"""
    serializer_class = AuctionDashboardSerializer
    permission_classes = [drf_permissions.IsAuthenticated, CanAccessDashboard]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'related_property__title']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'bid_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = user.get_accessible_auctions().select_related('related_property')
        
        # Filter by status if requested
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter active auctions
        active_only = self.request.query_params.get('active_only')
        if active_only and active_only.lower() == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                status='live',
                start_date__lte=now,
                end_date__gt=now
            )
            
        return queryset

class DashboardBidsView(generics.ListAPIView):
    """Bids for dashboard with pagination"""
    serializer_class = BidDashboardSerializer
    permission_classes = [drf_permissions.IsAuthenticated, CanAccessDashboard]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['auction__title', 'auction__related_property__title']
    ordering_fields = ['created_at', 'bid_amount', 'bid_time']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = user.get_accessible_bids().select_related('auction', 'auction__related_property', 'bidder')
        
        # Filter by status if requested
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter winning bids only
        winning_only = self.request.query_params.get('winning_only')
        if winning_only and winning_only.lower() == 'true':
            queryset = queryset.filter(status='winning')
            
        return queryset