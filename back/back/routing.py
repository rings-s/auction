"""
WebSocket routing configuration for the real estate auction platform.
Defines URL patterns for WebSocket connections.
"""

from django.urls import re_path

# Import WebSocket consumer classes
from consumers.chat_consumer import ChatConsumer
from consumers.auction_consumer import AuctionConsumer
from consumers.bidding_consumer import BiddingConsumer
from consumers.notification_consumer import NotificationConsumer
from consumers.dashboard_consumer import DashboardConsumer
from consumers.base_consumer import BaseConsumer

# WebSocket URL patterns
# These patterns match the existing frontend expectations
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
    
    # Alternative URL patterns for backward compatibility with our new implementations
    re_path(
        r'ws/auction/(?P<auction_id>[0-9a-f-]{36})/$',
        AuctionConsumer.as_asgi(),
        name='auction_ws_alt'
    ),
    
    re_path(
        r'ws/bidding/(?P<auction_id>[0-9a-f-]{36})/$',
        BiddingConsumer.as_asgi(),
        name='bidding_ws_alt'
    ),
]

"""
Implementation notes:

1. Consumer parameter naming:
   - ChatConsumer uses 'room_name'
   - AuctionConsumer uses 'auction_id'
   - BiddingConsumer uses 'auction_id'
   - NotificationConsumer uses 'user_id'
   - DashboardConsumer uses 'user_id'

2. URL structure maintained for backward compatibility:
   - Chat: ws/chat/{room_name}/
   - Auction updates: ws/auctions/{auction_id}/updates/
   - Bidding: ws/auctions/{auction_id}/bids/
   - Notifications: ws/notifications/{user_id}/
   - Dashboard: ws/dashboard/{user_id}/


3. For production deployment with Daphne:
   daphne -b 0.0.0.0 -p 8000 your_project.asgi:application
   
   For secure production:
   daphne -e ssl:443:privateKey=key.pem:certKey=cert.pem -b 0.0.0.0 your_project.asgi:application



4. Configuration for ASGI in asgi.py:
   
   ```python
   import os
   import django
   from django.core.asgi import get_asgi_application
   from channels.routing import ProtocolTypeRouter, URLRouter
   from channels.auth import AuthMiddlewareStack
   from consumers.middleware import JwtAuthMiddleware
   from consumers.routing import websocket_urlpatterns

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
   django.setup()

   application = ProtocolTypeRouter({
       # Django's ASGI application for traditional HTTP requests
       "http": get_asgi_application(),
       
       # WebSocket handler with authentication middleware
       "websocket": JwtAuthMiddleware(
           URLRouter(websocket_urlpatterns)
       ),
   })
   ```
"""