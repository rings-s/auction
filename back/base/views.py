"""
Comprehensive views module for Real Estate Auction System
Includes all API endpoints with advanced filtering and search capabilities
"""
import logging
import json
from datetime import datetime, timedelta
from functools import wraps

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F, Count, Avg, Min, Max, Sum, Value, ExpressionWrapper, BooleanField, CharField, DateField
from django.db.models.functions import Concat, Cast, TruncDate, Coalesce
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction

from .models import (
    Auction, Property, Bid, Contract, Payment, Transaction,
    Document, MessageThread, Message, ThreadParticipant, Notification
)
from .serializers import (
    AuctionListSerializer, AuctionDetailSerializer, AuctionCreateSerializer, AuctionUpdateSerializer,
    PropertyListSerializer, PropertyDetailSerializer, PropertyCreateSerializer, PropertyUpdateSerializer,
    BidSerializer, BidCreateSerializer,
    ContractSerializer, ContractCreateSerializer, ContractUpdateSerializer,
    PaymentSerializer,
    TransactionSerializer, TransactionCreateSerializer, TransactionUpdateSerializer,
    DocumentSerializer
)
from base.decorators import (
    role_required, debug_request, timer
)

logger = logging.getLogger(__name__)


# ==============================
# Custom Pagination Classes
# ==============================

class StandardResultSetPagination(PageNumberPagination):
    """Base pagination class with customizable page size"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Enhanced paginated response with metadata"""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.get_page_size(self.request),
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class AuctionResultSetPagination(StandardResultSetPagination):
    """Custom pagination for auction listings"""
    pass


class PropertyResultSetPagination(StandardResultSetPagination):
    """Custom pagination for property listings"""
    pass


class BidResultSetPagination(StandardResultSetPagination):
    """Custom pagination for bid listings"""
    pass


class ContractResultSetPagination(StandardResultSetPagination):
    """Custom pagination for contract listings"""
    pass


class TransactionResultSetPagination(StandardResultSetPagination):
    """Custom pagination for transaction listings"""
    pass


# ==============================
# Helper Functions
# ==============================

def create_response(data=None, message=None, error=None, error_code=None, status_code=status.HTTP_200_OK):
    """
    Create a standardized response format for API views

    Args:
        data (dict, optional): Data to return in response
        message (str, optional): Success message
        error (str or dict, optional): Error message or validation errors
        error_code (str, optional): Error code for client identification
        status_code (int, optional): HTTP status code

    Returns:
        Response: DRF Response with formatted data
    """
    response = {"success": error is None}

    if data is not None:
        response["data"] = data

    if message:
        response["message"] = message

    if error:
        response["error"] = error

    if error_code:
        response["error_code"] = error_code

    return Response(response, status=status_code)


def send_bid_confirmation_email(email, auction_title, property_title, bid_amount, currency, auction_id):
    """
    Send bid confirmation email

    Args:
        email (str): Recipient email
        auction_title (str): Auction title
        property_title (str): Property title
        bid_amount (decimal): Bid amount
        currency (str): Currency code
        auction_id (str): Auction ID
    """
    try:
        # Implementation of email sending logic
        logger.info(f"Sending bid confirmation email to {email} for auction {auction_id}")
        # Actual email sending would be implemented here
        pass
    except Exception as e:
        logger.error(f"Failed to send bid confirmation email: {str(e)}")


def send_outbid_notification_email(email, auction_title, auction_id, property_title,
                                  previous_bid, current_bid, currency, end_time):
    """
    Send outbid notification email

    Args:
        email (str): Recipient email
        auction_title (str): Auction title
        auction_id (str): Auction ID
        property_title (str): Property title
        previous_bid (decimal): User's previous bid
        current_bid (decimal): New highest bid
        currency (str): Currency code
        end_time (datetime): Auction end time
    """
    try:
        # Implementation of outbid notification logic
        logger.info(f"Sending outbid notification email to {email} for auction {auction_id}")
        # Actual email sending would be implemented here
        pass
    except Exception as e:
        logger.error(f"Failed to send outbid notification email: {str(e)}")


def update_property_status(property_id, new_status, user):
    """
    Utility function to update property status

    Args:
        property_id: ID of the property
        new_status: New status to set
        user: User performing the status update

    Returns:
        Tuple of (success, message)
    """
    try:
        property_obj = Property.objects.get(id=property_id)

        # Check permissions
        if not user.is_admin and property_obj.owner != user:
            return False, "You do not have permission to update this property status"

        # Validate status transition
        valid_status_transitions = {
            'draft': ['pending_approval', 'inactive'],
            'pending_approval': ['active', 'rejected'],
            'active': ['under_contract', 'inactive'],
            'under_contract': ['sold', 'active'],
            'inactive': ['active', 'draft']
        }

        if new_status not in valid_status_transitions.get(property_obj.status, []):
            return False, f"Invalid status transition from {property_obj.status} to {new_status}"

        # Update status
        property_obj.status = new_status

        # Set verification info if applicable
        if new_status == 'active':
            property_obj.is_verified = True
            property_obj.verified_by = user
            property_obj.verification_date = timezone.now()

        property_obj.save()

        return True, "Property status updated successfully"

    except Property.DoesNotExist:
        return False, "Property not found"
    except Exception as e:
        logger.error(f"Error updating property status: {str(e)}")
        return False, "An error occurred while updating property status"


def advanced_filter(queryset, request, filter_mapping=None, search_fields=None):
    """
    Apply advanced filtering to a queryset based on request parameters

    Args:
        queryset: Base queryset to filter
        request: The request object containing query parameters
        filter_mapping: Dict mapping query params to model fields with optional transformations
        search_fields: List of fields to include in global search

    Returns:
        Filtered queryset
    """
    # If no mappings provided, return original queryset
    if not filter_mapping:
        return queryset

    # Start with a copy of the original queryset
    filtered_queryset = queryset

    # Get query parameters excluding pagination params
    params = request.query_params.copy()
    pagination_params = ['page', 'page_size']
    for param in pagination_params:
        if param in params:
            del params[param]

    # Global search across multiple fields
    search_query = params.get('search')
    if search_query and search_fields:
        search_filters = Q()
        for field in search_fields:
            search_filters |= Q(**{f"{field}__icontains": search_query})
        filtered_queryset = filtered_queryset.filter(search_filters)

        # Remove search from params to avoid processing it again
        if 'search' in params:
            del params['search']

    # Process specific filter parameters
    for param, param_value in params.items():
        # Skip empty values
        if not param_value:
            continue

        # Check if parameter exists in mapping
        if param in filter_mapping:
            field_info = filter_mapping[param]

            # Simple field mapping
            if isinstance(field_info, str):
                filtered_queryset = filtered_queryset.filter(**{field_info: param_value})

            # Complex field mapping with transformation
            elif isinstance(field_info, dict):
                field = field_info.get('field')
                transform = field_info.get('transform')

                if field and transform:
                    # Apply transformation to the value
                    if transform == 'boolean':
                        value = param_value.lower() in ('true', 'yes', '1')
                    elif transform == 'int':
                        try:
                            value = int(param_value)
                        except ValueError:
                            continue
                    elif transform == 'float':
                        try:
                            value = float(param_value)
                        except ValueError:
                            continue
                    elif transform == 'date':
                        try:
                            value = datetime.strptime(param_value, '%Y-%m-%d').date()
                        except ValueError:
                            continue
                    elif transform == 'list':
                        value = param_value.split(',')
                    else:
                        value = param_value

                    filtered_queryset = filtered_queryset.filter(**{field: value})

                # Range filtering
                elif field_info.get('type') == 'range':
                    min_field = field_info.get('min_field')
                    max_field = field_info.get('max_field')

                    if min_field and param.startswith('min_'):
                        try:
                            value = float(param_value) if field_info.get('transform') == 'float' else param_value
                            filtered_queryset = filtered_queryset.filter(**{f"{min_field}__gte": value})
                        except ValueError:
                            continue

                    if max_field and param.startswith('max_'):
                        try:
                            value = float(param_value) if field_info.get('transform') == 'float' else param_value
                            filtered_queryset = filtered_queryset.filter(**{f"{max_field}__lte": value})
                        except ValueError:
                            continue

                # Date range filtering
                elif field_info.get('type') == 'date_range':
                    date_field = field_info.get('field')

                    if date_field and param.endswith('_start'):
                        try:
                            date_value = datetime.strptime(param_value, '%Y-%m-%d').date()
                            filtered_queryset = filtered_queryset.filter(**{f"{date_field}__gte": date_value})
                        except ValueError:
                            continue

                    if date_field and param.endswith('_end'):
                        try:
                            date_value = datetime.strptime(param_value, '%Y-%m-%d').date()
                            filtered_queryset = filtered_queryset.filter(**{f"{date_field}__lte": date_value})
                        except ValueError:
                            continue

                # Text search with different operators
                elif field_info.get('type') == 'text':
                    field = field_info.get('field')
                    operator = field_info.get('operator', 'icontains')

                    if field:
                        filtered_queryset = filtered_queryset.filter(**{f"{field}__{operator}": param_value})

    # Apply sorting
    sort_by = request.query_params.get('sort_by')
    order = request.query_params.get('order', 'desc')

    if sort_by:
        # Allow multiple sort fields (comma-separated)
        sort_fields = sort_by.split(',')
        order_prefix = '-' if order.lower() == 'desc' else ''

        # Build the ordering fields
        ordering = []
        for field in sort_fields:
            field = field.strip()
            if field.startswith('-'):
                # Field already has a direction prefix, respect it
                ordering.append(field)
            else:
                # Apply the global direction prefix
                ordering.append(f"{order_prefix}{field}")

        filtered_queryset = filtered_queryset.order_by(*ordering)

    return filtered_queryset


