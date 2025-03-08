"""
WebSocket routing configuration for the auction platform.
Defines URL patterns for WebSocket connections.

This file should be placed in your project root directory alongside asgi.py
"""

from django.urls import re_path

# Import WebSocket consumer classes from consumer modules
from consumers.chat_consumer import ChatConsumer
from consumers.auction_consumer import AuctionConsumer
from consumers.bidding_consumer import BiddingConsumer
from consumers.notification_consumer import NotificationConsumer
from consumers.dashboard_consumer import DashboardConsumer  # Include if implemented

# WebSocket URL patterns
# These patterns match the frontend WebSocketService.js expectations
websocket_urlpatterns = [
    # Chat messages
    # Allows alphanumeric characters, underscores, hyphens, and periods
    # Min length: 3 chars, Max length: 50 chars for security
    re_path(
        r'ws/chat/(?P<room_name>[a-zA-Z0-9_\-.]{3,50})/$',
        ChatConsumer.as_asgi(),
        name='chat_ws'
    ),
    
    # Auction real-time updates
    # For receiving live updates about an auction (price changes, timer, etc.)
    # Uses UUID format (36 chars including hyphens)
    re_path(
        r'ws/auctions/(?P<auction_id>[0-9a-f-]{36})/updates/$',
        AuctionConsumer.as_asgi(),
        name='auction_updates_ws'
    ),
    
    # Bidding activity
    # For real-time bidding functionality
    # Uses UUID format (36 chars including hyphens)
    re_path(
        r'ws/auctions/(?P<auction_id>[0-9a-f-]{36})/bids/$',
        BiddingConsumer.as_asgi(),
        name='bidding_ws'
    ),
    
    # User notifications
    # For real-time user notifications
    # Uses UUID format (36 chars including hyphens)
    re_path(
        r'ws/notifications/(?P<user_id>[0-9a-f-]{36})/$',
        NotificationConsumer.as_asgi(),
        name='notifications_ws'
    ),
    
    # Dashboard live updates
    # For real-time dashboard data updates
    # Uses UUID format (36 chars including hyphens)
    re_path(
        r'ws/dashboard/(?P<user_id>[0-9a-f-]{36})/$',
        DashboardConsumer.as_asgi(),
        name='dashboard_ws'
    ),
]

"""
Notes:
1. Ensure your consumer classes use the correct parameter names:
   - ChatConsumer should accept 'room_name'
   - AuctionConsumer should accept 'auction_id'
   - BiddingConsumer should accept 'auction_id'
   - NotificationConsumer should accept 'user_id'
   - DashboardConsumer should accept 'user_id'

2. For production deployments with Daphne:
   daphne -b 0.0.0.0 -p 8000 your_project.asgi:application
   
   For secure production:
   daphne -e ssl:443:privateKey=key.pem:certKey=cert.pem -b 0.0.0.0 your_project.asgi:application

3. If any of these consumers are not yet implemented, you can comment out 
   their import and URL pattern until they're ready.
"""