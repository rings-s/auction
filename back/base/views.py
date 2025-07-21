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


from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum, Avg, Max, Min
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
import json
# Data visualization imports moved to functions to avoid startup errors
# import pandas as pd
# import numpy as np  
# import plotly.graph_objects as go
# import plotly.express as px
# from plotly.utils import PlotlyJSONEncoder

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

class BaseCreateView(generics.CreateAPIView):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class BaseAPIView(APIView):
    """Base API view with common functionality"""
    permission_classes = [drf_permissions.IsAuthenticated]
    
    def handle_exception(self, exc):
        logger.error(f"Error in {self.__class__.__name__}: {str(exc)}")
        return super().handle_exception(exc)

class BaseDashboardView(generics.ListAPIView):
    """Base dashboard view with common dashboard functionality"""
    
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

class MediaDetailView(BaseDetailView):
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

class AuctionStatusView(BaseAPIView):
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

class MessageReplyView(BaseCreateView):
    serializer_class = MessageReplySerializer
    permission_classes = [drf_permissions.IsAuthenticated, CanSendMessages]

class PropertyOwnerContactView(BaseCreateView):
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

class MessageStatsView(BaseAPIView):
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







class UserDashboardView(BaseAPIView):
    """Enhanced main dashboard view for authenticated users"""
    
    def get(self, request):
        user = request.user
        
        # Get cached or calculate new metrics
        dashboard_data = DashboardMetrics.get_or_calculate(
            user=user,
            metric_type='user_dashboard',
            calculator_func=self._calculate_user_dashboard,
            expires_in_hours=1
        )
        
        return Response(dashboard_data)
    
    def _calculate_user_dashboard(self, user):
        """Calculate comprehensive user dashboard data"""
        # Get user-accessible data based on role
        properties = user.get_accessible_properties()
        auctions = user.get_accessible_auctions()
        bids = user.get_accessible_bids()
        
        # Calculate date ranges
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Property statistics
        property_stats = self._calculate_property_stats(properties, week_ago, month_ago)
        
        # Auction statistics
        auction_stats = self._calculate_auction_stats(auctions, week_ago, month_ago)
        
        # Bid statistics
        bid_stats = self._calculate_bid_stats(bids, week_ago, month_ago)
        
        # Rental management statistics (if applicable)
        rental_stats = self._calculate_rental_stats(user, properties)
        
        # Maintenance statistics
        maintenance_stats = self._calculate_maintenance_stats(user, properties)
        
        # Financial summary
        financial_stats = self._calculate_financial_stats(user, properties)
        
        # Recent activity
        recent_activity = self._get_recent_activity_data(user, week_ago)
        
        # Alerts and notifications
        alerts = self._get_user_alerts(user)
        
        return {
            'user_info': {
                'id': user.id,
                'role': user.role,
                'role_display': user.get_role_display(),
                'dashboard_priority': user.get_dashboard_priority(),
            },
            'property_stats': property_stats,
            'auction_stats': auction_stats,
            'bid_stats': bid_stats,
            'rental_stats': rental_stats,
            'maintenance_stats': maintenance_stats,
            'financial_stats': financial_stats,
            'recent_activity': recent_activity,
            'alerts': alerts,
            'last_updated': timezone.now().isoformat(),
        }
    
    def _calculate_property_stats(self, properties, week_ago, month_ago):
        """Calculate property statistics"""
        return {
            'total_properties': properties.count(),
            'published_properties': properties.filter(is_published=True).count(),
            'draft_properties': properties.filter(is_published=False).count(),
            'featured_properties': properties.filter(is_featured=True).count(),
            'verified_properties': properties.filter(is_verified=True).count(),
            'properties_value': float(properties.aggregate(Sum('market_value'))['market_value__sum'] or 0),
            'recent_properties': properties.filter(created_at__gte=week_ago).count(),
            'monthly_properties': properties.filter(created_at__gte=month_ago).count(),
            'avg_property_value': float(properties.aggregate(Avg('market_value'))['market_value__avg'] or 0),
            'status_breakdown': {
                'available': properties.filter(status='available').count(),
                'under_contract': properties.filter(status='under_contract').count(),
                'sold': properties.filter(status='sold').count(),
                'auction': properties.filter(status='auction').count(),
            },
            'type_breakdown': list(properties.values('property_type').annotate(
                count=Count('id'),
                avg_value=Avg('market_value')
            ).order_by('-count'))
        }
    
    def _calculate_auction_stats(self, auctions, week_ago, month_ago):
        """Calculate auction statistics"""
        return {
            'total_auctions': auctions.count(),
            'active_auctions': auctions.filter(status='live').count(),
            'scheduled_auctions': auctions.filter(status='scheduled').count(),
            'ended_auctions': auctions.filter(status='ended').count(),
            'completed_auctions': auctions.filter(status='completed').count(),
            'recent_auctions': auctions.filter(created_at__gte=week_ago).count(),
            'monthly_auctions': auctions.filter(created_at__gte=month_ago).count(),
            'total_auction_value': float(auctions.aggregate(Sum('current_bid'))['current_bid__sum'] or 0),
            'avg_starting_bid': float(auctions.aggregate(Avg('starting_bid'))['starting_bid__avg'] or 0),
        }
    
    def _calculate_bid_stats(self, bids, week_ago, month_ago):
        """Calculate bid statistics"""
        return {
            'total_bids': bids.count(),
            'winning_bids': bids.filter(status='winning').count(),
            'accepted_bids': bids.filter(status='accepted').count(),
            'total_bid_amount': float(bids.aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0),
            'recent_bids': bids.filter(created_at__gte=week_ago).count(),
            'monthly_bids': bids.filter(created_at__gte=month_ago).count(),
            'avg_bid_amount': float(bids.aggregate(Avg('bid_amount'))['bid_amount__avg'] or 0),
        }
    
    def _calculate_rental_stats(self, user, properties):
        """Calculate rental management statistics"""
        rental_properties = RentalProperty.objects.filter(base_property__in=properties)
        
        if not rental_properties.exists():
            return {'has_rentals': False}
        
        total_units = rental_properties.count()
        occupied_units = rental_properties.filter(rental_status='rented').count()
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        return {
            'has_rentals': True,
            'total_units': total_units,
            'occupied_units': occupied_units,
            'available_units': rental_properties.filter(rental_status='available').count(),
            'maintenance_units': rental_properties.filter(rental_status='maintenance').count(),
            'occupancy_rate': round(occupancy_rate, 2),
            'total_monthly_rent': float(rental_properties.aggregate(Sum('monthly_rent'))['monthly_rent__sum'] or 0),
            'occupied_monthly_rent': float(rental_properties.filter(rental_status='rented').aggregate(Sum('monthly_rent'))['monthly_rent__sum'] or 0),
        }
    
    def _calculate_maintenance_stats(self, user, properties):
        """Calculate maintenance statistics"""
        maintenance_requests = MaintenanceRequest.objects.filter(property__in=properties)
        
        return {
            'total_requests': maintenance_requests.count(),
            'pending_requests': maintenance_requests.filter(status='pending').count(),
            'in_progress_requests': maintenance_requests.filter(status='in_progress').count(),
            'completed_requests': maintenance_requests.filter(status='completed').count(),
            'urgent_requests': maintenance_requests.filter(priority='urgent').count(),
            'overdue_requests': maintenance_requests.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'assigned', 'in_progress']
            ).count(),
            'total_maintenance_cost': float(maintenance_requests.filter(
                status='completed'
            ).aggregate(Sum('actual_cost'))['actual_cost__sum'] or 0),
        }
    
    def _calculate_financial_stats(self, user, properties):
        """Calculate financial statistics"""
        current_month = timezone.now().replace(day=1)
        current_year = timezone.now().replace(month=1, day=1)
        
        # Get expenses
        monthly_expenses = Expense.objects.filter(
            property__in=properties,
            expense_date__gte=current_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        yearly_expenses = Expense.objects.filter(
            property__in=properties,
            expense_date__gte=current_year
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Get rental income
        rental_income = RentalProperty.objects.filter(
            base_property__in=properties,
            rental_status='rented'
        ).aggregate(total=Sum('monthly_rent'))['total'] or 0
        
        return {
            'monthly_expenses': float(monthly_expenses),
            'yearly_expenses': float(yearly_expenses),
            'monthly_rental_income': float(rental_income),
            'annual_rental_income': float(rental_income * 12),
            'net_monthly_income': float(rental_income) - float(monthly_expenses),
            'property_value': float(properties.aggregate(Sum('market_value'))['market_value__sum'] or 0),
        }
    
    def _get_recent_activity_data(self, user, week_ago):
        """Get recent activity data"""
        activities = []
        
        # Recent properties
        recent_properties = user.get_accessible_properties().filter(created_at__gte=week_ago)[:5]
        for prop in recent_properties:
            activities.append({
                'type': 'property',
                'title': f'New Property: {prop.title}',
                'timestamp': prop.created_at,
                'id': prop.id,
            })
        
        # Recent auctions
        recent_auctions = user.get_accessible_auctions().filter(created_at__gte=week_ago)[:5]
        for auction in recent_auctions:
            activities.append({
                'type': 'auction',
                'title': f'New Auction: {auction.title}',
                'timestamp': auction.created_at,
                'id': auction.id,
            })
        
        # Recent bids
        recent_bids = user.get_accessible_bids().filter(created_at__gte=week_ago)[:5]
        for bid in recent_bids:
            activities.append({
                'type': 'bid',
                'title': f'Bid: ${bid.bid_amount:,.2f}',
                'timestamp': bid.created_at,
                'id': bid.id,
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:10]
    
    def _get_user_alerts(self, user):
        """Get user alerts and notifications"""
        alerts = []
        properties = user.get_accessible_properties()
        
        # Maintenance alerts
        urgent_maintenance = MaintenanceRequest.objects.filter(
            property__in=properties,
            priority='urgent',
            status__in=['pending', 'assigned']
        ).count()
        
        if urgent_maintenance > 0:
            alerts.append({
                'type': 'urgent',
                'message': f'{urgent_maintenance} urgent maintenance requests need attention',
                'count': urgent_maintenance
            })
        
        # Lease expiration alerts
        if hasattr(user, 'owned_properties'):
            rental_properties = RentalProperty.objects.filter(base_property__in=properties)
            next_month = timezone.now().date() + timedelta(days=30)
            
            expiring_leases = Lease.objects.filter(
                rental_property__in=rental_properties,
                status='active',
                end_date__lte=next_month
            ).count()
            
            if expiring_leases > 0:
                alerts.append({
                    'type': 'warning',
                    'message': f'{expiring_leases} leases expiring in the next 30 days',
                    'count': expiring_leases
                })
        
        # Auction ending alerts
        ending_auctions = user.get_accessible_auctions().filter(
            status='live',
            end_date__lte=timezone.now() + timedelta(hours=24)
        ).count()
        
        if ending_auctions > 0:
            alerts.append({
                'type': 'info',
                'message': f'{ending_auctions} auctions ending in the next 24 hours',
                'count': ending_auctions
            })
        
        return alerts


class SystemDashboardView(BaseAPIView):
    """Enhanced system-wide dashboard for admins and appraisers"""
    permission_classes = [drf_permissions.IsAuthenticated, CanAccessAdvancedDashboard]
    
    def get(self, request):
        user = request.user
        
        # Get cached or calculate system metrics
        dashboard_data = DashboardMetrics.get_or_calculate(
            user=user,
            metric_type='system_dashboard',
            calculator_func=self._calculate_system_dashboard,
            expires_in_hours=2  # System data can be cached longer
        )
        
        return Response(dashboard_data)
    
    def _calculate_system_dashboard(self, user):
        """Calculate system-wide dashboard metrics"""
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
            'user_roles': list(User.objects.values('role').annotate(count=Count('id')).order_by('-count')),
        }
        
        # Property statistics
        properties = Property.objects.all()
        property_stats = {
            'total_properties': properties.count(),
            'published_properties': properties.filter(is_published=True).count(),
            'verified_properties': properties.filter(is_verified=True).count(),
            'properties_this_month': properties.filter(created_at__gte=month_ago).count(),
            'avg_property_value': float(properties.aggregate(Avg('market_value'))['market_value__avg'] or 0),
            'highest_property_value': float(properties.aggregate(Max('market_value'))['market_value__max'] or 0),
            'total_property_value': float(properties.aggregate(Sum('market_value'))['market_value__sum'] or 0),
        }
        
        # Auction statistics
        auctions = Auction.objects.all()
        auction_stats = {
            'total_auctions': auctions.count(),
            'active_auctions': auctions.filter(status='live').count(),
            'completed_auctions': auctions.filter(status='completed').count(),
            'total_auction_value': float(auctions.aggregate(Sum('current_bid'))['current_bid__sum'] or 0),
            'auctions_this_month': auctions.filter(created_at__gte=month_ago).count(),
        }
        
        # Bid statistics
        bids = Bid.objects.all()
        bid_stats = {
            'total_bids': bids.count(),
            'unique_bidders': bids.values('bidder').distinct().count(),
            'total_bid_value': float(bids.aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0),
            'avg_bid_amount': float(bids.aggregate(Avg('bid_amount'))['bid_amount__avg'] or 0),
            'bids_today': bids.filter(created_at__date=today).count(),
        }
        
        # Activity statistics
        activity_stats = {
            'auctions_ending_soon': auctions.filter(
                end_date__gte=now,
                end_date__lte=now + timedelta(hours=24),
                status='live'
            ).count(),
            'pending_verifications': properties.filter(is_verified=False).count(),
            'maintenance_requests_today': MaintenanceRequest.objects.filter(
                reported_date__date=today
            ).count(),
        }
        
        # Geographic statistics
        top_cities = Location.objects.annotate(
            property_count=Count('properties')
        ).filter(property_count__gt=0).order_by('-property_count')[:10]
        
        geographic_stats = [
            {
                'city': loc.city,
                'state': loc.state,
                'property_count': loc.property_count,
                'avg_value': float(properties.filter(location=loc).aggregate(
                    avg=Avg('market_value')
                )['avg'] or 0)
            }
            for loc in top_cities
        ]
        
        # Financial overview
        total_expenses = Expense.objects.filter(
            expense_date__gte=month_ago
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        financial_stats = {
            'monthly_expenses': float(total_expenses),
            'total_rental_income': float(RentalProperty.objects.filter(
                rental_status='rented'
            ).aggregate(total=Sum('monthly_rent'))['total'] or 0) * 12,
        }
        
        return {
            'user_stats': user_stats,
            'property_stats': property_stats,
            'auction_stats': auction_stats,
            'bid_stats': bid_stats,
            'activity_stats': activity_stats,
            'geographic_stats': geographic_stats,
            'financial_stats': financial_stats,
            'last_updated': timezone.now().isoformat(),
        }


class RecentActivityView(BaseAPIView):
    """Recent activity feed for dashboard"""
    
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

class DashboardPropertiesView(BaseDashboardView):
    """Properties for dashboard with pagination"""
    serializer_class = PropertyDashboardSerializer
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

class DashboardAuctionsView(BaseDashboardView):
    """Auctions for dashboard with pagination"""
    serializer_class = AuctionDashboardSerializer
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

class DashboardBidsView(BaseDashboardView):
    """Bids for dashboard with pagination"""
    serializer_class = BidDashboardSerializer
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


class DashboardWorkersView(BaseDashboardView):
    """Dashboard view for worker management"""
    serializer_class = WorkerBriefSerializer
    permission_classes = [CanManageWorkers]  # Override base permission
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'employee_id']
    ordering_fields = ['created_at', 'rating', 'total_jobs_completed']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Worker.objects.filter(status='active').prefetch_related('categories')
    
    def list(self, request, *args, **kwargs):
        """Enhanced list with dashboard metrics"""
        queryset = self.get_queryset()
        
        # Calculate worker metrics
        metrics = DashboardMetrics.get_or_calculate(
            user=request.user,
            metric_type='worker_dashboard',
            calculator_func=lambda user: self._calculate_worker_metrics(queryset),
            expires_in_hours=1
        )
        
        # Get paginated worker list
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            result.data['metrics'] = metrics
            return result
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'workers': serializer.data,
            'metrics': metrics
        })
    
    def _calculate_worker_metrics(self, queryset):
        """Calculate worker dashboard metrics"""
        total_workers = queryset.count()
        available_workers = queryset.filter(is_available=True).count()
        
        # Performance metrics
        avg_rating = queryset.aggregate(avg=Avg('rating'))['avg'] or 0
        total_jobs = queryset.aggregate(total=Sum('total_jobs_completed'))['total'] or 0
        
        # Category breakdown
        categories = WorkerCategory.objects.annotate(
            worker_count=Count('workers', filter=Q(workers__status='active'))
        ).order_by('-worker_count')[:5]
        
        return {
            'total_workers': total_workers,
            'available_workers': available_workers,
            'busy_workers': total_workers - available_workers,
            'average_rating': round(float(avg_rating), 2),
            'total_jobs_completed': total_jobs,
            'top_categories': [
                {
                    'name': cat.name,
                    'worker_count': cat.worker_count,
                    'hourly_rate_range': {
                        'min': float(cat.hourly_rate_min),
                        'max': float(cat.hourly_rate_max)
                    }
                }
                for cat in categories
            ]
        }


