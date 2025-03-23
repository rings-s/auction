"""
Context processors for Real Estate Auction System
Provides common template variables across all templates
"""
import logging
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Q, Avg
from django.conf import settings
from .models import (
    Property, Auction, Notification, MessageThread,
    ThreadParticipant, Message
)

logger = logging.getLogger(__name__)

def user_context(request):
    """
    Context processor to add user-related information to templates
    
    Adds:
    - user_properties: Count of properties owned by the user
    - user_auctions: Count of auctions created by the user
    - user_bids: Count of bids placed by the user
    - user_contracts: Count of contracts where user is a party
    - user_roles: List of user roles
    - is_agent: Boolean if user is an agent
    - is_buyer: Boolean if user has placed any bids
    """
    context = {
        'is_rtl': getattr(settings, 'USE_RTL', False),
        'default_currency': getattr(settings, 'DEFAULT_CURRENCY', 'SAR'),
        'site_name': getattr(settings, 'SITE_NAME', 'Real Estate Auction System')
    }
    
    # Only add user-specific context for authenticated users
    if request.user.is_authenticated:
        try:
            context.update({
                'user_properties_count': Property.objects.filter(owner=request.user).count(),
                'user_auctions_count': Auction.objects.filter(created_by=request.user).count(),
                'user_bids_count': request.user.bids.count(),
                'user_contracts_count': (
                    request.user.buyer_contracts.count() + 
                    request.user.seller_contracts.count()
                ),
                'is_agent': hasattr(request.user, 'has_role') and 
                            request.user.has_role('agent'),
                'is_buyer': request.user.bids.exists(),
            })
            
            # Add user roles if available
            if hasattr(request.user, 'role_names'):
                context['user_roles'] = request.user.role_names
                
        except Exception as e:
            logger.error(f"Error in user_context processor: {str(e)}")
    
    return context


