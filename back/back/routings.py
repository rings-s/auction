from django.urls import re_path, path
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from base.consumers import AuctionConsumer

# WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r'^ws/auctions/(?P<auction_id>\w+)/$', AuctionConsumer.as_asgi()),
    path('ws/auctions/<int:auction_id>/', AuctionConsumer.as_asgi(), name='auction_websocket'),
]

# Main application routing
application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})