class DashboardCompaniesView(BaseDashboardView):
    """Dashboard view for property management companies"""
    serializer_class = PropertyManagementCompanySerializer
    permission_classes = [drf_permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'registration_number', 'city']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return PropertyManagementCompany.objects.filter(is_active=True)
    
    def list(self, request, *args, **kwargs):
        """Enhanced list with company metrics"""
        queryset = self.get_queryset()
        
        # Calculate company metrics
        metrics = {
            'total_companies': queryset.count(),
            'verified_companies': queryset.filter(is_verified=True).count(),
            'total_managed_properties': Property.objects.filter(
                management_company__in=queryset
            ).count(),
            'total_workers': Worker.objects.filter(
                management_company__in=queryset,
                status='active'
            ).count(),
            'average_rating': float(queryset.aggregate(
                avg=Avg('rating')
            )['avg'] or 0),
        }
        
        response = super().list(request, *args, **kwargs)
        response.data['metrics'] = metrics
        return response


class DashboardAnalyticsView(BaseDashboardView):
    """Dashboard view for property analytics"""
    serializer_class = PropertyAnalyticsSerializer
    permission_classes = [CanAccessPropertyAnalytics]  # Override base permission
    
    def get_queryset(self):
        user = self.request.user
        accessible_properties = user.get_accessible_properties()
        return PropertyAnalytics.objects.filter(base_property__in=accessible_properties)
    
    def list(self, request, *args, **kwargs):
        """Enhanced analytics with performance metrics"""
        queryset = self.get_queryset()
        
        # Calculate analytics summary
        analytics_summary = DashboardMetrics.get_or_calculate(
            user=request.user,
            metric_type='analytics_dashboard',
            calculator_func=lambda user: self._calculate_analytics_summary(queryset),
            expires_in_hours=2
        )
        
        response = super().list(request, *args, **kwargs)
        response.data['analytics_summary'] = analytics_summary
        return response
    
    def _calculate_analytics_summary(self, queryset):
        """Calculate analytics dashboard summary"""
        if not queryset.exists():
            return {}
        
        return {
            'total_properties_analyzed': queryset.count(),
            'average_roi': float(queryset.aggregate(avg=Avg('roi_percentage'))['avg'] or 0),
            'average_occupancy': float(queryset.aggregate(avg=Avg('occupancy_rate'))['avg'] or 0),
            'total_revenue': float(queryset.aggregate(total=Sum('total_revenue'))['total'] or 0),
            'total_expenses': float(queryset.aggregate(total=Sum('total_expenses'))['total'] or 0),
            'net_income': float(queryset.aggregate(total=Sum('net_income'))['total'] or 0),
            'best_performing_property': queryset.order_by('-roi_percentage').first(),
            'worst_performing_property': queryset.order_by('roi_percentage').first(),
        }


