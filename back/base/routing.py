from django.urls import re_path
from . import consumers

"""
WebSocket URL patterns for the auction application.

These patterns define the WebSocket endpoints that clients can connect to.
Each pattern maps a URL to a specific consumer that will handle the WebSocket connection.
"""

websocket_urlpatterns = [
    # Chat WebSocket - Enhanced room_name pattern with better validation
    # Now allows letters, numbers, underscores, hyphens, and periods (common for IDs)
    # Minimum 3 chars, maximum 50 chars for security
    re_path(
        r'ws/chat/(?P<room_name>[\w\-\.]{3,50})/$',
        consumers.ChatConsumer.as_asgi(),
        name='chat_ws'
    ),
    
    # Comment out or remove the following endpoints until they are implemented
    # Uncomment when you implement the corresponding consumer classes
    
    # # Auction live updates - receive real-time updates for an auction
    re_path(
        r'ws/auction/(?P<auction_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        consumers.AuctionConsumer.as_asgi(),
        name='auction_ws'
    ),
    
    # # Bidding WebSocket - handle real-time bidding
    re_path(
        r'ws/bidding/(?P<auction_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        consumers.BiddingConsumer.as_asgi(),
        name='bidding_ws'
    ),
    
    # # Notifications WebSocket - personal user notifications
    re_path(
        r'ws/notifications/(?P<user_id>\d+)/$',
        consumers.NotificationConsumer.as_asgi(),
        name='notifications_ws'
    ),
    
    # # Dashboard live updates
    re_path(
        r'ws/dashboard/(?P<user_id>\d+)/$',
        consumers.DashboardConsumer.as_asgi(),
        name='dashboard_ws'
    ),
]

"""
Daphne Server Command:
To run this Django Channels application with Daphne, use:

daphne -b 0.0.0.0 -p 8000 your_project.asgi:application

Options:
-b 0.0.0.0  : Bind to all interfaces (for production, consider more specific binding)
-p 8000     : Port to listen on
--access-log: Add this flag to enable access logging

For development:
daphne -b 127.0.0.1 -p 8000 your_project.asgi:application

For secure production:
daphne -e ssl:443:privateKey=key.pem:certKey=cert.pem -b 0.0.0.0 your_project.asgi:application
"""