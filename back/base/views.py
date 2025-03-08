import logging
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from base.models import (
    Category, Subcategory, Auction, AuctionTimer, RealEstate, Vehicle,
    Machinery, Factory, HeavyVehicleAuction, Bid, Transaction,
    Document, Contract, ContractTermRevision, Message, PaymentMethod, Notification
)
from accounts.models import CustomUser, Role
from .serializers import (
    CategorySerializer, SubcategorySerializer, AuctionSerializer, AuctionTimerSerializer,
    RealEstateSerializer, VehicleSerializer, MachinerySerializer,
    FactorySerializer, HeavyVehicleAuctionSerializer, BidSerializer,
    TransactionSerializer, DocumentSerializer, ContractSerializer,
    ContractTermRevisionSerializer, MessageSerializer, PaymentMethodSerializer,
    NotificationSerializer, CustomUserSerializer
)
from .decorators import role_required, debug_request  # Import both decorators from decorators.py


# Configure logger
logger = logging.getLogger(__name__)

# ------------ Helper Functions ------------

def standard_paginate(queryset, request, serializer_class):
    """Helper function to standardize pagination across views"""
    page_size = int(request.GET.get('page_size', 10))
    page = request.GET.get('page', 1)
    
    paginator = Paginator(queryset, page_size)
    
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    
    data = serializer_class(results, many=True, context={'request': request}).data
    
    return {
        'count': paginator.count,
        'next': int(page) + 1 if int(page) < paginator.num_pages else None,
        'previous': int(page) - 1 if int(page) > 1 else None,
        'total_pages': paginator.num_pages,
        'results': data
    }

# ------------ Category Views ------------

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def category_list(request):
    """
    List all categories or create a new category.
    Optional query params:
    - q: Search by name
    """
    try:
        queryset = Category.objects.all()
        
        # Apply filters
        search_query = request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))
        
        # Order by specified field
        order_by = request.GET.get('order_by', 'name')
        direction = '-' if request.GET.get('direction') == 'desc' else ''
        queryset = queryset.order_by(f'{direction}{order_by}')
        
        # Use standard pagination
        response_data = standard_paginate(queryset, request, CategorySerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in category_list view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAdminUser])
@debug_request
def category_create(request):
    """Create a new category"""
    try:
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in category_create view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def category_detail(request, slug):
    """
    Retrieve a category by slug.
    """
    try:
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in category_detail view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@permission_classes([IsAdminUser])
@debug_request
def category_update(request, slug):
    """Update a category"""
    try:
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in category_update view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
@debug_request
def category_delete(request, slug):
    """Delete a category"""
    try:
        category = get_object_or_404(Category, slug=slug)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error in category_delete view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Subcategory Views ------------

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def subcategory_list(request):
    """
    List all subcategories.
    Optional query params:
    - category_id: Filter by category
    - q: Search by name
    """
    try:
        queryset = Subcategory.objects.all()
        
        # Apply filters
        category_id = request.GET.get('category_id')
        search_query = request.GET.get('q')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))
        
        # Order by specified field
        order_by = request.GET.get('order_by', 'name')
        direction = '-' if request.GET.get('direction') == 'desc' else ''
        queryset = queryset.order_by(f'{direction}{order_by}')
        
        # Use standard pagination
        response_data = standard_paginate(queryset, request, SubcategorySerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in subcategory_list view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAdminUser])