class DashboardWorkflowsView(BaseDashboardView):
    """Dashboard view for maintenance workflows"""
    serializer_class = PropertyMaintenanceWorkflowSerializer
    filterset_fields = ['current_status', 'workflow_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        accessible_properties = user.get_accessible_properties()
        return PropertyMaintenanceWorkflow.objects.filter(
            maintenance_request__property__in=accessible_properties
        ).select_related('maintenance_request')
    
    def list(self, request, *args, **kwargs):
        """Enhanced workflow list with status metrics"""
        queryset = self.get_queryset()
        
        # Calculate workflow metrics
        workflow_metrics = {
            'total_workflows': queryset.count(),
            'active_workflows': queryset.exclude(current_status__in=['completed', 'cancelled']).count(),
            'completed_workflows': queryset.filter(current_status='completed').count(),
            'escalated_workflows': queryset.filter(escalation_level__gt=0).count(),
            'average_completion_time': queryset.filter(
                completion_time__isnull=False
            ).aggregate(avg=Avg('completion_time'))['avg'],
            'status_breakdown': list(queryset.values('current_status').annotate(
                count=Count('id')
            ).order_by('-count')),
        }
        
        response = super().list(request, *args, **kwargs)
        response.data['workflow_metrics'] = workflow_metrics
        return response


# -------------------------------------------------------------------------
# Property Management API Views
# -------------------------------------------------------------------------

class RentalPropertyListCreateView(BaseListCreateView):
    """API for rental property management"""
    serializer_class = RentalPropertySerializer
    filterset_fields = ['rental_status', 'rental_type', 'furnished', 'pets_allowed']
    search_fields = ['property__title', 'property__address', 'property__location__city']
    ordering_fields = ['monthly_rent', 'created_at', 'property__market_value']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        base_properties = user.get_accessible_properties()
        return RentalProperty.objects.filter(
            property__in=base_properties
        ).select_related('property', 'property__location', 'property__owner').prefetch_related('leases')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]
        return [drf_permissions.AllowAny()]

    def perform_create(self, serializer):
        # Ensure the user can create rental properties for this property
        property_obj = serializer.validated_data['property']
        if not self.request.user.get_accessible_properties().filter(id=property_obj.id).exists():
            raise PermissionDenied("You don't have permission to manage this property")
        serializer.save()


class RentalPropertyDetailView(BaseDetailView):
    """API for individual rental property management"""
    serializer_class = RentalPropertySerializer
    
    def get_queryset(self):
        user = self.request.user
        base_properties = user.get_accessible_properties()
        return RentalProperty.objects.filter(
            property__in=base_properties
        ).select_related('property', 'property__location', 'property__owner').prefetch_related('leases')

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.AllowAny()]
        return [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiserOrDataEntry()]


class TenantListCreateView(BaseListCreateView):
    """API for tenant management"""
    serializer_class = TenantSerializer
    filterset_fields = ['status', 'tenant_type']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'national_id']
    ordering_fields = ['created_at', 'last_name', 'move_in_date']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return Tenant.objects.all().select_related('user').prefetch_related('leases')
        elif user.role == 'owner':
            # Owners can see tenants of their properties
            return Tenant.objects.filter(
                leases__rental_property__property__owner=user
            ).distinct().select_related('user').prefetch_related('leases')
        elif user.role == 'tenant':
            # Tenants can only see their own profile
            return Tenant.objects.filter(user=user).select_related('user').prefetch_related('leases')
        return Tenant.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Create tenant profile
        tenant = serializer.save()
        
        # Optionally link to user account if email matches
        user_email = serializer.validated_data.get('email')
        if user_email:
            try:
                user = User.objects.get(email=user_email)
                if not hasattr(user, 'tenant_profile'):
                    tenant.user = user
                    tenant.save()
            except User.DoesNotExist:
                pass


class TenantDetailView(BaseDetailView):
    """API for individual tenant management"""
    serializer_class = TenantSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return Tenant.objects.all().select_related('user').prefetch_related('leases')
        elif user.role == 'owner':
            return Tenant.objects.filter(
                leases__rental_property__property__owner=user
            ).distinct().select_related('user').prefetch_related('leases')
        elif user.role == 'tenant':
            return Tenant.objects.filter(user=user).select_related('user').prefetch_related('leases')
        return Tenant.objects.none()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]


class LeaseListCreateView(BaseListCreateView):
    """API for lease management"""
    serializer_class = LeaseSerializer
    filterset_fields = ['status', 'tenant', 'rental_property']
    search_fields = ['lease_number', 'tenant__first_name', 'tenant__last_name', 'rental_property__property__title']
    ordering_fields = ['start_date', 'end_date', 'monthly_rent', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return Lease.objects.all().select_related('tenant', 'rental_property__property', 'rental_property__property__location')
        elif user.role == 'owner':
            return Lease.objects.filter(
                rental_property__property__owner=user
            ).select_related('tenant', 'rental_property__property', 'rental_property__property__location')
        elif user.role == 'tenant':
            return Lease.objects.filter(
                tenant__user=user
            ).select_related('tenant', 'rental_property__property', 'rental_property__property__location')
        return Lease.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Validate property ownership
        rental_property = serializer.validated_data['rental_property']
        if self.request.user.role == 'owner':
            if rental_property.property.owner != self.request.user:
                raise PermissionDenied("You can only create leases for your own properties")
        serializer.save()


class LeaseDetailView(BaseDetailView):
    """API for individual lease management"""
    serializer_class = LeaseSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return Lease.objects.all().select_related('tenant', 'rental_property__property')
        elif user.role == 'owner':
            return Lease.objects.filter(
                rental_property__property__owner=user
            ).select_related('tenant', 'rental_property__property')
        elif user.role == 'tenant':
            return Lease.objects.filter(
                tenant__user=user
            ).select_related('tenant', 'rental_property__property')
        return Lease.objects.none()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]


class MaintenanceCategoryListCreateView(BaseListCreateView):
    """API for maintenance categories"""
    queryset = MaintenanceCategory.objects.filter(is_active=True)
    serializer_class = MaintenanceCategorySerializer
    filterset_fields = ['is_active', 'priority_level']
    search_fields = ['name', 'description']
    ordering_fields = ['priority_level', 'name', 'created_at']
    ordering = ['priority_level', 'name']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]
        return [drf_permissions.AllowAny()]


class MaintenanceCategoryDetailView(BaseDetailView):
    """API for individual maintenance category"""
    queryset = MaintenanceCategory.objects.all()
    serializer_class = MaintenanceCategorySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.AllowAny()]
        return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]


