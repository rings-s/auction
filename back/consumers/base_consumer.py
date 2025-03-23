# consumers/base_consumer.py

import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.conf import settings

# Don't import get_user_model here - move it to methods where it's used
logger = logging.getLogger(__name__)

class BaseConsumer(AsyncWebsocketConsumer):
    """
    Base consumer class with common functionality for all WebSocket consumers.
    Provides authentication, connection management, and error handling.
    """
    # The group name prefix, to be overridden by subclasses
    group_prefix = 'base'

    async def connect(self):
        """Handle WebSocket connection"""
        # Extract parameters from URL route
        self.user = self.scope.get('user')
        self.params = self.scope['url_route']['kwargs']

        # Authenticate user if required
        if not await self.authenticate():
            logger.warning(f"Authentication failed: {self.group_prefix} connection rejected")
            await self.close(code=4003)  # Authentication failure
            return

        # Set up the group name
        self.group_name = await self.get_group_name()

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        # Send initial data if available
        try:
            initial_data = await self.get_initial_data()
            if initial_data:
                await self.send(text_data=json.dumps(initial_data))
        except Exception as e:
            logger.error(f"Error sending initial data: {str(e)}")
            await self.send_error("Failed to load initial data")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave the group
        try:
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )

            # Perform any additional cleanup
            await self.on_disconnect(close_code)
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    async def receive(self, text_data):
        """Handle messages received from the client"""
        try:
            data = json.loads(text_data)

            # Handle ping/pong for keepalive
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
                return

            # Process the message
            await self.process_message(data)

        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send_error(f"An error occurred: {str(e)}")

    # Update in consumers/base_consumer.py

    async def send_error(self, message, details=None, code=None, client_id=None):
        """
        Send an enhanced error message to the client

        Args:
            message: Main error message
            details: Additional error details (optional)
            code: Error code for client-side handling (optional)
            client_id: Client-provided ID to correlate with request (optional)
        """
        error_data = {
            'type': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }

        if details:
            error_data['details'] = details

        if code:
            error_data['code'] = code

        if client_id:
            error_data['client_id'] = client_id

        # Log the error in debug mode
        if settings.DEBUG:
            logger.debug(f"Sending WebSocket error: {json.dumps(error_data)}")

        await self.send(text_data=json.dumps(error_data))

    async def get_group_name(self):
        """
        Get the group name for this consumer.
        Override in subclasses if a different naming convention is needed.
        """
        # Default implementation for simple ID-based groups
        if 'id' in self.params:
            return f"{self.group_prefix}_{self.params['id']}"
        elif 'user_id' in self.params:
            return f"{self.group_prefix}_{self.params['user_id']}"
        else:
            # Fallback to a generic name with the first parameter
            param_key = next(iter(self.params), 'general')
            return f"{self.group_prefix}_{self.params.get(param_key, 'general')}"

    async def authenticate(self):
        """
        Authenticate the connection.
        Override in subclasses to implement custom authentication.
        """
        # Default implementation - allow all connections
        return True

    async def get_initial_data(self):
        """
        Get initial data to send on connection.
        Override in subclasses to provide specific initial data.
        """
        # Default implementation - no initial data
        return None

    async def process_message(self, data):
        """
        Process a message received from the client.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement process_message")

    async def on_disconnect(self, close_code):
        """
        Perform any cleanup needed on disconnect.
        Override in subclasses if needed.
        """
        # Default implementation - no cleanup needed
        pass

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        # Import get_user_model inside the method to avoid AppRegistryNotReady errors
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"User {user_id} not found")
            return None

    @classmethod
    def encode_datetime(cls, dt):
        """Encode a datetime object for JSON serialization"""
        if dt:
            return dt.isoformat()
        return None

    @classmethod
    def format_decimal(cls, value):
        """Format a decimal value for JSON serialization"""
        if value is not None:
            return float(value)
        return None