def handle_exceptions(view_func):
    """
    Decorator to standardize exception handling in views
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"Error in {view_func.__name__}: {str(e)}", exc_info=True)

            # Create a standardized error response
            view_name = view_func.__name__
            error_code = f"{view_name.replace('_', '-')}-error"

            return create_response(
                error=f"An error occurred while processing your request: {str(e)}",
                error_code=error_code,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return wrapper


# ==============================
# Auction Views
# ==============================

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
@timer()
@handle_exceptions
def list_auctions(request):
    """
    List and filter auctions with advanced search and filter options

    Query Parameters:
    - status: Filter by auction status (draft, pending, active, closed, etc.)
    - auction_type: Filter by auction type (public, private, online, onsite)
    - property_type: Filter by property type
    - min_price: Minimum starting price
    - max_price: Maximum starting price
    - city: Filter by property city
    - district: Filter by property district
    - start_date_from: Auctions starting after this date
    - start_date_to: Auctions starting before this date
    - end_date_from: Auctions ending after this date
    - end_date_to: Auctions ending before this date
    - is_featured: Filter featured auctions
    - is_published: Filter published auctions (default: true)
    - bidder_id: Filter auctions where this user has placed bids
    - owner_id: Filter auctions by property owner
    - auctioneer_id: Filter auctions by auctioneer
    - has_bids: Filter auctions with/without bids
    - min_bid_count: Minimum number of bids
    - search: Global search across title, description, property title
    - sort_by: Sorting field (e.g., start_date, current_bid, bid_count)
    - order: Sort order (asc/desc)
    - fields: Comma-separated list of fields to include (selecting specific fields)
    """
    # Define mapping between query params and model fields
    filter_mapping = {
        'status': 'status',
        'auction_type': 'auction_type',
        'property_type': 'related_property__property_type',
        'city': {'type': 'text', 'field': 'related_property__city', 'operator': 'icontains'},
        'district': {'type': 'text', 'field': 'related_property__district', 'operator': 'icontains'},
        'min_price': {'type': 'range', 'min_field': 'starting_price', 'transform': 'float'},
        'max_price': {'type': 'range', 'max_field': 'starting_price', 'transform': 'float'},
        'start_date_from': {'type': 'date_range', 'field': 'start_date'},
        'start_date_to': {'type': 'date_range', 'field': 'start_date'},
        'end_date_from': {'type': 'date_range', 'field': 'end_date'},
        'end_date_to': {'type': 'date_range', 'field': 'end_date'},
        'is_featured': {'field': 'is_featured', 'transform': 'boolean'},
        'is_published': {'field': 'is_published', 'transform': 'boolean'},
        'bidder_id': 'bids__bidder_id',
        'owner_id': 'related_property__owner_id',
        'auctioneer_id': 'auctioneer_id',
        'min_bid_count': {'field': 'bid_count', 'transform': 'int'},
    }

    # Define fields for global search
    search_fields = ['title', 'description', 'related_property__title']

    # Base queryset with select_related for performance
    queryset = Auction.objects.select_related(
        'related_property',
        'created_by',
        'auctioneer'
    ).prefetch_related(
        'bids'
    ).filter(is_published=True)

    # Add bid count annotation
    queryset = queryset.annotate(bid_count=Count('bids', distinct=True))

    # Add remaining time annotation
    now = timezone.now()
    queryset = queryset.annotate(
        remaining_seconds=ExpressionWrapper(
            F('end_date') - now,
            output_field=CharField()
        )
    )

    # Apply has_bids filter if present
    has_bids = request.query_params.get('has_bids')
    if has_bids is not None:
        has_bids_value = has_bids.lower() in ('true', 'yes', '1')
        if has_bids_value:
            queryset = queryset.filter(bid_count__gt=0)
        else:
            queryset = queryset.filter(bid_count=0)

    # Apply advanced filtering
    queryset = advanced_filter(queryset, request, filter_mapping, search_fields)

    # Field selection if specified
    fields_param = request.query_params.get('fields')
    fields = fields_param.split(',') if fields_param else None

    # Default sorting
    if not request.query_params.get('sort_by'):
        queryset = queryset.order_by('-start_date')

    # Pagination
    paginator = AuctionResultSetPagination()
    page = paginator.paginate_queryset(queryset, request)

    # Serialize with fields selection if specified
    serializer = AuctionListSerializer(
        page,
        many=True,
        context={'request': request, 'fields': fields}
    )

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
@timer()
@handle_exceptions
def auction_analytics(request):
    """
    Provide comprehensive auction analytics

    Query Parameters:
    - start_date: Start date for analytics period
    - end_date: End date for analytics period
    - auction_type: Filter by auction type
    - status: Filter by auction status
    - format: Response format (json or csv)
    """
    # Apply date filtering if provided
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    queryset = Auction.objects.all()

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Filter by auction type if provided
    auction_type = request.query_params.get('auction_type')
    if auction_type:
        queryset = queryset.filter(auction_type=auction_type)

    # Filter by status if provided
    status_param = request.query_params.get('status')
    if status_param:
        queryset = queryset.filter(status=status_param)

    # Total auctions by status
    status_counts = queryset.values('status').annotate(
        count=Count('id')
    )

    # Auction types distribution
    type_distribution = queryset.values('auction_type').annotate(
        count=Count('id')
    )

    # Price statistics
    price_stats = queryset.aggregate(
        avg_starting_price=Avg('starting_price'),
        min_starting_price=Min('starting_price'),
        max_starting_price=Max('starting_price'),
        avg_current_bid=Avg('current_bid'),
        max_current_bid=Max('current_bid')
    )

    # Recent auction statistics
    recent_auctions = queryset.filter(
        start_date__gte=timezone.now() - timedelta(days=30)
    )

    # Bid statistics
    bid_stats = recent_auctions.annotate(
        bid_count=Count('bids')
    ).aggregate(
        avg_bids_per_auction=Avg('bid_count'),
        max_bids_auction=Max('bid_count'),
        total_bids=Sum('bid_count')
    )

    # Property type distribution in auctions
    property_type_distribution = queryset.values(
        'related_property__property_type'
    ).annotate(
        count=Count('id')
    )

    # Monthly auction trend
    monthly_trend = queryset.annotate(
        month=TruncDate('start_date', 'month')
    ).values('month').annotate(
        count=Count('id'),
        avg_starting_price=Avg('starting_price')
    ).order_by('month')

    # Calculate conversion rate (auctions to contracts)
    total_auctions = queryset.count()
    sold_auctions = queryset.filter(status='sold').count()
    conversion_rate = (sold_auctions / total_auctions * 100) if total_auctions > 0 else 0

    # Calculate average auction duration
    completed_auctions = queryset.filter(
        status__in=['closed', 'sold']
    ).annotate(
        duration=ExpressionWrapper(
            F('end_date') - F('start_date'),
            output_field=CharField()
        )
    )
    avg_duration_days = completed_auctions.aggregate(
        avg_days=Avg(Cast('duration', output_field=CharField()))
    )

    response_data = {
        'status_distribution': list(status_counts),
        'type_distribution': list(type_distribution),
        'price_statistics': price_stats,
        'bid_statistics': bid_stats,
        'property_type_distribution': list(property_type_distribution),
        'monthly_trend': list(monthly_trend),
        'conversion_rate': conversion_rate,
        'avg_auction_duration_days': avg_duration_days.get('avg_days') if avg_duration_days else None,
        'total_auctions': total_auctions,
        'active_auctions': queryset.filter(status='active').count(),
        'sold_auctions': sold_auctions
    }

    # Return in requested format
    format_param = request.query_params.get('format', 'json')
    if format_param.lower() == 'csv':
        import csv
        from io import StringIO

        # Create CSV file
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['Metric', 'Value'])

        # Write data
        writer.writerow(['Total Auctions', total_auctions])
        writer.writerow(['Active Auctions', queryset.filter(status='active').count()])
        writer.writerow(['Sold Auctions', sold_auctions])
        writer.writerow(['Conversion Rate', f"{conversion_rate:.2f}%"])
        writer.writerow(['Average Starting Price', price_stats.get('avg_starting_price')])
        writer.writerow(['Max Starting Price', price_stats.get('max_starting_price')])
        writer.writerow(['Average Current Bid', price_stats.get('avg_current_bid')])
        writer.writerow(['Max Current Bid', price_stats.get('max_current_bid')])
        writer.writerow(['Average Bids Per Auction', bid_stats.get('avg_bids_per_auction')])

        # Return CSV response
        return Response(
            output.getvalue(),
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="auction_analytics.csv"'}
        )

    # Default JSON response
    return create_response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
@timer()
@handle_exceptions
def auction_detail(request, auction_id):
    """
    Retrieve detailed information about a specific auction

    Query Parameters:
    - include_bids: Include bid history (true/false)
    - include_property: Include detailed property information (true/false)
    - include_documents: Include auction documents (true/false)
    """
    auction = get_object_or_404(
        Auction.objects.select_related(
            'related_property',
            'created_by',
            'auctioneer',
            'winning_bidder'
        ).prefetch_related(
            'bids',
            'documents'
        ),
        id=auction_id
    )

    # Check visibility permissions
    if not auction.is_published and (
        not request.user.is_authenticated or
        (request.user != auction.created_by and
         not request.user.has_role('admin'))
    ):
        return create_response(
            error="You do not have permission to view this auction",
            error_code="auction_not_accessible",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Prepare serializer context with optional includes
    serializer_context = {
        'request': request,
        'include_bids': request.query_params.get('include_bids', 'true').lower() in ('true', 'yes', '1'),
        'include_property': request.query_params.get('include_property', 'true').lower() in ('true', 'yes', '1'),
        'include_documents': request.query_params.get('include_documents', 'true').lower() in ('true', 'yes', '1')
    }

    serializer = AuctionDetailSerializer(auction, context=serializer_context)
    return create_response({"auction": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def create_auction(request):
    """
    Create a new auction
    """
    # Validate property ownership or admin status
    property_id = request.data.get('property_id')
    if not property_id:
        return create_response(
            error="Property ID is required",
            error_code="missing_property_id",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Get property and validate ownership
    property_obj = get_object_or_404(Property, id=property_id)

    if not request.user.is_admin and property_obj.owner != request.user:
        return create_response(
            error="You can only create auctions for your own properties",
            error_code="property_not_owned",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Validate input
    serializer = AuctionCreateSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save auction
    auction = serializer.save()

    # Serialize and return
    detail_serializer = AuctionDetailSerializer(auction)
    return create_response(
        {"auction": detail_serializer.data},
        message="Auction created successfully",
        status_code=status.HTTP_201_CREATED
    )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def update_auction(request, auction_id):
    """
    Update an existing auction
    """
    # Retrieve auction
    auction = get_object_or_404(Auction, id=auction_id)

    # Check update permissions
    if not request.user.is_admin and auction.created_by != request.user:
        return create_response(
            error="You do not have permission to update this auction",
            error_code="auction_update_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Validate input
    serializer = AuctionUpdateSerializer(
        auction,
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save updated auction
    updated_auction = serializer.save()

    # Serialize and return
    detail_serializer = AuctionDetailSerializer(updated_auction)
    return create_response({
        "auction": detail_serializer.data,
        "message": "Auction updated successfully"
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def delete_auction(request, auction_id):
    """
    Delete an auction
    """
    # Retrieve auction
    auction = get_object_or_404(Auction, id=auction_id)

    # Check delete permissions
    if not request.user.is_admin and auction.created_by != request.user:
        return create_response(
            error="You do not have permission to delete this auction",
            error_code="auction_delete_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Check if auction can be deleted
    if auction.status not in ['draft', 'cancelled']:
        return create_response(
            error="Only draft or cancelled auctions can be deleted",
            error_code="auction_delete_restricted",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Soft delete or hard delete based on configuration
    if getattr(settings, 'SOFT_DELETE', False):
        auction.is_published = False
        auction.save(update_fields=['is_published'])
        message = "Auction unpublished successfully"
    else:
        auction.delete()
        message = "Auction deleted successfully"

    return create_response(message=message)


# ==============================
# Property Views
# ==============================

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
@timer()
@handle_exceptions
def list_properties(request):
    """
    Comprehensive property search and filter endpoint with advanced filtering

    Query Parameters:
    - property_type: Filter by property type (land, apartment, etc.)
    - status: Filter by property status
    - min_price: Minimum estimated value
    - max_price: Maximum estimated value
    - min_area: Minimum property area
    - max_area: Maximum property area
    - bedrooms: Number of bedrooms
    - bathrooms: Number of bathrooms
    - city: Property city
    - district: Property district
    - country: Property country
    - is_featured: Filter featured properties
    - is_published: Filter published properties
    - has_auction: Filter properties with/without active auctions
    - is_verified: Filter verified properties
    - owner_id: Filter by owner
    - year_built_from: Minimum year built
    - year_built_to: Maximum year built
    - search: Global search across title, description, address
    - sort_by: Sorting field(s), comma-separated
    - order: Sort order (asc/desc)
    - fields: Comma-separated list of fields to include
    """
    # Define mapping between query params and model fields
    filter_mapping = {
        'property_type': 'property_type',
        'status': 'status',
        'city': {'type': 'text', 'field': 'city', 'operator': 'icontains'},
        'district': {'type': 'text', 'field': 'district', 'operator': 'icontains'},
        'country': {'type': 'text', 'field': 'country', 'operator': 'icontains'},
        'min_price': {'type': 'range', 'min_field': 'estimated_value', 'transform': 'float'},
        'max_price': {'type': 'range', 'max_field': 'estimated_value', 'transform': 'float'},
        'min_area': {'type': 'range', 'min_field': 'area', 'transform': 'float'},
        'max_area': {'type': 'range', 'max_field': 'area', 'transform': 'float'},
        'bedrooms': {'field': 'bedrooms', 'transform': 'int'},
        'bathrooms': {'field': 'bathrooms', 'transform': 'int'},
        'is_featured': {'field': 'is_featured', 'transform': 'boolean'},
        'is_published': {'field': 'is_published', 'transform': 'boolean'},
        'is_verified': {'field': 'is_verified', 'transform': 'boolean'},
        'owner_id': 'owner_id',
        'year_built_from': {'type': 'range', 'min_field': 'year_built', 'transform': 'int'},
        'year_built_to': {'type': 'range', 'max_field': 'year_built', 'transform': 'int'},
    }

    # Define fields for global search
    search_fields = ['title', 'description', 'address', 'city', 'district']

    # Base queryset with select_related for performance
    queryset = Property.objects.select_related(
        'owner',
        'verified_by'
    ).prefetch_related(
        'documents'
    )

    # Apply has_auction filter if present
    has_auction = request.query_params.get('has_auction')
    if has_auction is not None:
        has_auction_value = has_auction.lower() in ('true', 'yes', '1')
        properties_with_auctions = Property.objects.filter(
            auctions__status__in=['draft', 'pending', 'active']
        ).values_list('id', flat=True)

        if has_auction_value:
            queryset = queryset.filter(id__in=properties_with_auctions)
        else:
            queryset = queryset.exclude(id__in=properties_with_auctions)

    # Apply published filter (default to true)
    is_published = request.query_params.get('is_published', 'true')
    if is_published.lower() in ('true', 'yes', '1'):
        queryset = queryset.filter(is_published=True)

    # Apply advanced filtering
    queryset = advanced_filter(queryset, request, filter_mapping, search_fields)

    # Field selection if specified
    fields_param = request.query_params.get('fields')
    fields = fields_param.split(',') if fields_param else None

    # Default sorting if not specified
    if not request.query_params.get('sort_by'):
        queryset = queryset.order_by('-created_at')

    # Pagination
    paginator = PropertyResultSetPagination()
    page = paginator.paginate_queryset(queryset, request)

    # Serialize with fields selection if specified
    serializer = PropertyListSerializer(
        page,
        many=True,
        context={'request': request, 'fields': fields}
    )

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
@timer()
@handle_exceptions
def property_analytics(request):
    """
    Provide comprehensive property analytics

    Query Parameters:
    - start_date: Start date for analytics period
    - end_date: End date for analytics period
    - property_type: Filter by property type
    - status: Filter by property status
    - city: Filter by city
    - format: Response format (json or csv)
    """
    # Apply date filtering if provided
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    queryset = Property.objects.all()

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Filter by property type if provided
    property_type = request.query_params.get('property_type')
    if property_type:
        queryset = queryset.filter(property_type=property_type)

    # Filter by status if provided
    status_param = request.query_params.get('status')
    if status_param:
        queryset = queryset.filter(status=status_param)

    # Filter by city if provided
    city = request.query_params.get('city')
    if city:
        queryset = queryset.filter(city__icontains=city)

    # Property distribution by type
    type_distribution = queryset.values('property_type').annotate(
        count=Count('id'),
        total_value=Sum('estimated_value')
    )

    # Status distribution
    status_distribution = queryset.values('status').annotate(
        count=Count('id')
    )

    # Location-based analytics
    city_distribution = queryset.values('city').annotate(
        count=Count('id'),
        avg_value=Avg('estimated_value')
    ).order_by('-count')

    # Price and area statistics
    price_stats = queryset.aggregate(
        avg_value=Avg('estimated_value'),
        min_value=Min('estimated_value'),
        max_value=Max('estimated_value'),
        median_value=Avg('estimated_value')  # Approximation without window functions
    )

    area_stats = queryset.aggregate(
        avg_area=Avg('area'),
        min_area=Min('area'),
        max_area=Max('area'),
        total_area=Sum('area')
    )

    # Recent property views
    recent_views = queryset.filter(
        updated_at__gte=timezone.now() - timedelta(days=30)
    ).aggregate(
        total_views=Sum('views_count'),
        avg_views=Avg('views_count')
    )

    # Property yearly trend
    yearly_trend = queryset.annotate(
        year=TruncDate('created_at', 'year')
    ).values('year').annotate(
        count=Count('id'),
        avg_value=Avg('estimated_value')
    ).order_by('year')

    # Property age distribution
    current_year = timezone.now().year
    age_distribution = []

    # Age ranges
    age_ranges = [(0, 5), (6, 10), (11, 20), (21, 30), (31, float('inf'))]

    for min_age, max_age in age_ranges:
        min_year = current_year - max_age if max_age != float('inf') else 0
        max_year = current_year - min_age

        count = queryset.filter(
            year_built__gte=min_year,
            year_built__lte=max_year
        ).count()

        label = f"{min_age}-{max_age}" if max_age != float('inf') else f"{min_age}+"
        age_distribution.append({
            'age_range': label,
            'count': count
        })

    # Bedroom distribution
    bedroom_distribution = queryset.values('bedrooms').annotate(
        count=Count('id')
    ).order_by('bedrooms')

    # Auction attachment rate
    total_properties = queryset.count()
    properties_with_auctions = queryset.filter(
        auctions__isnull=False
    ).distinct().count()

    auction_rate = (properties_with_auctions / total_properties * 100) if total_properties > 0 else 0

    response_data = {
        'type_distribution': list(type_distribution),
        'status_distribution': list(status_distribution),
        'city_distribution': list(city_distribution),
        'price_statistics': price_stats,
        'area_statistics': area_stats,
        'recent_views': recent_views,
        'yearly_trend': list(yearly_trend),
        'age_distribution': age_distribution,
        'bedroom_distribution': list(bedroom_distribution),
        'auction_attachment_rate': auction_rate,
        'total_properties': total_properties,
        'active_properties': queryset.filter(status='active').count(),
        'sold_properties': queryset.filter(status='sold').count()
    }

    # Return in requested format
    format_param = request.query_params.get('format', 'json')
    if format_param.lower() == 'csv':
        import csv
        from io import StringIO

        # Create CSV file
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['Metric', 'Value'])

        # Write data
        writer.writerow(['Total Properties', total_properties])
        writer.writerow(['Active Properties', queryset.filter(status='active').count()])
        writer.writerow(['Sold Properties', queryset.filter(status='sold').count()])
        writer.writerow(['Auction Attachment Rate', f"{auction_rate:.2f}%"])
        writer.writerow(['Average Estimated Value', price_stats.get('avg_value')])
        writer.writerow(['Maximum Estimated Value', price_stats.get('max_value')])
        writer.writerow(['Average Area', area_stats.get('avg_area')])
        writer.writerow(['Total Area (All Properties)', area_stats.get('total_area')])

        # Return CSV response
        return Response(
            output.getvalue(),
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="property_analytics.csv"'}
        )

    # Default JSON response
    return create_response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
@timer()
@handle_exceptions
def property_detail(request, property_id):
    """
    Retrieve detailed information about a specific property

    Query Parameters:
    - include_auctions: Include auction information (true/false)
    - include_documents: Include property documents (true/false)
    """
    # Fetch property with related data
    property_obj = get_object_or_404(
        Property.objects.select_related(
            'owner',
            'verified_by'
        ).prefetch_related(
            'documents',
            'auctions'
        ),
        id=property_id
    )

    # Check visibility permissions
    if not property_obj.is_published and (
        not request.user.is_authenticated or
        (request.user != property_obj.owner and
         not request.user.has_role('admin'))
    ):
        return create_response(
            error="You do not have permission to view this property",
            error_code="property_not_accessible",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Increment view count (consider using cache to prevent spam)
    Property.objects.filter(id=property_id).update(views_count=F('views_count') + 1)

    # Prepare serializer context with optional includes
    serializer_context = {
        'request': request,
        'include_auctions': request.query_params.get('include_auctions', 'true').lower() in ('true', 'yes', '1'),
        'include_documents': request.query_params.get('include_documents', 'true').lower() in ('true', 'yes', '1')
    }

    # Serialize and return
    serializer = PropertyDetailSerializer(property_obj, context=serializer_context)
    return create_response({"property": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def create_property(request):
    """
    Create a new property listing
    """
    # Validate input
    serializer = PropertyCreateSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save property
    property_obj = serializer.save()

    # Serialize and return
    detail_serializer = PropertyDetailSerializer(property_obj)
    return create_response(
        {"property": detail_serializer.data},
        message="Property created successfully",
        status_code=status.HTTP_201_CREATED
    )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def update_property(request, property_id):
    """
    Update an existing property listing
    """
    # Retrieve property
    property_obj = get_object_or_404(Property, id=property_id)

    # Check update permissions
    if not request.user.is_admin and property_obj.owner != request.user:
        return create_response(
            error="You do not have permission to update this property",
            error_code="property_update_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Validate input
    serializer = PropertyUpdateSerializer(
        property_obj,
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save updated property
    updated_property = serializer.save()

    # Serialize and return
    detail_serializer = PropertyDetailSerializer(updated_property)
    return create_response({
        "property": detail_serializer.data,
        "message": "Property updated successfully"
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def delete_property(request, property_id):
    """
    Delete a property listing
    """
    # Retrieve property
    property_obj = get_object_or_404(Property, id=property_id)

    # Check delete permissions
    if not request.user.is_admin and property_obj.owner != request.user:
        return create_response(
            error="You do not have permission to delete this property",
            error_code="property_delete_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Check if property can be deleted
    if property_obj.status not in ['draft', 'inactive']:
        return create_response(
            error="Only draft or inactive properties can be deleted",
            error_code="property_delete_restricted",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Check for active auctions
    if property_obj.auctions.filter(status__in=['draft', 'pending', 'active']).exists():
        return create_response(
            error="Cannot delete property with active auctions",
            error_code="property_has_active_auctions",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Soft delete or hard delete based on configuration
    if getattr(settings, 'SOFT_DELETE', False):
        property_obj.is_published = False
        property_obj.save(update_fields=['is_published'])
        message = "Property unpublished successfully"
    else:
        property_obj.delete()
        message = "Property deleted successfully"

    return create_response(message=message)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def property_documents(request, property_id):
    """
    Retrieve documents associated with a property

    Query Parameters:
    - document_type: Filter by document type
    - verification_status: Filter by verification status
    - sort_by: Sorting field (created_at, document_type, verification_date)
    - order: Sort order (asc/desc)
    """
    # Retrieve property
    property_obj = get_object_or_404(Property, id=property_id)

    # Check view permissions
    if not request.user.is_admin and property_obj.owner != request.user:
        return create_response(
            error="You do not have permission to view these documents",
            error_code="property_documents_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Fetch documents with filtering
    documents = Document.objects.filter(related_property=property_obj)

    # Apply filters
    document_type = request.query_params.get('document_type')
    if document_type:
        documents = documents.filter(document_type=document_type)

    verification_status = request.query_params.get('verification_status')
    if verification_status:
        documents = documents.filter(verification_status=verification_status)

    # Apply sorting
    sort_by = request.query_params.get('sort_by', '-created_at')
    order = request.query_params.get('order', 'desc')

    # Validate sorting field
    valid_sort_fields = ['created_at', 'document_type', 'verification_date']
    if sort_by.lstrip('-') not in valid_sort_fields:
        sort_by = '-created_at'

    # Apply sorting
    sort_prefix = '-' if order.lower() == 'desc' else ''
    sort_field = sort_by.lstrip('-')
    documents = documents.order_by(f"{sort_prefix}{sort_field}")

    # Paginate results
    paginator = PageNumberPagination()
    paginator.page_size = int(request.query_params.get('page_size', 10))
    paginated_documents = paginator.paginate_queryset(documents, request)

    # Serialize documents
    serializer = DocumentSerializer(paginated_documents, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def change_property_status(request, property_id):
    """
    Change property status endpoint
    """
    new_status = request.data.get('status')

    if not new_status:
        return create_response(
            error="Status is required",
            error_code="missing_status",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Use utility function to update status
    success, message = update_property_status(property_id, new_status, request.user)

    if success:
        # Fetch updated property for response
        property_obj = Property.objects.get(id=property_id)
        serializer = PropertyDetailSerializer(property_obj)

        return create_response({
            "property": serializer.data,
            "message": message
        })
    else:
        return create_response(
            error=message,
            error_code="status_update_failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ==============================
# Bid Views
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def list_bids(request):
    """
    List and filter bids with comprehensive search options

    Query Parameters:
    - auction_id: Filter bids for a specific auction
    - bidder_id: Filter bids by a specific bidder
    - status: Filter by bid status
    - min_bid_amount: Minimum bid amount
    - max_bid_amount: Maximum bid amount
    - start_date: Bids placed after this date
    - end_date: Bids placed before this date
    - is_auto_bid: Filter auto bids
    - sort_by: Sorting field
    - order: Sort order (asc/desc)
    """
    # Define mapping between query params and model fields
    filter_mapping = {
        'auction_id': 'auction_id',
        'bidder_id': 'bidder_id',
        'status': 'status',
        'min_bid_amount': {'type': 'range', 'min_field': 'bid_amount', 'transform': 'float'},
        'max_bid_amount': {'type': 'range', 'max_field': 'bid_amount', 'transform': 'float'},
        'is_auto_bid': {'field': 'is_auto_bid', 'transform': 'boolean'},
    }

    # Base queryset with select_related for performance
    queryset = Bid.objects.select_related(
        'auction',
        'bidder'
    )

    # Apply date range filtering
    start_date = request.query_params.get('start_date')
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(bid_time__date__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    end_date = request.query_params.get('end_date')
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(bid_time__date__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Apply advanced filtering
    queryset = advanced_filter(queryset, request, filter_mapping)

    # Default sorting if not specified
    if not request.query_params.get('sort_by'):
        queryset = queryset.order_by('-bid_time')

    # Pagination
    paginator = BidResultSetPagination()
    page = paginator.paginate_queryset(queryset, request)

    # Serialize
    serializer = BidSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def place_bid(request):
    """
    Place a new bid on an auction
    """
    # Validate input
    serializer = BidCreateSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save bid within a transaction
    with transaction.atomic():
        # Create the bid
        bid = serializer.save()

        # Send bid confirmation email
        try:
            send_bid_confirmation_email(
                email=request.user.email,
                auction_title=bid.auction.title,
                property_title=bid.auction.related_property.title,
                bid_amount=bid.bid_amount,
                currency='SAR',  # Assuming Saudi Riyal, adjust as needed
                auction_id=str(bid.auction.id)
            )
        except Exception as email_error:
            logger.warning(f"Failed to send bid confirmation email: {str(email_error)}")

        # Check for outbid notifications
        if bid.auction.current_bid > bid.bid_amount:
            try:
                previous_winning_bid = Bid.objects.filter(
                    auction=bid.auction,
                    status='winning'
                ).first()

                if previous_winning_bid:
                    send_outbid_notification_email(
                        email=previous_winning_bid.bidder.email,
                        auction_title=bid.auction.title,
                        auction_id=str(bid.auction.id),
                        property_title=bid.auction.related_property.title,
                        previous_bid=previous_winning_bid.bid_amount,
                        current_bid=bid.bid_amount,
                        currency='SAR',
                        end_time=bid.auction.end_date
                    )
            except Exception as outbid_error:
                logger.warning(f"Failed to send outbid notification: {str(outbid_error)}")

    # Serialize and return
    serializer = BidSerializer(bid)
    return create_response(
        {"bid": serializer.data},
        message="Bid placed successfully",
        status_code=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def bid_analytics(request):
    """
    Provide comprehensive bid analytics

    Query Parameters:
    - auction_id: Filter analytics for a specific auction
    - bidder_id: Filter analytics for a specific bidder
    - start_date: Bids placed after this date
    - end_date: Bids placed before this date
    - format: Response format (json or csv)
    """
    # Base queryset
    queryset = Bid.objects.all()

    # Apply filters
    auction_id = request.query_params.get('auction_id')
    if auction_id:
        queryset = queryset.filter(auction_id=auction_id)

    bidder_id = request.query_params.get('bidder_id')
    if bidder_id:
        queryset = queryset.filter(bidder_id=bidder_id)

    # Apply date filtering
    start_date = request.query_params.get('start_date')
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(bid_time__date__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    end_date = request.query_params.get('end_date')
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(bid_time__date__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Bid distribution by status
    status_distribution = queryset.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('bid_amount')
    )

    # Auction bidding statistics
    auction_bid_stats = Auction.objects.annotate(
        bid_count=Count('bids'),
        total_bid_amount=Sum('bids__bid_amount')
    ).aggregate(
        avg_bids_per_auction=Avg('bid_count'),
        max_bids_per_auction=Max('bid_count'),
        avg_total_bid_amount=Avg('total_bid_amount')
    )

    # Bidder performance
    top_bidders = queryset.values('bidder__email').annotate(
        total_bids=Count('id'),
        total_bid_amount=Sum('bid_amount'),
        avg_bid_amount=Avg('bid_amount'),
        max_bid_amount=Max('bid_amount'),
        winning_bids=Count('id', filter=Q(status='winning'))
    ).order_by('-total_bid_amount')[:10]

    # Bid trends by time
    bid_trends = queryset.annotate(
        day=TruncDate('bid_time', 'day')
    ).values('day').annotate(
        count=Count('id'),
        avg_amount=Avg('bid_amount'),
        total_amount=Sum('bid_amount')
    ).order_by('day')

    # Auto-bid usage
    auto_bid_stats = queryset.aggregate(
        auto_bids=Count('id', filter=Q(is_auto_bid=True)),
        manual_bids=Count('id', filter=Q(is_auto_bid=False)),
        auto_bid_percentage=Count('id', filter=Q(is_auto_bid=True)) * 100.0 / Count('id'),
        avg_auto_bid_max=Avg('max_bid_amount', filter=Q(is_auto_bid=True))
    )

    response_data = {
        'status_distribution': list(status_distribution),
        'auction_bid_statistics': auction_bid_stats,
        'top_bidders': list(top_bidders),
        'bid_trends': list(bid_trends),
        'auto_bid_statistics': auto_bid_stats,
        'total_bids': queryset.count(),
        'total_bid_amount': queryset.aggregate(total=Sum('bid_amount'))['total'] or 0,
        'average_bid_amount': queryset.aggregate(avg=Avg('bid_amount'))['avg'] or 0,
    }

    # Return in requested format
    format_param = request.query_params.get('format', 'json')
    if format_param.lower() == 'csv':
        import csv
        from io import StringIO

        # Create CSV file
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['Metric', 'Value'])

        # Write data
        writer.writerow(['Total Bids', queryset.count()])
        writer.writerow(['Total Bid Amount', queryset.aggregate(total=Sum('bid_amount'))['total'] or 0])
        writer.writerow(['Average Bid Amount', queryset.aggregate(avg=Avg('bid_amount'))['avg'] or 0])
        writer.writerow(['Average Bids Per Auction', auction_bid_stats.get('avg_bids_per_auction')])
        writer.writerow(['Maximum Bids in an Auction', auction_bid_stats.get('max_bids_per_auction')])
        writer.writerow(['Auto-Bid Percentage', f"{auto_bid_stats.get('auto_bid_percentage'):.2f}%"])

        # Return CSV response
        return Response(
            output.getvalue(),
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="bid_analytics.csv"'}
        )

    # Default JSON response
    return create_response(response_data)


# ==============================
# Contract Views
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def list_contracts(request):
    """
    List and filter contracts with comprehensive search options

    Query Parameters:
    - status: Filter by contract status
    - buyer_id: Filter contracts by buyer
    - seller_id: Filter contracts by seller
    - agent_id: Filter contracts by agent
    - property_id: Filter contracts by property
    - auction_id: Filter contracts by auction
    - min_amount: Minimum contract amount
    - max_amount: Maximum contract amount
    - signed_only: Show only fully signed contracts
    - start_date: Contracts created after this date
    - end_date: Contracts created before this date
    - payment_method: Filter by payment method
    - sort_by: Sorting field
    - order: Sort order (asc/desc)
    """
    # Define mapping between query params and model fields
    filter_mapping = {
        'status': 'status',
        'buyer_id': 'buyer_id',
        'seller_id': 'seller_id',
        'agent_id': 'agent_id',
        'property_id': 'related_property_id',
        'auction_id': 'auction_id',
        'min_amount': {'type': 'range', 'min_field': 'contract_amount', 'transform': 'float'},
        'max_amount': {'type': 'range', 'max_field': 'contract_amount', 'transform': 'float'},
        'payment_method': 'payment_method',
    }

    # Base queryset with select_related for performance
    queryset = Contract.objects.select_related(
        'auction',
        'related_property',
        'buyer',
        'seller',
        'agent'
    )

    # Apply signed_only filter if requested
    signed_only = request.query_params.get('signed_only')
    if signed_only and signed_only.lower() in ('true', 'yes', '1'):
        queryset = queryset.filter(
            buyer_signed=True,
            seller_signed=True
        )
        # Also check agent signature if agent exists
        queryset = queryset.filter(
            Q(agent__isnull=True) | Q(agent_signed=True)
        )

    # Apply date filtering
    start_date = request.query_params.get('start_date')
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(contract_date__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    end_date = request.query_params.get('end_date')
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(contract_date__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Apply advanced filtering
    queryset = advanced_filter(queryset, request, filter_mapping)

    # Default sorting if not specified
    if not request.query_params.get('sort_by'):
        queryset = queryset.order_by('-contract_date')

    # Pagination
    paginator = ContractResultSetPagination()
    page = paginator.paginate_queryset(queryset, request)

    # Serialize
    serializer = ContractSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def contract_detail(request, contract_id):
    """
    Retrieve detailed information about a specific contract

    Query Parameters:
    - include_payments: Include payment details (true/false)
    - include_documents: Include contract documents (true/false)
    """
    # Fetch contract with related data
    contract = get_object_or_404(
        Contract.objects.select_related(
            'auction',
            'related_property',
            'buyer',
            'seller',
            'agent',
            'verification_authority'
        ).prefetch_related(
            'payments',
            'documents'
        ),
        id=contract_id
    )

    # Check view permissions
    if not request.user.is_admin and \
       request.user not in [contract.buyer, contract.seller, contract.agent]:
        return create_response(
            error="You do not have permission to view this contract",
            error_code="contract_not_accessible",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Prepare serializer context with optional includes
    serializer_context = {
        'request': request,
        'include_payments': request.query_params.get('include_payments', 'true').lower() in ('true', 'yes', '1'),
        'include_documents': request.query_params.get('include_documents', 'true').lower() in ('true', 'yes', '1')
    }

    # Serialize and return
    serializer = ContractSerializer(contract, context=serializer_context)
    return create_response({"contract": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def create_contract(request):
    """
    Create a new contract from an auction
    """
    # Validate input
    serializer = ContractCreateSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save contract within a transaction
    try:
        with transaction.atomic():
            # Create the contract
            contract = serializer.save()

            # Update auction status if needed
            auction = contract.auction
            auction.status = 'sold'
            auction.winning_bid = contract.contract_amount
            auction.winning_bidder = contract.buyer
            auction.save()

            # Update property status
            property_obj = contract.related_property
            property_obj.status = 'under_contract'
            property_obj.save()

        # Serialize and return
        detail_serializer = ContractSerializer(contract)
        return create_response(
            {"contract": detail_serializer.data},
            message="Contract created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return create_response(
            error=f"Failed to create contract: {str(e)}",
            error_code="contract_create_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def update_contract(request, contract_id):
    """
    Update an existing contract
    """
    # Retrieve contract
    contract = get_object_or_404(Contract, id=contract_id)

    # Check update permissions
    if not request.user.is_admin and request.user not in [contract.seller, contract.agent]:
        return create_response(
            error="You do not have permission to update this contract",
            error_code="contract_update_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Check contract status for updates
    if contract.status in ['completed', 'cancelled']:
        return create_response(
            error="Cannot update completed or cancelled contracts",
            error_code="contract_update_restricted",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Validate input
    serializer = ContractUpdateSerializer(
        contract,
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save updated contract
    updated_contract = serializer.save()

    # Serialize and return
    detail_serializer = ContractSerializer(updated_contract)
    return create_response({
        "contract": detail_serializer.data,
        "message": "Contract updated successfully"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def sign_contract(request, contract_id):
    """
    Sign a contract by a party
    """
    # Retrieve contract
    contract = get_object_or_404(Contract, id=contract_id)

    # Determine signing party
    user = request.user

    # Check signing permissions
    if user not in [contract.buyer, contract.seller, contract.agent]:
        return create_response(
            error="You are not a party to this contract",
            error_code="contract_sign_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Determine which signature to update
    if user == contract.buyer:
        if contract.buyer_signed:
            return create_response(
                error="You have already signed this contract",
                error_code="contract_already_signed",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        contract.buyer_signed = True
        contract.buyer_signature_date = timezone.now()
        message = "Contract signed by buyer"

    elif user == contract.seller:
        if contract.seller_signed:
            return create_response(
                error="You have already signed this contract",
                error_code="contract_already_signed",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        contract.seller_signed = True
        contract.seller_signature_date = timezone.now()
        message = "Contract signed by seller"

    elif user == contract.agent:
        if contract.agent_signed:
            return create_response(
                error="You have already signed this contract",
                error_code="contract_already_signed",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        contract.agent_signed = True
        contract.agent_signature_date = timezone.now()
        message = "Contract signed by agent"

    # Update contract status if fully signed
    if contract.buyer_signed and contract.seller_signed:
        contract.status = 'signed'
        # If agent is involved, also check agent's signature
        if contract.agent and not contract.agent_signed:
            contract.status = 'pending_agent'

    # Save contract
    contract.save()

    # Serialize and return
    serializer = ContractSerializer(contract)
    return create_response({
        "contract": serializer.data,
        "message": message
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def contract_analytics(request):
    """
    Provide comprehensive contract analytics

    Query Parameters:
    - start_date: Start date for analytics period
    - end_date: End date for analytics period
    - status: Filter by contract status
    - format: Response format (json or csv)
    """
    # Apply date filtering if provided
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    queryset = Contract.objects.all()

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(contract_date__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(contract_date__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Filter by status if provided
    status_param = request.query_params.get('status')
    if status_param:
        queryset = queryset.filter(status=status_param)

    # Contract status distribution
    status_distribution = queryset.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('contract_amount')
    )

    # Payment method distribution
    payment_method_distribution = queryset.values('payment_method').annotate(
        count=Count('id'),
        total_amount=Sum('contract_amount')
    )

    # Contract value statistics
    contract_value_stats = queryset.aggregate(
        avg_contract_value=Avg('contract_amount'),
        min_contract_value=Min('contract_amount'),
        max_contract_value=Max('contract_amount'),
        total_contract_value=Sum('contract_amount')
    )

    # Agent performance
    agent_performance = queryset.values('agent__email').annotate(
        total_contracts=Count('id'),
        total_contract_value=Sum('contract_amount')
    ).order_by('-total_contract_value')[:10]

    # Recent contracts (last 3 months)
    three_months_ago = timezone.now() - timedelta(days=90)
    recent_contracts = queryset.filter(
        contract_date__gte=three_months_ago
    ).aggregate(
        count=Count('id'),
        total_value=Sum('contract_amount')
    )

    # Property type distribution in contracts
    property_type_distribution = queryset.values(
        'related_property__property_type'
    ).annotate(
        count=Count('id'),
        total_value=Sum('contract_amount')
    )

    # Monthly contract trend
    monthly_trend = queryset.annotate(
        month=TruncDate('contract_date', 'month')
    ).values('month').annotate(
        count=Count('id'),
        avg_value=Avg('contract_amount'),
        total_value=Sum('contract_amount')
    ).order_by('month')

    # Completion rate (signed to completed)
    signed_contracts = queryset.filter(status='signed').count()
    completed_contracts = queryset.filter(status='completed').count()
    completion_rate = (completed_contracts / signed_contracts * 100) if signed_contracts > 0 else 0

    response_data = {
        'status_distribution': list(status_distribution),
        'payment_method_distribution': list(payment_method_distribution),
        'contract_value_statistics': contract_value_stats,
        'top_agents': list(agent_performance),
        'recent_contracts': recent_contracts,
        'property_type_distribution': list(property_type_distribution),
        'monthly_trend': list(monthly_trend),
        'completion_rate': completion_rate,
        'total_contracts': queryset.count(),
        'active_contracts': queryset.filter(status='active').count(),
        'completed_contracts': completed_contracts
    }

    # Return in requested format
    format_param = request.query_params.get('format', 'json')
    if format_param.lower() == 'csv':
        import csv
        from io import StringIO

        # Create CSV file
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['Metric', 'Value'])

        # Write data
        writer.writerow(['Total Contracts', queryset.count()])
        writer.writerow(['Active Contracts', queryset.filter(status='active').count()])
        writer.writerow(['Completed Contracts', completed_contracts])
        writer.writerow(['Completion Rate', f"{completion_rate:.2f}%"])
        writer.writerow(['Average Contract Value', contract_value_stats.get('avg_contract_value')])
        writer.writerow(['Total Contract Value', contract_value_stats.get('total_contract_value')])

        # Return CSV response
        return Response(
            output.getvalue(),
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="contract_analytics.csv"'}
        )

    # Default JSON response
    return create_response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def create_contract_payment(request, contract_id):
    """
    Create a payment for a specific contract
    """
    # Retrieve contract
    contract = get_object_or_404(Contract, id=contract_id)

    # Check payment creation permissions
    if not request.user.is_admin and request.user not in [contract.seller, contract.agent]:
        return create_response(
            error="You do not have permission to create payments for this contract",
            error_code="payment_creation_forbidden",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Prepare payment data
    payment_data = request.data.copy()
    payment_data['contract'] = contract_id
    payment_data['payer'] = request.user.id
    payment_data['payee'] = contract.seller.id

    # Validate input
    serializer = PaymentSerializer(
        data=payment_data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save payment within a transaction
    try:
        with transaction.atomic():
            # Save payment
            payment = serializer.save()

            # Update contract status if payment completes contract
            total_paid = contract.payments.aggregate(total=Sum('amount'))['total'] or 0
            total_paid += payment.amount

            if total_paid >= contract.contract_amount:
                contract.status = 'completed'
                contract.save(update_fields=['status'])

                # Update property status
                property_obj = contract.related_property
                property_obj.status = 'sold'
                property_obj.save(update_fields=['status'])

        return create_response(
            {"payment": serializer.data},
            message="Payment created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return create_response(
            error=f"Failed to create payment: {str(e)}",
            error_code="payment_create_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==============================
# Transaction Views
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def list_transactions(request):
    """
    List and filter transactions with comprehensive search options

    Query Parameters:
    - transaction_type: Filter by transaction type
    - status: Filter by transaction status
    - from_user_id: Filter transactions from a specific user
    - to_user_id: Filter transactions to a specific user
    - min_amount: Minimum transaction amount
    - max_amount: Maximum transaction amount
    - start_date: Transactions after this date
    - end_date: Transactions before this date
    - payment_id: Filter by related payment
    - auction_id: Filter by related auction
    - contract_id: Filter by related contract
    - currency: Filter by currency
    - sort_by: Sorting field
    - order: Sort order (asc/desc)
    """
    # Define mapping between query params and model fields
    filter_mapping = {
        'transaction_type': 'transaction_type',
        'status': 'status',
        'from_user_id': 'from_user_id',
        'to_user_id': 'to_user_id',
        'min_amount': {'type': 'range', 'min_field': 'amount', 'transform': 'float'},
        'max_amount': {'type': 'range', 'max_field': 'amount', 'transform': 'float'},
        'payment_id': 'payment_id',
        'auction_id': 'auction_id',
        'contract_id': 'contract_id',
        'currency': 'currency',
    }

    # Base queryset with select_related for performance
    queryset = Transaction.objects.select_related(
        'from_user',
        'to_user',
        'processed_by',
        'payment',
        'auction',
        'contract'
    )

    # Apply date filtering
    start_date = request.query_params.get('start_date')
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(transaction_date__date__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    end_date = request.query_params.get('end_date')
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(transaction_date__date__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Apply advanced filtering
    queryset = advanced_filter(queryset, request, filter_mapping)

    # Default sorting if not specified
    if not request.query_params.get('sort_by'):
        queryset = queryset.order_by('-transaction_date')

    # Pagination
    paginator = TransactionResultSetPagination()
    page = paginator.paginate_queryset(queryset, request)

    # Serialize
    serializer = TransactionSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def transaction_detail(request, transaction_id):
    """
    Retrieve detailed information about a specific transaction
    """
    # Fetch transaction with related data
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'from_user',
            'to_user',
            'processed_by',
            'payment',
            'auction',
            'contract'
        ),
        id=transaction_id
    )

    # Check view permissions
    if not request.user.is_admin and \
       request.user not in [transaction.from_user, transaction.to_user]:
        return create_response(
            error="You do not have permission to view this transaction",
            error_code="transaction_not_accessible",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Serialize and return
    serializer = TransactionSerializer(transaction)
    return create_response({"transaction": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['agent', 'admin'])
@debug_request
@timer()
@handle_exceptions
def create_transaction(request):
    """
    Create a new transaction
    """
    # Validate input
    serializer = TransactionCreateSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save transaction within a transaction block
    try:
        with transaction.atomic():
            # Create the transaction
            trans_obj = serializer.save()

            # Additional processing based on transaction type
            if trans_obj.transaction_type == 'deposit':
                # Link to payment or contract if applicable
                payment_id = request.data.get('payment_id')
                contract_id = request.data.get('contract_id')

                if payment_id:
                    try:
                        payment = Payment.objects.get(id=payment_id)
                        trans_obj.payment = payment
                        trans_obj.save(update_fields=['payment'])
                    except Payment.DoesNotExist:
                        logger.warning(f"Payment {payment_id} not found for transaction")

                if contract_id:
                    try:
                        contract = Contract.objects.get(id=contract_id)
                        trans_obj.contract = contract
                        trans_obj.save(update_fields=['contract'])
                    except Contract.DoesNotExist:
                        logger.warning(f"Contract {contract_id} not found for transaction")

        # Serialize and return
        detail_serializer = TransactionSerializer(trans_obj)
        return create_response(
            {"transaction": detail_serializer.data},
            message="Transaction created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return create_response(
            error=f"Failed to create transaction: {str(e)}",
            error_code="transaction_create_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@role_required(['admin'])
@debug_request
@timer()
@handle_exceptions
def update_transaction(request, transaction_id):
    """
    Update an existing transaction (admin only)
    """
    # Retrieve transaction
    trans_obj = get_object_or_404(Transaction, id=transaction_id)

    # Check if transaction can be updated
    if trans_obj.status in ['completed', 'cancelled']:
        return create_response(
            error="Cannot update completed or cancelled transactions",
            error_code="transaction_update_restricted",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Validate input
    serializer = TransactionUpdateSerializer(
        trans_obj,
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request}
    )

    if not serializer.is_valid():
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Save updated transaction
    updated_transaction = serializer.save()

    # Serialize and return
    detail_serializer = TransactionSerializer(updated_transaction)
    return create_response({
        "transaction": detail_serializer.data,
        "message": "Transaction updated successfully"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@debug_request
@timer()
@handle_exceptions
def transaction_analytics(request):
    """
    Provide comprehensive transaction analytics

    Query Parameters:
    - start_date: Start date for analytics period
    - end_date: End date for analytics period
    - transaction_type: Filter by transaction type
    - status: Filter by transaction status
    - currency: Filter by currency
    - format: Response format (json or csv)
    """
    # Apply date filtering if provided
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    queryset = Transaction.objects.all()

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(transaction_date__date__gte=start_date_obj)
        except ValueError:
            return create_response(
                error="Invalid start_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(transaction_date__date__lte=end_date_obj)
        except ValueError:
            return create_response(
                error="Invalid end_date format. Use YYYY-MM-DD.",
                error_code="invalid_date_format",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # Filter by transaction type if provided
    transaction_type = request.query_params.get('transaction_type')
    if transaction_type:
        queryset = queryset.filter(transaction_type=transaction_type)

    # Filter by status if provided
    status_param = request.query_params.get('status')
    if status_param:
        queryset = queryset.filter(status=status_param)

    # Filter by currency if provided
    currency = request.query_params.get('currency')
    if currency:
        queryset = queryset.filter(currency=currency)

    # Transaction type distribution
    type_distribution = queryset.values('transaction_type').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )

    # Status distribution
    status_distribution = queryset.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )

    # User transaction statistics
    user_transaction_stats = queryset.values('from_user__email').annotate(
        total_transactions=Count('id'),
        total_amount_sent=Sum('amount'),
        avg_transaction_amount=Avg('amount')
    ).order_by('-total_amount_sent')[:10]

    # Currency distribution
    currency_distribution = queryset.values('currency').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )

    # Recent transaction statistics (last 3 months)
    three_months_ago = timezone.now() - timedelta(days=90)
    recent_transaction_stats = queryset.filter(
        transaction_date__gte=three_months_ago
    ).aggregate(
        count=Count('id'),
        total_amount=Sum('amount'),
        avg_amount=Avg('amount')
    )

    # Transaction value statistics
    transaction_value_stats = queryset.aggregate(
        min_amount=Min('amount'),
        max_amount=Max('amount'),
        avg_amount=Avg('amount')
    )

    # Transaction trends by time
    transaction_trends = queryset.annotate(
        day=TruncDate('transaction_date', 'day')
    ).values('day').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('day')

    # Total fees and taxes
    fee_tax_stats = queryset.aggregate(
        total_fees=Sum('fee_amount'),
        total_taxes=Sum('tax_amount'),
        avg_fee_percentage=Avg(F('fee_amount') * 100 / F('amount')),
        avg_tax_percentage=Avg(F('tax_amount') * 100 / F('amount'))
    )

    response_data = {
        'type_distribution': list(type_distribution),
        'status_distribution': list(status_distribution),
        'top_transacting_users': list(user_transaction_stats),
        'currency_distribution': list(currency_distribution),
        'recent_transaction_stats': recent_transaction_stats,
        'transaction_value_stats': transaction_value_stats,
        'transaction_trends': list(transaction_trends),
        'fee_tax_statistics': fee_tax_stats,
        'total_transactions': queryset.count(),
        'total_amount': queryset.aggregate(total=Sum('amount'))['total'] or 0,
        'total_amount_with_fees': queryset.aggregate(
            total=Sum(F('amount') + F('fee_amount') + F('tax_amount'))
        )['total'] or 0
    }

    # Return in requested format
    format_param = request.query_params.get('format', 'json')
    if format_param.lower() == 'csv':
        import csv
        from io import StringIO

        # Create CSV file
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['Metric', 'Value'])

        # Write data
        writer.writerow(['Total Transactions', queryset.count()])
        writer.writerow(['Total Transaction Amount', queryset.aggregate(total=Sum('amount'))['total'] or 0])
        writer.writerow(['Total Amount With Fees', response_data['total_amount_with_fees']])
        writer.writerow(['Average Transaction Amount', transaction_value_stats.get('avg_amount')])
        writer.writerow(['Total Fees Collected', fee_tax_stats.get('total_fees')])
        writer.writerow(['Total Taxes Collected', fee_tax_stats.get('total_taxes')])

        # Return CSV response
        return Response(
            output.getvalue(),
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="transaction_analytics.csv"'}
        )

    # Default JSON response
    return create_response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['admin'])
@debug_request
@timer()
@handle_exceptions
def process_transaction(request, transaction_id):
    """
    Process a pending transaction
    """
    # Retrieve transaction
    trans_obj = get_object_or_404(Transaction, id=transaction_id)

    # Check transaction status
    if trans_obj.status != 'pending':
        return create_response(
            error="Only pending transactions can be processed",
            error_code="transaction_process_restricted",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Validate processing input
    processing_data = request.data

    # Process transaction within a transaction block
    try:
        with transaction.atomic():
            trans_obj.status = processing_data.get('status', 'completed')
            trans_obj.processed_by = request.user
            trans_obj.processed_at = timezone.now()
            trans_obj.reference = processing_data.get('reference', trans_obj.reference)
            trans_obj.notes = processing_data.get('notes', trans_obj.notes)

            # Calculate any additional fees or taxes
            trans_obj.fee_amount = processing_data.get(
                'fee_amount',
                trans_obj.fee_amount
            )
            trans_obj.tax_amount = processing_data.get(
                'tax_amount',
                trans_obj.tax_amount
            )

            trans_obj.save()

            # Update related objects if needed
            if trans_obj.payment and trans_obj.status == 'completed':
                trans_obj.payment.status = 'completed'
                trans_obj.payment.confirmed_at = timezone.now()
                trans_obj.payment.confirmed_by = request.user
                trans_obj.payment.save()

                # Update contract payment status if needed
                if trans_obj.contract:
                    # Check if contract is fully paid
                    total_paid = trans_obj.contract.payments.filter(
                        status='completed'
                    ).aggregate(total=Sum('amount'))['total'] or 0

                    if total_paid >= trans_obj.contract.contract_amount:
                        trans_obj.contract.status = 'completed'
                        trans_obj.contract.save(update_fields=['status'])

        # Serialize and return
        serializer = TransactionSerializer(trans_obj)
        return create_response({
            "transaction": serializer.data,
            "message": "Transaction processed successfully"
        })
    except Exception as e:
        return create_response(
            error=f"Failed to process transaction: {str(e)}",
            error_code="transaction_process_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Comprehensive dashboard overview
    """
    user = request.user

    # Properties
    owned_properties = Property.objects.filter(owner=user)
    active_properties = owned_properties.filter(status='active')

    # Auctions
    user_auctions = Auction.objects.filter(created_by=user)
    active_auctions = user_auctions.filter(status='active')

    # Bids
    user_bids = Bid.objects.filter(bidder=user)
    active_bids = user_bids.filter(auction__status='active')

    # Contracts
    buyer_contracts = Contract.objects.filter(buyer=user)
    seller_contracts = Contract.objects.filter(seller=user)
    active_contracts = buyer_contracts.filter(status='active') | seller_contracts.filter(status='active')

    # Financial overview
    total_property_value = owned_properties.aggregate(total=Sum('estimated_value'))['total'] or 0
    total_auction_value = user_auctions.aggregate(total=Sum('starting_price'))['total'] or 0
    total_contract_value = (
        buyer_contracts.filter(status='completed').aggregate(total=Sum('contract_amount'))['total'] or 0 +
        seller_contracts.filter(status='completed').aggregate(total=Sum('contract_amount'))['total'] or 0
    )

    return Response({
        'statistics': {
            'properties': {
                'total': owned_properties.count(),
                'active': active_properties.count(),
                'total_value': total_property_value
            },
            'auctions': {
                'total': user_auctions.count(),
                'active': active_auctions.count(),
                'total_value': total_auction_value
            },
            'bids': {
                'total': user_bids.count(),
                'active': active_bids.count(),
                'total_bid_amount': user_bids.aggregate(total=Sum('bid_amount'))['total'] or 0
            },
            'contracts': {
                'total': buyer_contracts.count() + seller_contracts.count(),
                'active': active_contracts.count(),
                'total_value': total_contract_value
            }
        },
        'recent_activity': {
            'properties': list(owned_properties.order_by('-created_at')[:5].values()),
            'auctions': list(user_auctions.order_by('-created_at')[:5].values()),
            'bids': list(user_bids.order_by('-created_at')[:5].values()),
            'contracts': list(
                list(buyer_contracts.order_by('-created_at')[:3].values()) +
                list(seller_contracts.order_by('-created_at')[:3].values())
            )
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_section(request, section):
    """
    Get detailed data for a specific dashboard section
    """
    user = request.user

    if section == 'properties':
        owned_properties = Property.objects.filter(owner=user)
        return Response({
            'statistics': {
                'total': owned_properties.count(),
                'by_status': owned_properties.values('status').annotate(count=Count('id')),
                'by_type': owned_properties.values('property_type').annotate(count=Count('id'))
            },
            'recent': list(owned_properties.order_by('-created_at')[:10].values())
        })

    elif section == 'auctions':
        user_auctions = Auction.objects.filter(created_by=user)
        return Response({
            'statistics': {
                'total': user_auctions.count(),
                'by_status': user_auctions.values('status').annotate(count=Count('id')),
                'by_type': user_auctions.values('auction_type').annotate(count=Count('id'))
            },
            'recent': list(user_auctions.order_by('-created_at')[:10].values())
        })

    # Add more sections as needed
    return Response({'error': 'Invalid section'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_chart(request, chart_type):
    """
    Provide data for various dashboard charts
    """
    user = request.user

    if chart_type == 'property_value_trend':
        properties = Property.objects.filter(owner=user)
        return Response({
            'labels': [p.created_at.strftime('%b %Y') for p in properties],
            'values': [float(p.estimated_value) for p in properties]
        })

    elif chart_type == 'auction_activity':
        auctions = Auction.objects.filter(created_by=user)
        return Response({
            'labels': [a.created_at.strftime('%b %Y') for a in auctions],
            'values': [1 for _ in auctions]
        })

    # Add more chart types as needed
    return Response({'error': 'Invalid chart type'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_quick_stats(request):
    """
    Provide quick statistics for the dashboard
    """
    user = request.user

    # Last 7 days
    week_ago = timezone.now() - timezone.timedelta(days=7)

    return Response({
        'last_7_days': {
            'new_properties': Property.objects.filter(owner=user, created_at__gte=week_ago).count(),
            'new_auctions': Auction.objects.filter(created_by=user, created_at__gte=week_ago).count(),
            'new_bids': Bid.objects.filter(bidder=user, created_at__gte=week_ago).count(),
            'new_contracts': Contract.objects.filter(
                Q(buyer=user) | Q(seller=user),
                created_at__gte=week_ago
            ).count()
        },
        'unread_notifications': Notification.objects.filter(recipient=user, is_read=False).count(),
        'pending_actions': {
            'pending_auctions': Auction.objects.filter(created_by=user, status='pending').count(),
            'pending_contracts': Contract.objects.filter(
                Q(buyer=user) | Q(seller=user),
                status__in=['pending_buyer', 'pending_seller', 'pending_payment']
            ).count()
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_recent_activity(request):
    """
    Retrieve recent activity across all models
    """
    user = request.user

    recent_activities = []

    # Combine and sort recent activities
    # Properties
    properties = Property.objects.filter(owner=user).order_by('-created_at')[:5]
    recent_activities.extend([
        {
            'type': 'property',
            'action': 'created',
            'data': p.title,
            'timestamp': p.created_at
        } for p in properties
    ])

    # Auctions
    auctions = Auction.objects.filter(created_by=user).order_by('-created_at')[:5]
    recent_activities.extend([
        {
            'type': 'auction',
            'action': 'created',
            'data': a.title,
            'timestamp': a.created_at
        } for a in auctions
    ])

    # Bids
    bids = Bid.objects.filter(bidder=user).order_by('-created_at')[:5]
    recent_activities.extend([
        {
            'type': 'bid',
            'action': 'placed',
            'data': f"Bid of {b.bid_amount} on {b.auction.title}",
            'timestamp': b.created_at
        } for b in bids
    ])

    # Contracts
    contracts = Contract.objects.filter(Q(buyer=user) | Q(seller=user)).order_by('-created_at')[:5]
    recent_activities.extend([
        {
            'type': 'contract',
            'action': 'created',
            'data': c.title,
            'timestamp': c.created_at
        } for c in contracts
    ])

    # Sort all activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return Response({
        'recent_activities': recent_activities[:10]  # Limit to 10 most recent activities
    })