class MaintenanceRequestListCreateView(BaseListCreateView):
    """API for maintenance requests"""
    serializer_class = MaintenanceRequestSerializer
    filterset_fields = ['status', 'priority', 'category', 'property', 'emergency_repair']
    search_fields = ['title', 'description', 'property__title', 'specific_location']
    ordering_fields = ['reported_date', 'due_date', 'priority', 'estimated_cost']
    ordering = ['-reported_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return MaintenanceRequest.objects.all().select_related(
                'property', 'category', 'requested_by', 'assigned_to'
            )
        elif user.role == 'owner':
            return MaintenanceRequest.objects.filter(
                property__owner=user
            ).select_related('property', 'category', 'requested_by', 'assigned_to')
        elif user.role == 'tenant':
            return MaintenanceRequest.objects.filter(
                Q(requested_by=user) | Q(property__rental_info__leases__tenant__user=user)
            ).select_related('property', 'category', 'requested_by', 'assigned_to')
        return MaintenanceRequest.objects.none()

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


class MaintenanceRequestDetailView(BaseDetailView):
    """API for individual maintenance request"""
    serializer_class = MaintenanceRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return MaintenanceRequest.objects.all().select_related('property', 'category', 'requested_by', 'assigned_to')
        elif user.role == 'owner':
            return MaintenanceRequest.objects.filter(
                property__owner=user
            ).select_related('property', 'category', 'requested_by', 'assigned_to')
        elif user.role == 'tenant':
            return MaintenanceRequest.objects.filter(
                Q(requested_by=user) | Q(property__rental_info__leases__tenant__user=user)
            ).select_related('property', 'category', 'requested_by', 'assigned_to')
        return MaintenanceRequest.objects.none()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiserOrDataEntry()]


class ExpenseCategoryListCreateView(BaseListCreateView):
    """API for expense categories"""
    queryset = ExpenseCategory.objects.filter(is_active=True)
    serializer_class = ExpenseCategorySerializer
    filterset_fields = ['is_active', 'is_tax_deductible', 'parent_category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]
        return [drf_permissions.AllowAny()]


class ExpenseCategoryDetailView(BaseDetailView):
    """API for individual expense category"""
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.AllowAny()]
        return [drf_permissions.IsAuthenticated(), IsAppraiserOrDataEntry()]


class ExpenseListCreateView(BaseListCreateView):
    """API for expense management"""
    serializer_class = ExpenseSerializer
    filterset_fields = ['status', 'expense_type', 'category', 'property', 'is_recurring', 'is_emergency']
    search_fields = ['title', 'description', 'vendor_name', 'property__title']
    ordering_fields = ['expense_date', 'amount', 'due_date', 'created_at']
    ordering = ['-expense_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return Expense.objects.all().select_related(
                'property', 'category', 'created_by', 'approved_by'
            )
        elif user.role == 'owner':
            return Expense.objects.filter(
                property__owner=user
            ).select_related('property', 'category', 'created_by', 'approved_by')
        return Expense.objects.none()

    def get_permissions(self):
        return [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiserOrDataEntry()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExpenseDetailView(BaseDetailView):
    """API for individual expense management"""
    serializer_class = ExpenseSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return Expense.objects.all().select_related('property', 'category', 'created_by', 'approved_by')
        elif user.role == 'owner':
            return Expense.objects.filter(
                property__owner=user
            ).select_related('property', 'category', 'created_by', 'approved_by')
        return Expense.objects.none()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsPropertyOwnerOrAppraiserOrDataEntry()]


# -------------------------------------------------------------------------
# Property Analytics and Reports
# -------------------------------------------------------------------------