def notifications_context(request):
    """
    Context processor to add notification information to templates
    
    Adds:
    - unread_notifications_count: Count of unread notifications
    - recent_notifications: List of recent notifications
    - unread_messages_count: Count of unread messages
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Unread notifications count
            unread_count = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            
            # Recent notifications
            recent_notifications = Notification.objects.filter(
                recipient=request.user
            ).order_by('-created_at')[:5]
            
            # Unread messages count
            user_thread_memberships = ThreadParticipant.objects.filter(
                user=request.user,
                is_active=True
            )
            
            unread_messages_count = 0
            for membership in user_thread_memberships:
                unread_messages_count += membership.unread_count
            
            context.update({
                'unread_notifications_count': unread_count,
                'recent_notifications': recent_notifications,
                'unread_messages_count': unread_messages_count
            })
            
        except Exception as e:
            logger.error(f"Error in notifications_context processor: {str(e)}")
    
    return context


def auctions_context(request):
    """
    Context processor to add auction-related information to templates
    
    Adds:
    - featured_auctions: List of featured auctions
    - ending_soon_auctions: List of auctions ending soon
    - new_auctions: List of newly listed auctions
    - active_auctions_count: Count of active auctions
    """
    context = {}
    
    try:
        # Create a base queryset for published auctions
        base_queryset = Auction.objects.filter(
            is_published=True,
        ).select_related('related_property', 'auctioneer')
        
        # Get current time
        now = timezone.now()
        
        # Featured auctions (limited to 5)
        featured_auctions = base_queryset.filter(
            is_featured=True,
            start_date__lte=now,
            end_date__gt=now
        ).order_by('-created_at')[:5]
        
        # Auctions ending soon (next 24 hours)
        ending_soon = base_queryset.filter(
            status='active',
            end_date__range=(now, now + timedelta(hours=24))
        ).order_by('end_date')[:5]
        
        # Newly listed auctions (past 48 hours)
        new_auctions = base_queryset.filter(
            start_date__range=(now - timedelta(hours=48), now)
        ).order_by('-start_date')[:5]
        
        # Count of active auctions
        active_count = base_queryset.filter(
            status='active',
            start_date__lte=now,
            end_date__gt=now
        ).count()
        
        context.update({
            'featured_auctions': featured_auctions,
            'ending_soon_auctions': ending_soon,
            'new_auctions': new_auctions,
            'active_auctions_count': active_count
        })
        
    except Exception as e:
        logger.error(f"Error in auctions_context processor: {str(e)}")
    
    return context


def properties_context(request):
    """
    Context processor to add property-related information to templates
    
    Adds:
    - featured_properties: List of featured properties
    - recent_properties: List of recently added properties 
    - property_types: List of available property types with counts
    """
    context = {}
    
    try:
        # Create a base queryset for published properties
        base_queryset = Property.objects.filter(
            is_published=True
        ).select_related('owner')
        
        # Featured properties (limited to 5)
        featured_properties = base_queryset.filter(
            is_featured=True
        ).order_by('-created_at')[:5]
        
        # Recent properties (limited to 5)
        recent_properties = base_queryset.order_by('-created_at')[:5]
        
        # Get property types with counts
        property_types = base_queryset.values('property_type').annotate(
            count=Count('id')
        ).order_by('property_type')
        
        # Get property cities with counts
        cities = base_queryset.values('city').annotate(
            count=Count('id')
        ).order_by('city')
        
        context.update({
            'featured_properties': featured_properties,
            'recent_properties': recent_properties,
            'property_types': property_types,
            'property_cities': cities
        })
        
    except Exception as e:
        logger.error(f"Error in properties_context processor: {str(e)}")
    
    return context


def system_metrics_context(request):
    """
    Context processor to add system metrics information to templates
    Only available to admin users
    
    Adds:
    - total_properties: Count of all properties
    - total_auctions: Count of all auctions
    - total_bids: Count of all bids
    - total_contracts: Count of all contracts
    - avg_property_value: Average property value
    - avg_auction_value: Average auction winning bid
    """
    context = {}
    
    # Only provide metrics to admin users
    if request.user.is_authenticated and (
        request.user.is_staff or 
        request.user.is_superuser or 
        (hasattr(request.user, 'has_role') and request.user.has_role('admin'))
    ):
        try:
            # Get current time
            now = timezone.now()
            
            # Properties statistics
            property_count = Property.objects.count()
            active_property_count = Property.objects.filter(status='active').count()
            
            # Auctions statistics
            auction_count = Auction.objects.count()
            active_auction_count = Auction.objects.filter(
                status='active',
                start_date__lte=now,
                end_date__gt=now
            ).count()
            
            # Transaction values
            avg_property_value = Property.objects.aggregate(
                avg=Avg('estimated_value')
            )['avg'] or 0
            
            avg_auction_value = Auction.objects.filter(
                status='sold'
            ).aggregate(
                avg=Avg('winning_bid')
            )['avg'] or 0
            
            # User statistics
            user_model = request.user.__class__
            user_count = user_model.objects.count()
            
            context.update({
                'total_properties': property_count,
                'active_properties': active_property_count,
                'total_auctions': auction_count,
                'active_auctions': active_auction_count,
                'avg_property_value': avg_property_value,
                'avg_auction_value': avg_auction_value,
                'total_users': user_count
            })
            
        except Exception as e:
            logger.error(f"Error in system_metrics_context processor: {str(e)}")
    
    return context


def messaging_context(request):
    """
    Context processor to add messaging information to templates
    
    Adds:
    - recent_threads: List of recent message threads
    - unread_threads_count: Count of threads with unread messages
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Get user's thread memberships
            user_memberships = ThreadParticipant.objects.filter(
                user=request.user,
                is_active=True
            ).select_related('thread')
            
            # Get thread IDs
            thread_ids = [membership.thread_id for membership in user_memberships]
            
            # Get recent threads
            recent_threads = MessageThread.objects.filter(
                id__in=thread_ids
            ).order_by('-last_message_at')[:5]
            
            # Count threads with unread messages
            unread_threads_count = sum(
                1 for membership in user_memberships if membership.has_unread_messages
            )
            
            context.update({
                'recent_threads': recent_threads,
                'unread_threads_count': unread_threads_count
            })
            
        except Exception as e:
            logger.error(f"Error in messaging_context processor: {str(e)}")
    
    return context


def debug_context(request):
    """
    Debug context processor - only active when DEBUG=True
    
    Adds:
    - debug: Boolean indicating debug mode
    - debug_sql_queries: List of SQL queries (if DEBUG_SQL=True)
    """
    context = {
        'debug': settings.DEBUG
    }
    
    if settings.DEBUG and getattr(settings, 'DEBUG_SQL', False):
        from django.db import connection
        context['debug_sql_queries'] = connection.queries
    
    return context