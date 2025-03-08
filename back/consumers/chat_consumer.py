# your_auction_app/consumers.py

from django.utils import timezone
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
import json
import re
import logging
from django.db import transaction
from base.models import Message
from django.core.exceptions import ValidationError

# Set up logger
logger = logging.getLogger(__name__)

class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        # Enhanced room_name validation
        if not self._validate_room_name(self.room_name):
            logger.warning(f"Rejected connection attempt with invalid room_name: {self.room_name}")
            self.close(code=4000)  # Custom close code for invalid room
            return
            
        self.room_group_name = f'chat_{self.room_name}'
        
        # Get user information
        self.user = self.scope.get('user', None)
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        self.accept()
        
        # Send join message to room if authenticated
        if self.user and not self.user.is_anonymous:
            username = self.user.first_name or self.user.email.split('@')[0]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'system_message',
                    'message': f"{username} joined the chat",
                    'event': 'join'
                }
            )
    
    def disconnect(self, close_code):
        # Send leave message if user was authenticated
        if hasattr(self, 'user') and self.user and not self.user.is_anonymous:
            username = self.user.first_name or self.user.email.split('@')[0]
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'system_message',
                    'message': f"{username} left the chat",
                    'event': 'leave'
                }
            )
            
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    def receive_json(self, content):
        # Get the user from the scope if authenticated
        user = self.scope.get('user', None)
        
        # Handle ping messages for connection keepalive
        if content.get('type') == 'ping':
            self.send_json({
                'type': 'pong',
                'timestamp': timezone.now().isoformat()
            })
            return
        
        message_text = content.get('message', '')
        user_id = content.get('user_id')
        client_id = content.get('client_id', '')  # Client-generated ID for optimistic updates
        
        # Validate message content
        if not message_text or not message_text.strip():
            self.send_json({
                'type': 'error',
                'error': 'Message cannot be empty',
                'client_id': client_id
            })
            return
            
        if len(message_text) > 5000:  # Limit message length
            self.send_json({
                'type': 'error',
                'error': 'Message is too long (max 5000 characters)',
                'client_id': client_id
            })
            return
        
        # Save message to database with error handling
        message_id = None
        if user and not user.is_anonymous:
            try:
                with transaction.atomic():
                    # Create message instance
                    message = Message.objects.create(
                        sender=user,
                        room_id=self.room_name,
                        content=message_text
                    )
                    message_id = str(message.id)
                    username = user.first_name or user.email.split('@')[0]
            except ValidationError as e:
                error_message = str(e)
                logger.error(f"Validation error when creating message: {error_message}")
                self.send_json({
                    'type': 'error',
                    'error': 'Message validation failed',
                    'details': error_message,
                    'client_id': client_id
                })
                return
            except Exception as e:
                error_message = str(e)
                logger.error(f"Error creating message: {error_message}")
                self.send_json({
                    'type': 'error',
                    'error': 'Message could not be saved',
                    'client_id': client_id
                })
                return
        else:
            username = 'Anonymous'
        
        # Send message to room group
        try:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'user_id': user_id,
                    'username': username,
                    'id': message_id,
                    'client_id': client_id,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error sending message to group: {error_message}")
            self.send_json({
                'type': 'error',
                'error': 'Message could not be delivered to the group',
                'client_id': client_id
            })
    
    # Receive message from room group
    def chat_message(self, event):
        # Send message to WebSocket
        self.send_json({
            'type': 'message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'id': event.get('id'),
            'client_id': event.get('client_id', ''),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        })
    
    # System messages (join/leave)
    def system_message(self, event):
        self.send_json({
            'type': 'system',
            'message': event['message'],
            'event': event['event'],
            'timestamp': timezone.now().isoformat()
        })
    
    # Helper method to validate room_name
    def _validate_room_name(self, room_name):
        """
        Validate room_name to prevent security issues.
        Rules:
        - Must be alphanumeric with underscores, hyphens or dots only
        - Length between 3 and 100 characters
        - No consecutive special characters
        - Cannot start or end with special character
        """
        # Basic length check
        if not (3 <= len(room_name) <= 100):
            return False
            
        # Check for consecutive special characters
        if '__' in room_name or '--' in room_name or '..' in room_name:
            return False
            
        # Check start/end characters
        if room_name[0] in '_-.' or room_name[-1] in '_-.':
            return False
            
        # Additional pattern validation
        pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\-\.]*[a-zA-Z0-9]$')
        if not pattern.match(room_name) and len(room_name) > 1:
            return False
            
        return True