class PropertyAnalyticsView(APIView):
    """Property analytics dashboard"""
    
    def get(self, request, property_id=None):
        try:
            # Import data visualization libraries
            import pandas as pd
            import plotly
        except ImportError:
            return Response({
                'error': 'Data visualization libraries not installed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        user = request.user
        
        if property_id:
            # Analytics for specific property
            try:
                property_obj = user.get_accessible_properties().get(id=property_id)
            except Property.DoesNotExist:
                return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
            
            properties = [property_obj]
        else:
            # Analytics for all accessible properties
            properties = user.get_accessible_properties()[:10]  # Limit for performance
        
        if not properties:
            return Response({'error': 'No properties found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate analytics data
        analytics_data = []
        
        for prop in properties:
            # Calculate metrics
            rental_info = getattr(prop, 'rental_info', None)
            if rental_info:
                # Revenue data
                monthly_rent = float(rental_info.monthly_rent)
                annual_income = monthly_rent * 12
                occupancy_rate = rental_info.occupancy_rate
                
                # Expense data
                total_expenses = prop.expenses.filter(
                    expense_date__year=datetime.now().year
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                
                # Maintenance data
                maintenance_cost = prop.expenses.filter(
                    expense_type='maintenance',
                    expense_date__year=datetime.now().year
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                
                maintenance_requests = prop.maintenance_requests.count()
                
                analytics_data.append({
                    'property_id': prop.id,
                    'property_title': prop.title,
                    'monthly_rent': monthly_rent,
                    'annual_income': annual_income,
                    'occupancy_rate': occupancy_rate,
                    'total_expenses': float(total_expenses),
                    'maintenance_cost': float(maintenance_cost),
                    'maintenance_requests': maintenance_requests,
                    'net_income': annual_income - float(total_expenses),
                    'roi': ((annual_income - float(total_expenses)) / float(prop.market_value)) * 100 if prop.market_value else 0
                })
        
        # Create charts
        charts = {}
        
        if analytics_data:
            df = pd.DataFrame(analytics_data)
            
            # Revenue vs Expenses Chart
            fig_revenue = go.Figure()
            fig_revenue.add_trace(go.Bar(
                name='Annual Income',
                x=df['property_title'],
                y=df['annual_income'],
                marker_color='green'
            ))
            fig_revenue.add_trace(go.Bar(
                name='Total Expenses',
                x=df['property_title'],
                y=df['total_expenses'],
                marker_color='red'
            ))
            fig_revenue.update_layout(
                title='Annual Income vs Expenses by Property',
                xaxis_title='Property',
                yaxis_title='Amount (SAR)',
                barmode='group'
            )
            charts['revenue_expenses'] = json.dumps(fig_revenue, cls=PlotlyJSONEncoder)
            
            # Occupancy Rate Chart
            fig_occupancy = px.bar(
                df, x='property_title', y='occupancy_rate',
                title='Occupancy Rate by Property',
                labels={'occupancy_rate': 'Occupancy Rate (%)', 'property_title': 'Property'}
            )
            charts['occupancy'] = json.dumps(fig_occupancy, cls=PlotlyJSONEncoder)
            
            # ROI Chart
            fig_roi = px.bar(
                df, x='property_title', y='roi',
                title='Return on Investment by Property',
                labels={'roi': 'ROI (%)', 'property_title': 'Property'},
                color='roi',
                color_continuous_scale='RdYlGn'
            )
            charts['roi'] = json.dumps(fig_roi, cls=PlotlyJSONEncoder)
        
        return Response({
            'analytics_data': analytics_data,
            'charts': charts,
            'summary': {
                'total_properties': len(analytics_data),
                'total_annual_income': sum(item['annual_income'] for item in analytics_data),
                'total_expenses': sum(item['total_expenses'] for item in analytics_data),
                'average_occupancy': np.mean([item['occupancy_rate'] for item in analytics_data]) if analytics_data else 0,
                'average_roi': np.mean([item['roi'] for item in analytics_data]) if analytics_data else 0,
            }
        })


class ReportGenerationView(APIView):
    """Generate property management reports"""
    
    def post(self, request):
        report_type = request.data.get('report_type', 'financial')
        property_ids = request.data.get('property_ids', [])
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')
        
        if not period_start or not period_end:
            return Response({
                'error': 'period_start and period_end are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create report record
        report = Report.objects.create(
            title=f"{report_type.title()} Report - {period_start} to {period_end}",
            report_type=report_type,
            generated_by=request.user,
            period_start=period_start,
            period_end=period_end,
            status='generating'
        )
        
        # Add properties to report
        if property_ids:
            accessible_properties = request.user.get_accessible_properties().filter(id__in=property_ids)
        else:
            accessible_properties = request.user.get_accessible_properties()
        
        report.properties.set(accessible_properties)
        
        # Generate report data (this could be moved to a background task)
        try:
            report_data = self._generate_report_data(report_type, accessible_properties, period_start, period_end)
            report.report_data = report_data
            report.status = 'completed'
            report.save()
            
            return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
            return Response({
                'error': 'Report generation failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_report_data(self, report_type, properties, period_start, period_end):
        """Generate report data based on type"""
        data = {
            'properties': [],
            'summary': {},
            'period': {'start': period_start, 'end': period_end}
        }
        
        for prop in properties:
            prop_data = {
                'id': prop.id,
                'title': prop.title,
                'address': prop.address,
            }
            
            if report_type == 'financial':
                # Financial report data
                expenses = prop.expenses.filter(
                    expense_date__range=[period_start, period_end]
                )
                rental_info = getattr(prop, 'rental_info', None)
                
                prop_data.update({
                    'total_expenses': expenses.aggregate(total=Sum('total_amount'))['total'] or 0,
                    'monthly_rent': float(rental_info.monthly_rent) if rental_info else 0,
                    'annual_income': float(rental_info.monthly_rent) * 12 if rental_info else 0,
                })
            
            elif report_type == 'maintenance':
                # Maintenance report data
                maintenance_requests = prop.maintenance_requests.filter(
                    reported_date__range=[period_start, period_end]
                )
                
                prop_data.update({
                    'total_requests': maintenance_requests.count(),
                    'completed_requests': maintenance_requests.filter(status='completed').count(),
                    'pending_requests': maintenance_requests.filter(status='pending').count(),
                    'total_maintenance_cost': maintenance_requests.aggregate(
                        total=Sum('actual_cost')
                    )['total'] or 0,
                })
            
            data['properties'].append(prop_data)
        
        return data


class ReportListView(generics.ListAPIView):
    """List generated reports"""
    serializer_class = ReportSerializer
    filterset_fields = ['report_type', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Report.objects.filter(generated_by=self.request.user)


class ReportDetailView(generics.RetrieveAPIView):
    """Retrieve specific report"""
    serializer_class = ReportSerializer
    
    def get_queryset(self):
        return Report.objects.filter(generated_by=self.request.user)


# ========================================================================
# Property Management Dashboard Views
# ========================================================================

class DashboardRentalPropertiesView(APIView):
    """Dashboard view for rental properties overview"""
    
    def get(self, request):
        user = request.user
        
        # Get user-accessible rental properties
        rental_properties = RentalProperty.objects.filter(
            base_property__owner=user
        ).select_related('base_property')
        
        # Calculate statistics
        total_properties = rental_properties.count()
        occupied_properties = rental_properties.filter(rental_status='rented').count()
        available_properties = rental_properties.filter(rental_status='available').count()
        maintenance_properties = rental_properties.filter(rental_status='maintenance').count()
        
        # Financial statistics
        total_monthly_rent = rental_properties.aggregate(
            total=Sum('monthly_rent')
        )['total'] or 0
        
        average_rent = rental_properties.aggregate(
            avg=Avg('monthly_rent')
        )['avg'] or 0
        
        # Calculate occupancy rate
        occupancy_rate = (occupied_properties / total_properties * 100) if total_properties > 0 else 0
        
        data = {
            'total_properties': total_properties,
            'occupied_properties': occupied_properties,
            'available_properties': available_properties,
            'maintenance_properties': maintenance_properties,
            'occupancy_rate': round(occupancy_rate, 2),
            'total_monthly_rent': float(total_monthly_rent),
            'average_rent': float(average_rent),
            'annual_income_estimate': float(total_monthly_rent * 12),
        }
        
        return Response(data)


class DashboardTenantsView(APIView):
    """Dashboard view for tenants overview"""
    
    def get(self, request):
        user = request.user
        
        # Get tenants for user's properties
        user_properties = RentalProperty.objects.filter(
            base_property__owner=user
        ).values_list('id', flat=True)
        
        tenants = Tenant.objects.filter(
            leases__rental_property__in=user_properties
        ).distinct()
        
        # Calculate statistics
        total_tenants = tenants.count()
        active_tenants = tenants.filter(status='active').count()
        inactive_tenants = tenants.filter(status='inactive').count()
        
        # Recent activity
        week_ago = timezone.now() - timedelta(days=7)
        new_tenants = tenants.filter(created_at__gte=week_ago).count()
        
        # Tenant types breakdown
        tenant_types = tenants.values('tenant_type').annotate(
            count=Count('id')
        ).order_by('tenant_type')
        
        data = {
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'inactive_tenants': inactive_tenants,
            'new_tenants_this_week': new_tenants,
            'tenant_types_breakdown': list(tenant_types),
        }
        
        return Response(data)


class DashboardLeasesView(APIView):
    """Dashboard view for leases overview"""
    
    def get(self, request):
        user = request.user
        
        # Get leases for user's properties
        user_properties = RentalProperty.objects.filter(
            base_property__owner=user
        ).values_list('id', flat=True)
        
        leases = Lease.objects.filter(
            rental_property__in=user_properties
        )
        
        # Calculate statistics
        total_leases = leases.count()
        active_leases = leases.filter(status='active').count()
        expired_leases = leases.filter(status='expired').count()
        
        # Expiring soon (next 30 days)
        next_month = timezone.now().date() + timedelta(days=30)
        expiring_soon = leases.filter(
            status='active',
            end_date__lte=next_month
        ).count()
        
        # Financial statistics
        total_monthly_revenue = leases.filter(status='active').aggregate(
            total=Sum('monthly_rent')
        )['total'] or 0
        
        # Lease duration analysis
        avg_duration = leases.aggregate(
            avg_duration=Avg(
                models.F('end_date') - models.F('start_date')
            )
        )['avg_duration']
        
        avg_duration_months = avg_duration.days / 30.44 if avg_duration else 0
        
        data = {
            'total_leases': total_leases,
            'active_leases': active_leases,
            'expired_leases': expired_leases,
            'expiring_soon': expiring_soon,
            'total_monthly_revenue': float(total_monthly_revenue),
            'average_lease_duration_months': round(avg_duration_months, 1),
        }
        
        return Response(data)


class DashboardMaintenanceView(APIView):
    """Dashboard view for maintenance requests overview"""
    
    def get(self, request):
        user = request.user
        
        # Get maintenance requests for user's properties
        user_properties = Property.objects.filter(owner=user).values_list('id', flat=True)
        
        maintenance_requests = MaintenanceRequest.objects.filter(
            base_property__in=user_properties
        )
        
        # Calculate statistics
        total_requests = maintenance_requests.count()
        pending_requests = maintenance_requests.filter(status='pending').count()
        in_progress_requests = maintenance_requests.filter(status='in_progress').count()
        completed_requests = maintenance_requests.filter(status='completed').count()
        
        # Priority breakdown
        urgent_requests = maintenance_requests.filter(priority='urgent').count()
        high_priority_requests = maintenance_requests.filter(priority='high').count()
        
        # Recent activity
        week_ago = timezone.now() - timedelta(days=7)
        new_requests = maintenance_requests.filter(reported_date__gte=week_ago).count()
        
        # Cost analysis
        total_estimated_cost = maintenance_requests.aggregate(
            total=Sum('estimated_cost')
        )['total'] or 0
        
        total_actual_cost = maintenance_requests.filter(
            status='completed'
        ).aggregate(
            total=Sum('actual_cost')
        )['total'] or 0
        
        # Category breakdown
        category_breakdown = maintenance_requests.filter(
            category__isnull=False
        ).values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        data = {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'in_progress_requests': in_progress_requests,
            'completed_requests': completed_requests,
            'urgent_requests': urgent_requests,
            'high_priority_requests': high_priority_requests,
            'new_requests_this_week': new_requests,
            'total_estimated_cost': float(total_estimated_cost),
            'total_actual_cost': float(total_actual_cost),
            'top_categories': list(category_breakdown),
        }
        
        return Response(data)


class DashboardExpensesView(APIView):
    """Dashboard view for expenses overview"""
    
    def get(self, request):
        user = request.user
        
        # Get expenses for user's properties
        user_properties = Property.objects.filter(owner=user).values_list('id', flat=True)
        
        expenses = Expense.objects.filter(
            base_property__in=user_properties
        )
        
        # Calculate statistics
        total_expenses = expenses.count()
        pending_expenses = expenses.filter(status='pending').count()
        approved_expenses = expenses.filter(status='approved').count()
        paid_expenses = expenses.filter(status='paid').count()
        
        # Financial statistics
        current_month = timezone.now().replace(day=1)
        
        total_amount = expenses.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        monthly_amount = expenses.filter(
            expense_date__gte=current_month
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Category breakdown
        category_breakdown = expenses.filter(
            category__isnull=False
        ).values(
            'category__name'
        ).annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('-total_amount')[:5]
        
        # Expense type breakdown
        type_breakdown = expenses.values(
            'expense_type'
        ).annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('-total_amount')
        
        # Recent activity
        week_ago = timezone.now() - timedelta(days=7)
        new_expenses = expenses.filter(created_at__gte=week_ago).count()
        
        data = {
            'total_expenses': total_expenses,
            'pending_expenses': pending_expenses,
            'approved_expenses': approved_expenses,
            'paid_expenses': paid_expenses,
            'total_amount': float(total_amount),
            'monthly_amount': float(monthly_amount),
            'new_expenses_this_week': new_expenses,
            'category_breakdown': list(category_breakdown),
            'type_breakdown': list(type_breakdown),
        }
        
        return Response(data)


class PropertyManagementAnalyticsView(APIView):
    """Comprehensive analytics view for property management"""
    
    def get(self, request):
        user = request.user
        
        # Get user's properties
        user_properties = Property.objects.filter(owner=user)
        rental_properties = RentalProperty.objects.filter(
            base_property__in=user_properties
        )
        
        # Time period
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)  # Last year
        
        # Calculate comprehensive analytics
        analytics_data = {}
        
        # 1. Financial Performance
        total_rental_income = rental_properties.aggregate(
            total=Sum('monthly_rent')
        )['total'] or 0
        
        annual_income = float(total_rental_income * 12)
        
        # Total expenses for the period
        total_expenses = Expense.objects.filter(
            base_property__in=user_properties,
            expense_date__range=[start_date, end_date]
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        net_income = annual_income - float(total_expenses)
        
        # ROI calculation (simplified)
        total_property_value = user_properties.aggregate(
            total=Sum('market_value')
        )['total'] or 0
        
        roi_percentage = (net_income / float(total_property_value) * 100) if total_property_value > 0 else 0
        
        analytics_data['financial'] = {
            'annual_rental_income': annual_income,
            'total_expenses': float(total_expenses),
            'net_income': net_income,
            'total_property_value': float(total_property_value),
            'roi_percentage': round(roi_percentage, 2),
        }
        
        # 2. Occupancy Analytics
        total_units = rental_properties.count()
        occupied_units = rental_properties.filter(rental_status='rented').count()
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        analytics_data['occupancy'] = {
            'total_units': total_units,
            'occupied_units': occupied_units,
            'vacant_units': total_units - occupied_units,
            'occupancy_rate': round(occupancy_rate, 2),
        }
        
        # 3. Maintenance Analytics
        maintenance_requests = MaintenanceRequest.objects.filter(
            base_property__in=user_properties,
            reported_date__range=[start_date, end_date]
        )
        
        avg_completion_time = maintenance_requests.filter(
            status='completed',
            started_date__isnull=False,
            completed_date__isnull=False
        ).aggregate(
            avg_time=Avg(
                models.F('completed_date') - models.F('started_date')
            )
        )['avg_time']
        
        avg_completion_days = avg_completion_time.days if avg_completion_time else 0
        
        analytics_data['maintenance'] = {
            'total_requests': maintenance_requests.count(),
            'completed_requests': maintenance_requests.filter(status='completed').count(),
            'average_completion_days': avg_completion_days,
            'total_maintenance_cost': float(
                maintenance_requests.aggregate(
                    total=Sum('actual_cost')
                )['total'] or 0
            ),
        }
        
        # 4. Tenant Analytics
        tenants = Tenant.objects.filter(
            leases__rental_property__in=rental_properties
        ).distinct()
        
        analytics_data['tenants'] = {
            'total_tenants': tenants.count(),
            'active_tenants': tenants.filter(status='active').count(),
            'average_lease_duration': 12,  # Could be calculated more precisely
        }
        
        return Response(analytics_data)


# -------------------------------------------------------------------------
# Enhanced Analytics Views with Heat Maps and Bar Charts
# -------------------------------------------------------------------------

class AdvancedPropertyAnalyticsView(APIView):
    """Enhanced property analytics with heat maps and advanced bar charts"""
    
    def get(self, request):
        try:
            # Import data visualization libraries
            import pandas as pd
            import numpy as np
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.utils import PlotlyJSONEncoder
        except ImportError:
            return Response({
                'error': 'Data visualization libraries not installed. Please install: pip install pandas plotly numpy'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        user = request.user
        
        # Get user's accessible properties
        user_properties = user.get_accessible_properties()
        rental_properties = RentalProperty.objects.filter(base_property__in=user_properties)
        
        # Time period for analytics
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        # Prepare analytics data
        analytics_data = []
        
        for property_obj in user_properties:
            try:
                rental_prop = rental_properties.filter(base_property=property_obj).first()
                
                # Calculate financial metrics
                monthly_rent = float(rental_prop.monthly_rent) if rental_prop else 0
                annual_income = monthly_rent * 12
                
                # Get expenses for this property
                property_expenses = Expense.objects.filter(
                    base_property=property_obj,
                    expense_date__range=[start_date, end_date]
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                
                # Calculate ROI
                property_value = float(property_obj.market_value) if property_obj.market_value else 0
                roi = ((annual_income - float(property_expenses)) / property_value * 100) if property_value > 0 else 0
                
                # Occupancy rate
                occupancy_rate = 100 if rental_prop and rental_prop.rental_status == 'rented' else 0
                
                # Maintenance metrics
                maintenance_requests = MaintenanceRequest.objects.filter(
                    base_property=property_obj,
                    reported_date__range=[start_date, end_date]
                )
                maintenance_count = maintenance_requests.count()
                avg_maintenance_cost = maintenance_requests.aggregate(
                    avg=Avg('actual_cost')
                )['avg'] or 0
                
                analytics_data.append({
                    'property_id': property_obj.id,
                    'property_title': property_obj.title,
                    'city': property_obj.location.city if property_obj.location else 'Unknown',
                    'property_type': property_obj.property_type,
                    'annual_income': annual_income,
                    'total_expenses': float(property_expenses),
                    'net_income': annual_income - float(property_expenses),
                    'roi': round(roi, 2),
                    'occupancy_rate': occupancy_rate,
                    'property_value': property_value,
                    'maintenance_requests': maintenance_count,
                    'avg_maintenance_cost': float(avg_maintenance_cost),
                    'latitude': float(property_obj.latitude) if property_obj.latitude else None,
                    'longitude': float(property_obj.longitude) if property_obj.longitude else None,
                })
            except Exception as e:
                logger.error(f"Error calculating analytics for property {property_obj.id}: {e}")
                continue
        
        # Generate enhanced visualizations
        charts = {}
        
        if analytics_data:
            df = pd.DataFrame(analytics_data)
            
            # 1. Performance Heat Map Matrix
            performance_metrics = ['roi', 'occupancy_rate', 'annual_income', 'maintenance_requests']
            property_labels = [item['property_title'][:20] + '...' if len(item['property_title']) > 20 
                             else item['property_title'] for item in analytics_data]
            
            # Normalize data for heat map (0-100 scale)
            normalized_data = []
            for metric in performance_metrics:
                values = [item[metric] for item in analytics_data]
                if values and max(values) > 0:
                    normalized = [(v - min(values)) / (max(values) - min(values)) * 100 for v in values]
                else:
                    normalized = [0] * len(values)
                normalized_data.append(normalized)
            
            # Create performance heat map
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=normalized_data,
                x=property_labels,
                y=['ROI (%)', 'Occupancy (%)', 'Annual Income', 'Maintenance Requests'],
                colorscale='RdYlGn',
                colorbar=dict(title="Performance Score (0-100)"),
                hoverongaps=False,
                hovertemplate='Property: %{x}<br>Metric: %{y}<br>Score: %{z:.1f}<extra></extra>'
            ))
            
            fig_heatmap.update_layout(
                title='Property Performance Heat Map',
                xaxis_title='Properties',
                yaxis_title='Performance Metrics',
                height=400,
                font=dict(size=10),
                xaxis={'tickangle': 45}
            )
            charts['performance_heatmap'] = json.dumps(fig_heatmap, cls=PlotlyJSONEncoder)
            
            # 2. Geographic Heat Map (if coordinates available)
            if any(item['latitude'] and item['longitude'] for item in analytics_data):
                locations_data = [item for item in analytics_data if item['latitude'] and item['longitude']]
                
                fig_geo_heat = px.density_mapbox(
                    pd.DataFrame(locations_data),
                    lat='latitude',
                    lon='longitude',
                    z='roi',
                    radius=10,
                    center=dict(lat=locations_data[0]['latitude'], lon=locations_data[0]['longitude']),
                    zoom=10,
                    mapbox_style="open-street-map",
                    title='Geographic ROI Heat Map',
                    color_continuous_scale='Viridis'
                )
                fig_geo_heat.update_layout(height=500)
                charts['geographic_heatmap'] = json.dumps(fig_geo_heat, cls=PlotlyJSONEncoder)
            
            # 3. Advanced Bar Charts
            
            # ROI by Property Type
            type_roi = df.groupby('property_type')['roi'].agg(['mean', 'count']).reset_index()
            fig_roi_type = px.bar(
                type_roi, 
                x='property_type', 
                y='mean',
                title='Average ROI by Property Type',
                labels={'mean': 'Average ROI (%)', 'property_type': 'Property Type'},
                color='mean',
                color_continuous_scale='Blues'
            )
            fig_roi_type.update_layout(height=400)
            charts['roi_by_type'] = json.dumps(fig_roi_type, cls=PlotlyJSONEncoder)
            
            # Financial Performance Comparison
            fig_financial = go.Figure()
            
            # Add income bars
            fig_financial.add_trace(go.Bar(
                name='Annual Income',
                x=property_labels,
                y=[item['annual_income'] for item in analytics_data],
                marker_color='lightblue',
                yaxis='y'
            ))
            
            # Add expense bars
            fig_financial.add_trace(go.Bar(
                name='Total Expenses',
                x=property_labels,
                y=[item['total_expenses'] for item in analytics_data],
                marker_color='lightcoral',
                yaxis='y'
            ))
            
            # Add net income line
            fig_financial.add_trace(go.Scatter(
                name='Net Income',
                x=property_labels,
                y=[item['net_income'] for item in analytics_data],
                mode='lines+markers',
                line=dict(color='green', width=3),
                yaxis='y'
            ))
            
            fig_financial.update_layout(
                title='Financial Performance Analysis',
                xaxis_title='Properties',
                yaxis_title='Amount (SAR)',
                height=500,
                barmode='group',
                xaxis={'tickangle': 45},
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            charts['financial_performance'] = json.dumps(fig_financial, cls=PlotlyJSONEncoder)
            
            # 4. Maintenance Analytics Heat Map
            maintenance_by_type = []
            cities = list(set([item['city'] for item in analytics_data]))
            property_types = list(set([item['property_type'] for item in analytics_data]))
            
            maintenance_matrix = []
            for city in cities:
                city_row = []
                for prop_type in property_types:
                    avg_maintenance = np.mean([
                        item['maintenance_requests'] for item in analytics_data 
                        if item['city'] == city and item['property_type'] == prop_type
                    ])
                    city_row.append(avg_maintenance if not np.isnan(avg_maintenance) else 0)
                maintenance_matrix.append(city_row)
            
            if maintenance_matrix and any(any(row) for row in maintenance_matrix):
                fig_maintenance_heat = go.Figure(data=go.Heatmap(
                    z=maintenance_matrix,
                    x=property_types,
                    y=cities,
                    colorscale='Reds',
                    colorbar=dict(title="Avg Maintenance Requests"),
                    hovertemplate='City: %{y}<br>Type: %{x}<br>Avg Requests: %{z:.1f}<extra></extra>'
                ))
                
                fig_maintenance_heat.update_layout(
                    title='Maintenance Requests Heat Map by City and Property Type',
                    xaxis_title='Property Type',
                    yaxis_title='City',
                    height=400
                )
                charts['maintenance_heatmap'] = json.dumps(fig_maintenance_heat, cls=PlotlyJSONEncoder)
            
            # 5. Occupancy and ROI Correlation Scatter Plot
            fig_correlation = px.scatter(
                df,
                x='occupancy_rate',
                y='roi',
                size='property_value',
                color='city',
                hover_data=['property_title', 'annual_income'],
                title='ROI vs Occupancy Rate Correlation',
                labels={'occupancy_rate': 'Occupancy Rate (%)', 'roi': 'ROI (%)'}
            )
            fig_correlation.update_layout(height=500)
            charts['roi_occupancy_correlation'] = json.dumps(fig_correlation, cls=PlotlyJSONEncoder)
        
        # Calculate summary statistics
        summary_stats = {}
        if analytics_data:
            summary_stats = {
                'total_properties': len(analytics_data),
                'total_annual_income': sum(item['annual_income'] for item in analytics_data),
                'total_expenses': sum(item['total_expenses'] for item in analytics_data),
                'average_roi': np.mean([item['roi'] for item in analytics_data]),
                'average_occupancy': np.mean([item['occupancy_rate'] for item in analytics_data]),
                'total_property_value': sum(item['property_value'] for item in analytics_data),
                'total_maintenance_requests': sum(item['maintenance_requests'] for item in analytics_data),
                'best_performing_property': max(analytics_data, key=lambda x: x['roi'])['property_title'] if analytics_data else None,
                'cities_covered': len(set([item['city'] for item in analytics_data])),
                'property_types': len(set([item['property_type'] for item in analytics_data])),
            }
        
        return Response({
            'analytics_data': analytics_data,
            'charts': charts,
            'summary_stats': summary_stats,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            }
        })


class WorkerAnalyticsView(APIView):
    """Analytics for worker performance and maintenance management"""
    
    def get(self, request):
        try:
            import pandas as pd
            import numpy as np
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.utils import PlotlyJSONEncoder
        except ImportError:
            return Response({
                'error': 'Data visualization libraries not installed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        user = request.user
        
        # Get worker performance data
        workers = Worker.objects.filter(status='active').prefetch_related('categories', 'assigned_maintenance')
        
        # Time period for analysis
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)  # Last 3 months
        
        worker_data = []
        for worker in workers:
            maintenance_jobs = worker.assigned_maintenance.filter(
                reported_date__range=[start_date, end_date]
            )
            
            completed_jobs = maintenance_jobs.filter(status='completed')
            avg_completion_time = completed_jobs.aggregate(
                avg=Avg(models.F('completed_date') - models.F('started_date'))
            )['avg']
            
            worker_data.append({
                'worker_id': worker.id,
                'worker_name': worker.full_name,
                'employee_id': worker.employee_id,
                'categories': [cat.name for cat in worker.categories.all()],
                'total_jobs': maintenance_jobs.count(),
                'completed_jobs': completed_jobs.count(),
                'pending_jobs': maintenance_jobs.filter(status__in=['assigned', 'in_progress']).count(),
                'completion_rate': (completed_jobs.count() / maintenance_jobs.count() * 100) if maintenance_jobs.count() > 0 else 0,
                'avg_completion_days': avg_completion_time.days if avg_completion_time else 0,
                'hourly_rate': float(worker.hourly_rate),
                'rating': float(worker.rating) if worker.rating else 0,
                'is_available': worker.is_available,
                'employment_type': worker.employment_type,
            })
        
        charts = {}
        
        if worker_data:
            df = pd.DataFrame(worker_data)
            
            # Worker Performance Heat Map
            worker_names = [item['worker_name'] for item in worker_data]
            performance_metrics = ['completion_rate', 'total_jobs', 'avg_completion_days', 'rating']
            
            # Normalize data for heat map
            normalized_data = []
            for metric in performance_metrics:
                values = [item[metric] for item in worker_data]
                if values and max(values) > 0:
                    if metric == 'avg_completion_days':  # Lower is better for completion time
                        normalized = [100 - (v / max(values) * 100) for v in values]
                    else:
                        normalized = [(v / max(values) * 100) for v in values]
                else:
                    normalized = [0] * len(values)
                normalized_data.append(normalized)
            
            fig_worker_heat = go.Figure(data=go.Heatmap(
                z=normalized_data,
                x=worker_names,
                y=['Completion Rate (%)', 'Total Jobs', 'Speed (inverted)', 'Rating'],
                colorscale='RdYlGn',
                colorbar=dict(title="Performance Score (0-100)"),
                hovertemplate='Worker: %{x}<br>Metric: %{y}<br>Score: %{z:.1f}<extra></extra>'
            ))
            
            fig_worker_heat.update_layout(
                title='Worker Performance Heat Map',
                xaxis_title='Workers',
                yaxis_title='Performance Metrics',
                height=400,
                xaxis={'tickangle': 45}
            )
            charts['worker_performance_heatmap'] = json.dumps(fig_worker_heat, cls=PlotlyJSONEncoder)
            
            # Workload Distribution Bar Chart
            fig_workload = px.bar(
                df,
                x='worker_name',
                y=['completed_jobs', 'pending_jobs'],
                title='Worker Workload Distribution',
                labels={'value': 'Number of Jobs', 'worker_name': 'Worker'},
                color_discrete_map={'completed_jobs': 'green', 'pending_jobs': 'orange'}
            )
            fig_workload.update_layout(height=400, xaxis={'tickangle': 45})
            charts['workload_distribution'] = json.dumps(fig_workload, cls=PlotlyJSONEncoder)
            
            # Skills vs Performance Correlation
            skills_performance = []
            all_categories = set()
            for worker in worker_data:
                all_categories.update(worker['categories'])
            
            for category in all_categories:
                category_workers = [w for w in worker_data if category in w['categories']]
                if category_workers:
                    avg_completion_rate = np.mean([w['completion_rate'] for w in category_workers])
                    avg_rating = np.mean([w['rating'] for w in category_workers if w['rating'] > 0])
                    worker_count = len(category_workers)
                    
                    skills_performance.append({
                        'category': category,
                        'avg_completion_rate': avg_completion_rate,
                        'avg_rating': avg_rating if avg_rating else 0,
                        'worker_count': worker_count
                    })
            
            if skills_performance:
                skills_df = pd.DataFrame(skills_performance)
                fig_skills = px.scatter(
                    skills_df,
                    x='avg_completion_rate',
                    y='avg_rating',
                    size='worker_count',
                    hover_data=['category'],
                    title='Skills Performance Analysis',
                    labels={'avg_completion_rate': 'Average Completion Rate (%)', 'avg_rating': 'Average Rating'}
                )
                fig_skills.update_layout(height=400)
                charts['skills_performance'] = json.dumps(fig_skills, cls=PlotlyJSONEncoder)
        
        # Calculate summary statistics
        summary_stats = {}
        if worker_data:
            summary_stats = {
                'total_workers': len(worker_data),
                'available_workers': len([w for w in worker_data if w['is_available']]),
                'average_completion_rate': np.mean([w['completion_rate'] for w in worker_data]),
                'total_jobs_assigned': sum(w['total_jobs'] for w in worker_data),
                'total_completed_jobs': sum(w['completed_jobs'] for w in worker_data),
                'average_rating': np.mean([w['rating'] for w in worker_data if w['rating'] > 0]),
                'skill_categories': len(all_categories) if 'all_categories' in locals() else 0,
            }
        
        return Response({
            'worker_data': worker_data,
            'charts': charts,
            'summary_stats': summary_stats,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            }
        })


class PaymentAnalyticsView(APIView):
    """Analytics for payment tracking and financial reports"""
    
    def get(self, request):
        try:
            import pandas as pd
            import numpy as np
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.utils import PlotlyJSONEncoder
        except ImportError:
            return Response({
                'error': 'Data visualization libraries not installed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        user = request.user
        
        # Get payment data
        from accounts.models import Payment
        
        # Time period for analysis
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)  # Last year
        
        # Get payments based on user role
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(user=user)
        
        payments = payments.filter(payment_date__range=[start_date, end_date])
        
        payment_data = []
        for payment in payments:
            payment_data.append({
                'payment_id': payment.payment_id,
                'amount': float(payment.amount),
                'currency': payment.currency,
                'payment_type': payment.payment_type,
                'payment_type_display': payment.get_payment_type_display(),
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'payment_date': payment.payment_date,
                'due_date': payment.due_date,
                'is_overdue': payment.is_overdue,
                'days_overdue': payment.days_overdue,
                'property_title': payment.property_reference.title if payment.property_reference else None,
                'month': payment.payment_date.strftime('%Y-%m'),
                'quarter': f"Q{((payment.payment_date.month-1)//3)+1} {payment.payment_date.year}",
            })
        
        charts = {}
        
        if payment_data:
            df = pd.DataFrame(payment_data)
            
            # Payment Status Distribution
            status_counts = df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='Payment Status Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            charts['payment_status_distribution'] = json.dumps(fig_status, cls=PlotlyJSONEncoder)
            
            # Payment Types Heat Map by Month
            payment_type_month = df.groupby(['month', 'payment_type']).agg({
                'amount': 'sum'
            }).reset_index()
            
            if len(payment_type_month) > 0:
                pivot_data = payment_type_month.pivot(index='month', columns='payment_type', values='amount').fillna(0)
                
                fig_type_heat = go.Figure(data=go.Heatmap(
                    z=pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    colorscale='Blues',
                    colorbar=dict(title="Amount (SAR)"),
                    hovertemplate='Month: %{y}<br>Type: %{x}<br>Amount: %{z:,.0f} SAR<extra></extra>'
                ))
                
                fig_type_heat.update_layout(
                    title='Payment Types Heat Map by Month',
                    xaxis_title='Payment Type',
                    yaxis_title='Month',
                    height=400
                )
                charts['payment_types_heatmap'] = json.dumps(fig_type_heat, cls=PlotlyJSONEncoder)
            
            # Monthly Payment Trends
            monthly_totals = df.groupby('month').agg({
                'amount': 'sum',
                'payment_id': 'count'
            }).reset_index()
            
            fig_trends = go.Figure()
            
            # Add amount trend
            fig_trends.add_trace(go.Scatter(
                x=monthly_totals['month'],
                y=monthly_totals['amount'],
                mode='lines+markers',
                name='Total Amount',
                line=dict(color='blue', width=3),
                yaxis='y'
            ))
            
            # Add count trend
            fig_trends.add_trace(go.Scatter(
                x=monthly_totals['month'],
                y=monthly_totals['payment_id'],
                mode='lines+markers',
                name='Payment Count',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))
            
            fig_trends.update_layout(
                title='Monthly Payment Trends',
                xaxis_title='Month',
                yaxis=dict(title='Amount (SAR)', side='left'),
                yaxis2=dict(title='Payment Count', side='right', overlaying='y'),
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            charts['monthly_trends'] = json.dumps(fig_trends, cls=PlotlyJSONEncoder)
            
            # Overdue Payments Analysis
            overdue_data = df[df['is_overdue'] == True]
            if len(overdue_data) > 0:
                fig_overdue = px.histogram(
                    overdue_data,
                    x='days_overdue',
                    nbins=20,
                    title='Overdue Payments Distribution',
                    labels={'days_overdue': 'Days Overdue', 'count': 'Number of Payments'},
                    color_discrete_sequence=['red']
                )
                fig_overdue.update_layout(height=400)
                charts['overdue_distribution'] = json.dumps(fig_overdue, cls=PlotlyJSONEncoder)
        
        # Calculate summary statistics
        summary_stats = {}
        if payment_data:
            total_amount = sum(p['amount'] for p in payment_data)
            paid_amount = sum(p['amount'] for p in payment_data if p['status'] == 'paid')
            overdue_count = len([p for p in payment_data if p['is_overdue']])
            
            summary_stats = {
                'total_payments': len(payment_data),
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'pending_amount': total_amount - paid_amount,
                'overdue_payments': overdue_count,
                'payment_types': len(set(p['payment_type'] for p in payment_data)),
                'average_payment': total_amount / len(payment_data) if payment_data else 0,
                'payment_success_rate': (len([p for p in payment_data if p['status'] == 'paid']) / len(payment_data) * 100) if payment_data else 0,
            }
        
        return Response({
            'payment_data': payment_data,
            'charts': charts,
            'summary_stats': summary_stats,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            }
        })


# -------------------------------------------------------------------------
# Worker Management Views
# -------------------------------------------------------------------------

class WorkerCategoryListCreateView(BaseListCreateView):
    queryset = WorkerCategory.objects.filter(is_active=True)
    serializer_class = WorkerCategorySerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']

class WorkerCategoryDetailView(BaseDetailView):
    queryset = WorkerCategory.objects.all()
    serializer_class = WorkerCategorySerializer

class WorkerListCreateView(BaseListCreateView):
    queryset = Worker.objects.select_related('management_company').prefetch_related('categories', 'property_assignments__assigned_property')
    serializer_class = WorkerSerializer
    filterset_fields = ['status', 'employment_type', 'is_available', 'categories']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email', 'phone']

class WorkerDetailView(BaseDetailView):
    queryset = Worker.objects.select_related('management_company').prefetch_related('categories', 'property_assignments__assigned_property')
    serializer_class = WorkerSerializer





class PropertyManagementCompanyListCreateView(BaseListCreateView):
    queryset = PropertyManagementCompany.objects.filter(is_active=True)
    serializer_class = PropertyManagementCompanySerializer
    permission_classes = [drf_permissions.IsAuthenticated, IsAdminUser]
    search_fields = ['name', 'registration_number', 'city']

class PropertyManagementCompanyDetailView(BaseDetailView):
    queryset = PropertyManagementCompany.objects.prefetch_related('workers', 'managed_properties')
    serializer_class = PropertyManagementCompanySerializer
    permission_classes = [drf_permissions.IsAuthenticated, IsAdminUser]

class WorkerPropertyAssignmentListCreateView(BaseListCreateView):
    queryset = WorkerPropertyAssignment.objects.select_related('worker', 'worker__management_company', 'assigned_property', 'assigned_property__location')
    serializer_class = WorkerPropertyAssignmentSerializer
    permission_classes = [CanManageWorkers]  # Override base permission
    filterset_fields = ['worker', 'property', 'is_active', 'status']

class WorkerPropertyAssignmentDetailView(BaseDetailView):
    queryset = WorkerPropertyAssignment.objects.select_related('worker', 'worker__management_company', 'assigned_property', 'assigned_property__location')
    serializer_class = WorkerPropertyAssignmentSerializer
    permission_classes = [CanManageWorkers]  # Override base permission

class PropertyMaintenanceWorkflowListView(generics.ListAPIView):
    queryset = PropertyMaintenanceWorkflow.objects.select_related('property', 'property__location', 'assigned_to', 'created_by').prefetch_related('maintenance_requests')
    serializer_class = PropertyMaintenanceWorkflowSerializer
    filterset_fields = ['current_status', 'workflow_type']

class PropertyMaintenanceWorkflowDetailView(BaseDetailView):
    queryset = PropertyMaintenanceWorkflow.objects.select_related('property', 'property__location', 'assigned_to', 'created_by').prefetch_related('maintenance_requests')
    serializer_class = PropertyMaintenanceWorkflowSerializer
    # Permission handled by BaseDashboardView