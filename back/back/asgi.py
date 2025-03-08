"""
ASGI config for the auction platform project.
It exposes the ASGI callable as a module-level variable named 'application'.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set Django settings module and initialize
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

# Import websocket URL patterns
from .routing import websocket_urlpatterns

# Configure the ASGI application with protocol routing
application = ProtocolTypeRouter({
    # Django's ASGI application for traditional HTTP requests
    "http": get_asgi_application(),
    
    # WebSocket handler with authentication and origin validation
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})