@debug_request
def subcategory_create(request):
    """Create a new subcategory"""
    try:
        serializer = SubcategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in subcategory_create view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def subcategory_detail(request, slug):
    """
    Retrieve a subcategory by slug.
    """
    try:
        subcategory = get_object_or_404(Subcategory, slug=slug)
        serializer = SubcategorySerializer(subcategory, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in subcategory_detail view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Auction Views ------------


@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def auction_list(request):
    """
    List auctions with comprehensive filtering options.
    
    Query parameters:
    - category: Filter by category slug
    - subcategory: Filter by subcategory slug
    - status: Filter by auction status
    - min_price: Filter by minimum current price
    - max_price: Filter by maximum current price
    - seller: Filter by seller ID
    - q: Search in title or description
    - sort_by: Sort by field (created_at, end_time, current_price)
    - direction: Sort direction (asc, desc)
    - auction_type: Filter by auction type (e.g., 'real_estate', 'vehicle')
    - ended: Show only ended auctions (true/false)
    - upcoming: Show only upcoming auctions (true/false)
    """
    try:
        logger.debug("Entering auction_list view")
        
        # Initial queryset
        queryset = Auction.objects.all().select_related(
            'category', 'subcategory', 'seller'
        ).prefetch_related('bids', 'timer')
        logger.debug(f"Initial Auction queryset count: {queryset.count()}")

        # Apply filters
        category_slug = request.GET.get('category')
        subcategory_slug = request.GET.get('subcategory')
        status_filter = request.GET.get('status')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        seller_id = request.GET.get('seller')
        search_query = request.GET.get('q')
        auction_type = request.GET.get('auction_type')
        ended = request.GET.get('ended')
        upcoming = request.GET.get('upcoming')
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            logger.debug(f"After category filter ({category_slug}): {queryset.count()}")

        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
            logger.debug(f"After subcategory filter ({subcategory_slug}): {queryset.count()}")

        if status_filter:
            try:
                queryset = queryset.filter(status=status_filter.upper())
                logger.debug(f"After status filter ({status_filter.upper()}): {queryset.count()}")
            except ValueError as e:
                logger.error(f"Invalid status value: {status_filter}, error: {str(e)}")
                return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(current_price__gte=min_price)
                logger.debug(f"After min_price filter ({min_price}): {queryset.count()}")
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid min_price value: {min_price}, error: {str(e)}")
                return Response({'error': 'min_price must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(current_price__lte=max_price)
                logger.debug(f"After max_price filter ({max_price}): {queryset.count()}")
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid max_price value: {max_price}, error: {str(e)}")
                return Response({'error': 'max_price must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
            logger.debug(f"After seller filter ({seller_id}): {queryset.count()}")

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            logger.debug(f"After search filter ({search_query}): {queryset.count()}")

        now = timezone.now()
        
        if ended == 'true':
            queryset = queryset.filter(end_time__lt=now)
            logger.debug(f"After ended filter: {queryset.count()}")

        if upcoming == 'true':
            queryset = queryset.filter(start_time__gt=now)
            logger.debug(f"After upcoming filter: {queryset.count()}")

        # Filter by auction type
        if auction_type:
            related_models = {
                'real_estate': RealEstate,
                'vehicle': Vehicle,
                'machinery': Machinery,
                'factory': Factory,
                'heavy_vehicle': HeavyVehicleAuction,
            }
            
            if auction_type not in related_models:
                logger.error(f"Invalid auction_type provided: {auction_type}")
                return Response(
                    {'error': f'Invalid auction_type: {auction_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            model_class = related_models[auction_type]
            try:
                auction_ids = model_class.objects.values_list('auction', flat=True)
                logger.debug(f"Auction IDs for {auction_type}: {list(auction_ids)}")
                if not auction_ids:
                    logger.info(f"No related {auction_type} objects found")
                queryset = queryset.filter(id__in=auction_ids)
                logger.debug(f"After auction_type filter ({auction_type}): {queryset.count()}")
            except Exception as e:
                logger.error(f"Error querying {auction_type} model: {str(e)}", exc_info=True)
                return Response(
                    {'error': f'Error filtering by auction_type {auction_type}: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Sort results
        sort_by = request.GET.get('sort_by', 'created_at')
        direction = request.GET.get('direction', 'desc')
        sort_field = f"{'-' if direction == 'desc' else ''}{sort_by}"
        try:
            queryset = queryset.order_by(sort_field)
            logger.debug(f"After sorting by {sort_field}: {queryset.count()}")
        except Exception as e:
            logger.error(f"Invalid sort field {sort_field}: {str(e)}")
            return Response({'error': 'Invalid sort field'}, status=status.HTTP_400_BAD_REQUEST)

        # Pagination and serialization
        try:
            response_data = standard_paginate(queryset, request, AuctionSerializer)
            logger.debug("Pagination and serialization completed successfully")
        except Exception as e:
            logger.error(f"Error during pagination/serialization: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error in pagination or serialization: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(response_data)

    except Exception as e:
        logger.error(f"Unexpected error in auction_list view: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def auction_detail(request, auction_id):
    """
    Retrieve an auction by ID and include its detailed information.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        serializer = AuctionSerializer(auction, context={'request': request})
        data = serializer.data
        
        # Check if this auction has specialized data
        auction_types = {
            'real_estate': {'model': RealEstate, 'serializer': RealEstateSerializer},
            'vehicle': {'model': Vehicle, 'serializer': VehicleSerializer},
            'machinery': {'model': Machinery, 'serializer': MachinerySerializer},
            'factory': {'model': Factory, 'serializer': FactorySerializer},
            'heavy_vehicle': {'model': HeavyVehicleAuction, 'serializer': HeavyVehicleAuctionSerializer},
        }
        
        for type_name, type_data in auction_types.items():
            try:
                if type_name in ['machinery', 'heavy_vehicle']:
                    # These models have ForeignKey relationship (multiple possible instances)
                    instance = type_data['model'].objects.filter(auction=auction).first()
                else:
                    # These models have OneToOne relationship (exactly one instance)
                    instance = type_data['model'].objects.get(auction=auction)
                
                if instance:
                    data['auction_type'] = type_name
                    data['specific_data'] = type_data['serializer'](
                        instance, 
                        context={'request': request}
                    ).data
                    break
            except type_data['model'].DoesNotExist:
                continue
        
        # Add recent bids
        recent_bids = Bid.objects.filter(auction=auction).order_by('-created_at')[:10]
        data['recent_bids'] = BidSerializer(
            recent_bids, 
            many=True, 
            context={'request': request}
        ).data
        
        # Add documents if user is authenticated
        if request.user.is_authenticated:
            documents = Document.objects.filter(auction=auction)
            data['documents'] = DocumentSerializer(
                documents, 
                many=True, 
                context={'request': request}
            ).data
        
        return Response(data)
    except Exception as e:
        logger.error(f"Error in auction_detail view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

@api_view(['POST'])
@role_required([Role.SELLER, Role.ADMIN])
@permission_classes([IsAuthenticated])
@debug_request
def auction_create(request):
    """
    Create a new auction with optional specific auction type data.
    
    Request format:
    {
        "auction": { ... auction data ... },
        "auction_type": "real_estate|vehicle|machinery|factory|heavy_vehicle",
        "specific_data": { ... type-specific data ... }
    }
    """
    try:
        auction_data = request.data.get('auction', {})
        auction_type = request.data.get('auction_type')
        specific_data = request.data.get('specific_data', {})
        
        # Add seller automatically
        auction_data['seller'] = request.user.id
        
        # Create the base auction
        auction_serializer = AuctionSerializer(data=auction_data)
        if not auction_serializer.is_valid():
            return Response(auction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        auction = auction_serializer.save()
        
        # Create auction timer
        timer_data = request.data.get('timer', {})
        if timer_data:
            timer_data['auction'] = auction.id
            timer_serializer = AuctionTimerSerializer(data=timer_data)
            if timer_serializer.is_valid():
                timer_serializer.save()
            else:
                # Rollback if timer creation fails
                auction.delete()
                return Response(timer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create specific auction type if provided
        if auction_type and specific_data:
            specific_data['auction'] = auction.id
            
            if auction_type == 'real_estate':
                serializer = RealEstateSerializer(data=specific_data)
            elif auction_type == 'vehicle':
                serializer = VehicleSerializer(data=specific_data)
            elif auction_type == 'machinery':
                serializer = MachinerySerializer(data=specific_data)
            elif auction_type == 'factory':
                serializer = FactorySerializer(data=specific_data)
            elif auction_type == 'heavy_vehicle':
                serializer = HeavyVehicleAuctionSerializer(data=specific_data)
            else:
                return Response(
                    {'error': f'Invalid auction type: {auction_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not serializer.is_valid():
                # Rollback if specific data creation fails
                auction.delete()
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
        
        return Response(
            auction_serializer.data,
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Error in auction_create view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@debug_request
def auction_update(request, auction_id):
    """
    Update an auction and optionally its specific type data.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Check if user is the seller or admin
        if auction.seller != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to update this auction'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update base auction
        auction_data = request.data.get('auction', {})
        if auction_data:
            auction_serializer = AuctionSerializer(
                auction, 
                data=auction_data, 
                partial=True
            )
            if not auction_serializer.is_valid():
                return Response(auction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            auction = auction_serializer.save()
        
        # Update timer if provided
        timer_data = request.data.get('timer', {})
        if timer_data:
            try:
                timer = AuctionTimer.objects.get(auction=auction)
                timer_serializer = AuctionTimerSerializer(
                    timer, 
                    data=timer_data, 
                    partial=True
                )
                if not timer_serializer.is_valid():
                    return Response(timer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                timer_serializer.save()
            except AuctionTimer.DoesNotExist:
                timer_data['auction'] = auction.id
                timer_serializer = AuctionTimerSerializer(data=timer_data)
                if not timer_serializer.is_valid():
                    return Response(timer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                timer_serializer.save()
        
        # Update specific type data if provided
        auction_type = request.data.get('auction_type')
        specific_data = request.data.get('specific_data', {})
        
        if auction_type and specific_data:
            instance = None
            serializer_class = None
            
            # Find the right model and serializer
            if auction_type == 'real_estate':
                try:
                    instance = RealEstate.objects.get(auction=auction)
                    serializer_class = RealEstateSerializer
                except RealEstate.DoesNotExist:
                    instance = None
            elif auction_type == 'vehicle':
                try:
                    instance = Vehicle.objects.get(auction=auction)
                    serializer_class = VehicleSerializer
                except Vehicle.DoesNotExist:
                    instance = None
            elif auction_type == 'machinery':
                try:
                    instance = Machinery.objects.filter(auction=auction).first()
                    serializer_class = MachinerySerializer
                except Machinery.DoesNotExist:
                    instance = None
            elif auction_type == 'factory':
                try:
                    instance = Factory.objects.get(auction=auction)
                    serializer_class = FactorySerializer
                except Factory.DoesNotExist:
                    instance = None
            elif auction_type == 'heavy_vehicle':
                try:
                    instance = HeavyVehicleAuction.objects.filter(auction=auction).first()
                    serializer_class = HeavyVehicleAuctionSerializer
                except HeavyVehicleAuction.DoesNotExist:
                    instance = None
            else:
                return Response(
                    {'error': f'Invalid auction type: {auction_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update or create instance
            if instance:
                serializer = serializer_class(
                    instance, 
                    data=specific_data, 
                    partial=True
                )
            else:
                specific_data['auction'] = auction.id
                serializer = serializer_class(data=specific_data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
        
        # Refresh auction data
        updated_auction = Auction.objects.get(id=auction_id)
        return Response(
            AuctionSerializer(updated_auction, context={'request': request}).data
        )
    except Exception as e:
        logger.error(f"Error in auction_update view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@debug_request
def auction_delete(request, auction_id):
    """Delete an auction"""
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Check if user is the seller or admin
        if auction.seller != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to delete this auction'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if auction has bids
        if Bid.objects.filter(auction=auction).exists():
            return Response(
                {'error': 'Cannot delete auction with existing bids'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        auction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error in auction_delete view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Bid Views ------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def create_bid(request, auction_id):
    """
    Create a new bid for an auction.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Check if auction is active
        if auction.status != 'ACTIVE':
            return Response(
                {'error': 'Cannot bid on inactive auction'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if auction has started and not ended
        now = timezone.now()
        if now < auction.start_time or now > auction.end_time:
            return Response(
                {'error': 'Auction is not open for bidding'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is not the seller
        if auction.seller == request.user:
            return Response(
                {'error': 'You cannot bid on your own auction'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare bid data
        bid_data = {
            'auction': auction.id,
            'bidder': request.user.id,
            'amount': request.data.get('amount'),
            'auto_bid_limit': request.data.get('auto_bid_limit', None),
            'status': 'PLACED'
        }
        
        bid_serializer = BidSerializer(
            data=bid_data, 
            context={'request': request}
        )
        if not bid_serializer.is_valid():
            return Response(bid_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bid = bid_serializer.save()
        
        # Update auction current price
        auction.current_price = bid.amount
        auction.save()
        
        # If timer auto-extend is enabled and bid is within threshold of end time
        try:
            timer = auction.timer
            time_remaining = (auction.end_time - now).total_seconds()
            threshold_seconds = timer.extension_threshold.total_seconds()
            
            if timer.auto_extend and time_remaining < threshold_seconds:
                timer.extend_timer()
        except AuctionTimer.DoesNotExist:
            pass
        
        return Response(
            bid_serializer.data,
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Error in create_bid view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def list_bids(request, auction_id):
    """
    List all bids for an auction.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        bids = Bid.objects.filter(auction=auction).order_by('-created_at')
        
        response_data = standard_paginate(bids, request, BidSerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in list_bids view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def user_bids(request):
    """
    List all bids made by the current user.
    """
    try:
        bids = Bid.objects.filter(bidder=request.user).order_by('-created_at')
        
        # Apply filters
        auction_id = request.GET.get('auction_id')
        status_filter = request.GET.get('status')
        
        if auction_id:
            bids = bids.filter(auction_id=auction_id)
        
        if status_filter:
            bids = bids.filter(status=status_filter)
        
        response_data = standard_paginate(bids, request, BidSerializer)
        
        # Add auction details to each bid
        for bid_data in response_data['results']:
            auction = Auction.objects.get(id=bid_data['auction'])
            bid_data['auction_details'] = {
                'id': auction.id,
                'title': auction.title,
                'current_price': float(auction.current_price),
                'status': auction.status,
                'end_time': auction.end_time,
            }
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in user_bids view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Document Views ------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def document_upload(request, auction_id):
    """
    Upload a document for an auction.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Check if user has permission (seller, buyer, or admin)
        if (auction.seller != request.user and 
            not request.user.is_staff and 
            not Transaction.objects.filter(auction=auction, winner=request.user).exists()):
            return Response(
                {'error': 'You do not have permission to upload documents for this auction'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get document data
        document_data = request.data.copy()
        document_data['auction'] = auction.id
        document_data['uploaded_by'] = request.user.id
        
        document_serializer = DocumentSerializer(data=document_data)
        if not document_serializer.is_valid():
            return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        document = document_serializer.save()
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Error in document_upload view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def document_list(request, auction_id):
    """
    List all documents for an auction.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Check if user has permission (seller, buyer, or admin)
        if (auction.seller != request.user and 
            not request.user.is_staff and 
            not Transaction.objects.filter(auction=auction, winner=request.user).exists()):
            return Response(
                {'error': 'You do not have permission to view documents for this auction'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documents = Document.objects.filter(auction=auction).order_by('-created_at')
        
        # Apply filters
        document_type = request.GET.get('document_type')
        verification_status = request.GET.get('verification_status')
        
        if document_type:
            documents = documents.filter(document_type=document_type)
        
        if verification_status is not None:
            verification_bool = verification_status.lower() == 'true'
            documents = documents.filter(verification_status=verification_bool)
        
        response_data = standard_paginate(documents, request, DocumentSerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in document_list view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Transaction Views ------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def create_transaction(request, auction_id):
    """
    Create a transaction for a won auction.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Check if auction is ended
        if auction.status != 'ENDED':
            return Response(
                {'error': 'Can only create transactions for ended auctions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get winning bid
        winning_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        if not winning_bid:
            return Response(
                {'error': 'No bids found for this auction'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the winner
        if winning_bid.bidder != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only the auction winner can initiate a transaction'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if transaction already exists
        if Transaction.objects.filter(auction=auction, winner=winning_bid.bidder).exists():
            return Response(
                {'error': 'A transaction already exists for this auction'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare transaction data
        transaction_data = {
            'auction': auction.id,
            'winner': winning_bid.bidder.id,
            'winning_bid': winning_bid.id,
            'amount': winning_bid.amount,
            'currency': auction.currency,
            'payment_type': request.data.get('payment_type', 'FULL'),
            'payment_method': request.data.get('payment_method'),
            'status': 'PENDING',
            'reference_number': f'TXN-{auction.id}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        }
        
        # Add optional fields
        if 'payment_proof' in request.data:
            transaction_data['payment_proof'] = request.data['payment_proof']
        
        if 'escrow_agent' in request.data:
            transaction_data['escrow_agent'] = request.data['escrow_agent']
        
        if 'notes' in request.data:
            transaction_data['notes'] = request.data['notes']
        
        if 'metadata' in request.data:
            transaction_data['metadata'] = request.data['metadata']
        
        transaction_serializer = TransactionSerializer(data=transaction_data)
        if not transaction_serializer.is_valid():
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = transaction_serializer.save()
        
        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Error in create_transaction view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def transaction_list(request):
    """
    List transactions for the current user.
    """
    try:
        # Determine if user is viewing as winner or seller
        view_as = request.GET.get('view_as', 'winner')
        
        if view_as == 'winner':
            transactions = Transaction.objects.filter(winner=request.user)
        elif view_as == 'seller':
            transactions = Transaction.objects.filter(auction__seller=request.user)
        else:
            return Response(
                {'error': 'Invalid view_as parameter. Use "winner" or "seller".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply filters
        status_filter = request.GET.get('status')
        payment_type = request.GET.get('payment_type')
        payment_method = request.GET.get('payment_method')
        
        if status_filter:
            transactions = transactions.filter(status=status_filter)
        
        if payment_type:
            transactions = transactions.filter(payment_type=payment_type)
        
        if payment_method:
            transactions = transactions.filter(payment_method=payment_method)
        
        # Order by created date
        transactions = transactions.order_by('-created_at')
        
        response_data = standard_paginate(transactions, request, TransactionSerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in transaction_list view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Search Views ------------

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def search(request):
    """
    Global search across multiple models.
    
    Query parameters:
    - q: Search query
    - models: Comma-separated list of models to search (auctions,categories,subcategories,users)
    - page: Page number
    - page_size: Number of results per page
    """
    try:
        search_query = request.GET.get('q', '')
        if not search_query:
            return Response(
                {'error': 'Search query is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        models_param = request.GET.get('models', 'auctions,categories,subcategories')
        models_to_search = models_param.split(',')
        
        results = {
            'auctions': [],
            'categories': [],
            'subcategories': [],
            'users': [],
        }
        
        # Search auctions
        if 'auctions' in models_to_search:
            auctions = Auction.objects.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            ).order_by('-created_at')[:10]
            
            results['auctions'] = AuctionSerializer(
                auctions, 
                many=True, 
                context={'request': request}
            ).data
        
        # Search categories
        if 'categories' in models_to_search:
            categories = Category.objects.filter(
                Q(name__icontains=search_query)
            ).order_by('name')[:10]
            
            results['categories'] = CategorySerializer(
                categories, 
                many=True, 
                context={'request': request}
            ).data
        
        # Search subcategories
        if 'subcategories' in models_to_search:
            subcategories = Subcategory.objects.filter(
                Q(name__icontains=search_query)
            ).order_by('name')[:10]
            
            results['subcategories'] = SubcategorySerializer(
                subcategories, 
                many=True, 
                context={'request': request}
            ).data
        
        # Search users (admin only)
        if 'users' in models_to_search and request.user.is_staff:
            users = CustomUser.objects.filter(
                Q(email__icontains=search_query) | 
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query)
            ).order_by('email')[:10]
            
            results['users'] = CustomUserSerializer(
                users, 
                many=True, 
                context={'request': request}
            ).data
        
        return Response(results)
    except Exception as e:
        logger.error(f"Error in search view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Dashboard Views ------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def user_dashboard(request):
    """
    Get dashboard data for the current user.
    """
    try:
        user = request.user
        
        # Active auctions where user is seller
        selling_auctions = Auction.objects.filter(
            seller=user,
            status='ACTIVE'
        ).count()
        
        # Active auctions where user has placed bids
        bidding_auctions = Auction.objects.filter(
            bids__bidder=user,
            status='ACTIVE'
        ).distinct().count()
        
        # Won auctions
        won_auctions = Transaction.objects.filter(
            winner=user
        ).count()
        
        # Sold auctions
        sold_auctions = Transaction.objects.filter(
            auction__seller=user
        ).count()
        
        # Recent bids
        recent_bids = Bid.objects.filter(
            bidder=user
        ).order_by('-created_at')[:5]
        
        recent_bids_data = BidSerializer(
            recent_bids,
            many=True,
            context={'request': request}
        ).data
        
        # Add auction details to bids
        for bid_data in recent_bids_data:
            auction = Auction.objects.get(id=bid_data['auction'])
            bid_data['auction_details'] = {
                'title': auction.title,
                'current_price': float(auction.current_price),
                'end_time': auction.end_time,
            }
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(
            Q(winner=user) | Q(auction__seller=user)
        ).order_by('-created_at')[:5]
        
        recent_transactions_data = TransactionSerializer(
            recent_transactions,
            many=True,
            context={'request': request}
        ).data
        
        # Recent notifications
        recent_notifications = Notification.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        recent_notifications_data = NotificationSerializer(
            recent_notifications,
            many=True,
            context={'request': request}
        ).data
        
        dashboard_data = {
            'selling_auctions': selling_auctions,
            'bidding_auctions': bidding_auctions,
            'won_auctions': won_auctions,
            'sold_auctions': sold_auctions,
            'recent_bids': recent_bids_data,
            'recent_transactions': recent_transactions_data,
            'recent_notifications': recent_notifications_data,
        }
        
        return Response(dashboard_data)
    except Exception as e:
        logger.error(f"Error in user_dashboard view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAdminUser])
@debug_request
def admin_dashboard(request):
    """
    Get dashboard data for admin users.
    """
    try:
        # Active auctions count
        active_auctions = Auction.objects.filter(status='ACTIVE').count()
        
        # Total auctions count
        total_auctions = Auction.objects.count()
        
        # Registered users count
        total_users = CustomUser.objects.count()
        
        # Total bids count
        total_bids = Bid.objects.count()
        
        # Total transactions amount
        total_transaction_amount = Transaction.objects.filter(
            status='COMPLETED'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Recent transactions
        recent_transactions = Transaction.objects.order_by('-created_at')[:10]
        recent_transactions_data = TransactionSerializer(
            recent_transactions,
            many=True,
            context={'request': request}
        ).data
        
        # Recent users
        recent_users = CustomUser.objects.order_by('-date_joined')[:10]
        recent_users_data = CustomUserSerializer(
            recent_users,
            many=True,
            context={'request': request}
        ).data
        
        # Auctions by category
        auctions_by_category = Category.objects.annotate(
            auction_count=Count('auctions')
        ).values('name', 'auction_count').order_by('-auction_count')[:10]
        
        # Recent notifications
        recent_notifications = Notification.objects.order_by('-created_at')[:10]
        recent_notifications_data = NotificationSerializer(
            recent_notifications,
            many=True,
            context={'request': request}
        ).data
        
        dashboard_data = {
            'active_auctions': active_auctions,
            'total_auctions': total_auctions,
            'total_users': total_users,
            'total_bids': total_bids,
            'total_transaction_amount': float(total_transaction_amount),
            'recent_transactions': recent_transactions_data,
            'recent_users': recent_users_data,
            'auctions_by_category': list(auctions_by_category),
            'recent_notifications': recent_notifications_data,
        }
        
        return Response(dashboard_data)
    except Exception as e:
        logger.error(f"Error in admin_dashboard view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Message Views ------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def message_history(request, room_id):
    """
    Get message history for a chat room.
    """
    try:
        messages = Message.objects.filter(room_id=room_id).order_by('timestamp')
        
        # Pagination
        response_data = standard_paginate(messages, request, MessageSerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in message_history view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Contract Views ------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def create_contract(request):
    """
    Create a new contract between buyer and seller.
    """
    try:
        contract_data = request.data.copy()
        
        # Validate that the user is either buyer or seller
        if (contract_data.get('seller') != request.user.id and 
            contract_data.get('buyer') != request.user.id and 
            not request.user.is_staff):
            return Response(
                {'error': 'You must be either the buyer or seller to create a contract.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate contract number
        contract_data['contract_number'] = f'CONT-{timezone.now().strftime("%Y%m%d%H%M%S")}'
        
        # Create the contract
        contract_serializer = ContractSerializer(data=contract_data)
        if not contract_serializer.is_valid():
            return Response(contract_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        contract = contract_serializer.save()
        
        # Create initial contract terms if provided
        terms_data = request.data.get('terms', [])
        for term in terms_data:
            term['contract'] = contract.id
            term['revised_by'] = request.user.id
            term['version_number'] = 1
            term['is_current_version'] = True
            
            term_serializer = ContractTermRevisionSerializer(data=term)
            if term_serializer.is_valid():
                term_serializer.save()
            else:
                logger.warning(f"Invalid term data: {term_serializer.errors}")
        
        return Response(
            ContractSerializer(contract).data,
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Error in create_contract view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def list_contracts(request):
    """
    List contracts for the current user.
    """
    try:
        # Determine role to filter by
        role = request.GET.get('role', 'all')
        
        if role == 'seller':
            contracts = Contract.objects.filter(seller=request.user)
        elif role == 'buyer':
            contracts = Contract.objects.filter(buyer=request.user)
        elif role == 'legal':
            contracts = Contract.objects.filter(
                Q(seller_legal_rep=request.user) | Q(buyer_legal_rep=request.user)
            )
        elif role == 'all':
            contracts = Contract.objects.filter(
                Q(seller=request.user) | Q(buyer=request.user) |
                Q(seller_legal_rep=request.user) | Q(buyer_legal_rep=request.user)
            )
        else:
            return Response(
                {'error': 'Invalid role parameter. Use "seller", "buyer", "legal", or "all".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply filters
        status_filter = request.GET.get('status')
        contract_type = request.GET.get('contract_type')
        
        if status_filter:
            contracts = contracts.filter(status=status_filter)
        
        if contract_type:
            contracts = contracts.filter(contract_type=contract_type)
        
        # Order by
        contracts = contracts.order_by('-created_at')
        
        response_data = standard_paginate(contracts, request, ContractSerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in list_contracts view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Payment Method Views ------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def add_payment_method(request):
    """
    Add a new payment method for the current user.
    """
    try:
        payment_data = request.data.copy()
        payment_data['user'] = request.user.id
        
        serializer = PaymentMethodSerializer(data=payment_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = serializer.save()
        
        return Response(
            PaymentMethodSerializer(payment_method).data,
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"Error in add_payment_method view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def list_payment_methods(request):
    """
    List payment methods for the current user.
    """
    try:
        payment_methods = PaymentMethod.objects.filter(user=request.user)
        
        # Filter by method type if provided
        method_type = request.GET.get('method_type')
        if method_type:
            payment_methods = payment_methods.filter(method_type=method_type)
        
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in list_payment_methods view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Notification Views ------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
def notification_list(request):
    """
    List notifications for the current user.
    """
    try:
        notifications = Notification.objects.filter(user=request.user)
        
        # Apply filters
        notification_type = request.GET.get('notification_type')
        read_status = request.GET.get('read')
        
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        
        if read_status is not None:
            read_bool = read_status.lower() == 'true'
            notifications = notifications.filter(read=read_bool)
        
        # Order by created date
        notifications = notifications.order_by('-created_at')
        
        response_data = standard_paginate(notifications, request, NotificationSerializer)
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in notification_list view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    """
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        
        notification.read = True
        notification.save()
        
        return Response(
            NotificationSerializer(notification).data
        )
    except Exception as e:
        logger.error(f"Error in mark_notification_read view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ------------ Dispute and Verification Views ------------

@api_view(['POST'])
@role_required([Role.LEGAL, Role.ADMIN])
@debug_request
def handle_dispute(request, transaction_id):
    """
    Handle a disputed transaction (available to legal representatives).
    """
    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        # Update transaction status
        if transaction.status != 'DISPUTED':
            return Response(
                {'error': 'Can only handle transactions that are in DISPUTED status'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        resolution = request.data.get('resolution')
        if resolution not in ['REFUND', 'COMPLETE', 'CANCEL']:
            return Response(
                {'error': 'Invalid resolution option'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Apply resolution
        if resolution == 'REFUND':
            transaction.status = 'REFUNDED'
            # Logic to process refund
        elif resolution == 'COMPLETE':
            transaction.status = 'COMPLETED'
        elif resolution == 'CANCEL':
            transaction.status = 'FAILED'
            
        transaction.notes += f"\nDispute resolved by {request.user.email} on {timezone.now()}: {request.data.get('notes', 'No notes provided')}"
        transaction.save()
        
        return Response(
            TransactionSerializer(transaction).data
        )
    except Exception as e:
        logger.error(f"Error in handle_dispute view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@role_required([Role.INSPECTOR, Role.ADMIN])
@debug_request
def create_inspection_report(request, auction_id):
    """
    Create an inspection report for an auction item.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id)
        
        # Prepare report data
        report_data = {
            'auction': auction.id,
            'inspector': request.user.id,
            'inspection_date': timezone.now(),
            'condition_rating': request.data.get('condition_rating'),
            'findings': request.data.get('findings'),
            'recommendations': request.data.get('recommendations'),
            'is_verified': request.data.get('is_verified', False),
        }
        
        # Save as a special document type
        document_data = {
            'auction': auction.id,
            'document_type': 'INSPECTION',
            'title': f'Inspection Report - {auction.title}',
            'description': 'Official inspection report',
            'uploaded_by': request.user.id,
            'verification_status': True,
            'verified_by': request.user.id,
            'metadata': report_data
        }
        
        if 'file' in request.data:
            document_data['file'] = request.data['file']
            
        document_serializer = DocumentSerializer(data=document_data)
        if document_serializer.is_valid():
            document = document_serializer.save()
            
            # Update auction status based on inspection
            if report_data['is_verified']:
                auction.status = 'VERIFIED'
                auction.save()
                
            return Response(
                document_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in create_inspection_report view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@role_required([Role.INSPECTOR, Role.ADMIN])
@debug_request
def verify_document(request, document_id):
    """
    Verify a document (available only to inspectors and admins).
    """
    try:
        document = get_object_or_404(Document, id=document_id)
        
        document.verification_status = True
        document.verified_by = request.user
        document.save()
        
        return Response(
            DocumentSerializer(document).data
        )
    except Exception as e:
        logger.error(f"Error in verify_document view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@role_required([Role.LEGAL, Role.ADMIN])
@debug_request
def review_contract(request, contract_id):
    """
    Review a contract (available to legal representatives).
    """
    try:
        contract = get_object_or_404(Contract, id=contract_id)
        
        # Update contract with review information
        contract.reviewed_by = request.user
        contract.review_date = timezone.now()
        contract.review_notes = request.data.get('review_notes', '')
        
        # Update status based on approval
        approval_status = request.data.get('approved', False)
        if approval_status:
            if contract.seller_legal_rep == request.user:
                contract.status = 'PENDING_BUYER'
            elif contract.buyer_legal_rep == request.user:
                contract.status = 'ACTIVE'
        else:
            contract.status = 'DISPUTED'
            
        contract.save()
        
        # Create a notification for relevant parties
        # (This would require implementing a notification system)
        
        return Response(
            ContractSerializer(contract).data
        )
    except Exception as e:
        logger.error(f"Error in review_contract view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )