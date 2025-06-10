from django.urls import re_path
from base.consumers import AuctionConsumer

websocket_urlpatterns = [
    re_path(r'^ws/auctions/(?P<auction_id>\w+)/$', AuctionConsumer.as_asgi()),
]