import logging
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import transaction

# Set up logging
logger = logging.getLogger(__name__)
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType

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
from django.utils import timezone
from datetime import timedelta


# Location Views
class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsVerifiedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city', 'state', 'country']
    search_fields = ['city', 'state', 'country']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsVerifiedUser, IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

# Media Views
class MediaListCreateView(generics.ListCreateAPIView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['media_type', 'is_primary']
    search_fields = ['name']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def create(self, request, *args, **kwargs):
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
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"Error in MediaListCreateView.create: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response(
                {"error": {"message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )

class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Media.objects.select_related('content_type')
    serializer_class = MediaSerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsObjectOwner()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.select_related('property')
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAppraiserOrDataEntry()]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def patch(self, request, *args, **kwargs):
        """Handle partial updates like auction extension"""
        auction = self.get_object()
        action = request.data.get('action')
        
        if action == 'extend':
            return self.extend_auction(request, auction)
        elif action == 'complete':
            return self.complete_auction(request, auction)
        else:
            return super().patch(request, *args, **kwargs)
    
    def extend_auction(self, request, auction):
        """Extend auction end time"""
        if request.user != auction.created_by and not request.user.is_staff:
            return Response(
                {'error': 'Only auction owner can extend auction'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        extension_hours = request.data.get('extension_hours', 24)
        reason = request.data.get('reason', '')
        
        try:
            extension_hours = int(extension_hours)
            if extension_hours < 1 or extension_hours > 168:  # Max 7 days
                return Response(
                    {'error': 'Extension must be between 1 and 168 hours'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extend the auction
            auction.end_date += timedelta(hours=extension_hours)
            auction.save()
            
            # Log the extension
            logger.info(f"Auction {auction.id} extended by {extension_hours} hours. Reason: {reason}")
            
            serializer = self.get_serializer(auction)
            return Response({
                'message': f'Auction extended by {extension_hours} hours',
                'auction': serializer.data
            })
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid extension hours'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error extending auction {auction.id}: {str(e)}")
            return Response(
                {'error': 'Failed to extend auction'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def complete_auction(self, request, auction):
        """Complete auction with selected winner"""
        if request.user != auction.created_by and not request.user.is_staff:
            return Response(
                {'error': 'Only auction owner can complete auction'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        winning_bid_id = request.data.get('winning_bid_id')
        notes = request.data.get('notes', '')
        
        try:
            if not winning_bid_id:
                return Response(
                    {'error': 'Winning bid ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the winning bid
            winning_bid = Bid.objects.get(id=winning_bid_id, auction=auction)
            
            # Update auction status
            auction.status = 'completed'
            auction.save()
            
            # Update bid statuses
            winning_bid.status = 'winning'
            winning_bid.save()
            
            # Mark other bids as outbid
            auction.bids.exclude(id=winning_bid_id).update(status='outbid')
            
            logger.info(f"Auction {auction.id} completed. Winner: {winning_bid.bidder.email}")
            
            serializer = self.get_serializer(auction)
            return Response({
                'message': 'Auction completed successfully',
                'auction': serializer.data,
                'winning_bid': {
                    'id': winning_bid.id,
                    'amount': float(winning_bid.bid_amount),
                    'bidder_name': winning_bid.bidder.get_full_name() or winning_bid.bidder.email
                }
            })
            
        except Bid.DoesNotExist:
            return Response(
                {'error': 'Invalid winning bid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error completing auction {auction.id}: {str(e)}")
            return Response(
                {'error': 'Failed to complete auction'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        return Bid.objects.select_related('auction', 'bidder').order_by('-bid_time')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new bid with comprehensive validation and error handling
        """
        try:
            # Log the incoming request data
            logger.info(f"Bid creation attempt by user {request.user.id}: {request.data}")
            
            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                return Response({
                    'error': {
                        'code': 'AUTH_REQUIRED',
                        'message': 'Authentication required to place bids'
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is verified
            if not getattr(request.user, 'is_verified', False):
                return Response({
                    'error': {
                        'code': 'VERIFICATION_REQUIRED', 
                        'message': 'Email verification required to place bids'
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if user is active
            if not request.user.is_active:
                return Response({
                    'error': {
                        'code': 'ACCOUNT_INACTIVE',
                        'message': 'Account is inactive'
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Validate required fields
            auction_id = request.data.get('auction')
            bid_amount = request.data.get('bid_amount')
            
            if not auction_id:
                return Response({
                    'error': {
                        'code': 'MISSING_AUCTION',
                        'message': 'Auction ID is required'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not bid_amount:
                return Response({
                    'error': {
                        'code': 'MISSING_BID_AMOUNT',
                        'message': 'Bid amount is required'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate bid amount is numeric
            try:
                bid_amount = float(bid_amount)
                if bid_amount <= 0:
                    raise ValueError("Bid amount must be positive")
            except (ValueError, TypeError):
                return Response({
                    'error': {
                        'code': 'INVALID_BID_AMOUNT',
                        'message': 'Invalid bid amount. Must be a positive number.'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the auction and validate it exists
            try:
                auction = Auction.objects.select_related('related_property').get(id=auction_id)
            except Auction.DoesNotExist:
                return Response({
                    'error': {
                        'code': 'AUCTION_NOT_FOUND',
                        'message': 'Auction not found'
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if auction can accept bids
            if not auction.can_accept_bids():
                return Response({
                    'error': {
                        'code': 'AUCTION_INACTIVE',
                        'message': 'Auction is not currently accepting bids'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if auction has ended
            if auction.end_date and timezone.now() > auction.end_date:
                return Response({
                    'error': {
                        'code': 'AUCTION_ENDED',
                        'message': 'Auction has ended'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check minimum bid requirement
            current_bid = auction.current_bid if auction.current_bid else auction.starting_bid
            minimum_required = float(current_bid) + float(auction.minimum_increment)
            
            if bid_amount < minimum_required:
                return Response({
                    'error': {
                        'code': 'BID_TOO_LOW',
                        'message': f'Bid must be at least ${minimum_required:,.2f}',
                        'minimum_bid': minimum_required,
                        'current_bid': float(current_bid),
                        'increment': float(auction.minimum_increment)
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user is bidding on their own auction
            if hasattr(auction, 'created_by') and auction.created_by == request.user:
                return Response({
                    'error': {
                        'code': 'SELF_BID_NOT_ALLOWED',
                        'message': 'You cannot bid on your own auction'
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Prepare bid data
            bid_data = {
                'auction': auction_id,
                'bid_amount': bid_amount,
                'max_bid_amount': request.data.get('max_bid_amount'),
                'notes': request.data.get('notes', ''),
                'status': 'pending'
            }
            
            # Create serializer instance
            serializer = self.get_serializer(data=bid_data)
            
            # Validate serializer
            if not serializer.is_valid():
                logger.error(f"Bid serializer validation errors: {serializer.errors}")
                return Response({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid bid data',
                        'details': serializer.errors
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the bid
            try:
                bid = serializer.save(
                    bidder=request.user,
                    ip_address=self.get_client_ip(request),
                    is_verified=request.user.is_verified
                )
                
                logger.info(f"Bid created successfully: ID {bid.id}, Amount ${bid.bid_amount}, User {request.user.id}")
                
                # Return success response
                response_data = {
                    'success': True,
                    'message': 'Bid placed successfully',
                    'bid': {
                        'id': bid.id,
                        'amount': float(bid.bid_amount),
                        'auction_id': auction.id,
                        'bidder_info': {
                            'id': request.user.id,
                            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email,
                            'email': request.user.email
                        },
                        'bid_time': bid.bid_time.isoformat(),
                        'status': bid.status,
                        'is_verified': bid.is_verified
                    },
                    'auction_update': {
                        'current_bid': float(auction.current_bid) if auction.current_bid else float(auction.starting_bid),
                        'bid_count': auction.bid_count,
                        'next_minimum_bid': float(auction.current_bid or auction.starting_bid) + float(auction.minimum_increment)
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as save_error:
                logger.error(f"Error saving bid: {str(save_error)}")
                return Response({
                    'error': {
                        'code': 'BID_SAVE_ERROR',
                        'message': 'Failed to save bid. Please try again.'
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected error in bid creation: {str(e)}", exc_info=True)
            return Response({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred. Please try again.'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class BidDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.select_related('auction', 'bidder')
    serializer_class = BidSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsObjectOwner()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context