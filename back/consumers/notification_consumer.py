# consumers/notification_consumer.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from datetime import datetime
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from base.models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.notification_group_name = f'notifications_{self.user_id}'
        
        # Authenticate
        user = self.scope.get('user')
        if not user or not user.is_authenticated or str(user.id) != self.user_id:
            logger.warning(f"Unauthorized connection attempt to notifications for user_id: {self.user_id}")
            await self.close(code=4003)  # Custom close code for authentication failure
            return
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications
        try:
            notifications = await self.get_notifications()
            await self.send(text_data=json.dumps({
                'type': 'notifications',
                'notifications': notifications
            }))
        except Exception as e:
            logger.error(f"Error sending initial notifications: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Failed to load notifications'
            }))
    
    async def disconnect(self, close_code):
        # Leave notification group
        try:
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            
            # Handle ping messages for connection keepalive
            if text_data_json.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
                return
                
            action = text_data_json.get('action')
            
            if action == 'mark_read':
                notification_id = text_data_json.get('notification_id')
                if notification_id:
                    success = await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        'type': 'notification_read',
                        'notification_id': notification_id,
                        'success': success
                    }))
                    
                    # Also broadcast to other connected clients for this user
                    await self.channel_layer.group_send(
                        self.notification_group_name,
                        {
                            'type': 'notification_read_event',
                            'notification_id': notification_id
                        }
                    )
                
            elif action == 'mark_all_read':
                success = await self.mark_all_notifications_read()
                await self.send(text_data=json.dumps({
                    'type': 'all_read',
                    'success': success
                }))
                
                # Also broadcast to other connected clients for this user
                await self.channel_layer.group_send(
                    self.notification_group_name,
                    {
                        'type': 'all_read_event'
                    }
                )
                
            elif action == 'mark_displayed':
                notification_id = text_data_json.get('notification_id')
                if notification_id:
                    await self.mark_notification_displayed(notification_id)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': f'An error occurred: {str(e)}'
            }))
    
    # Event handlers for group messages
    async def notification_message(self, event):
        """Handle new notification event"""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))
    
    async def notification_read_event(self, event):
        """Handle notification read event"""
        await self.send(text_data=json.dumps({
            'type': 'notification_read',
            'notification_id': event['notification_id']
        }))
    
    async def all_read_event(self, event):
        """Handle all notifications read event"""
        await self.send(text_data=json.dumps({
            'type': 'all_read'
        }))
    
    # Database access methods
    @database_sync_to_async
    def get_notifications(self, limit=50):
        try:
            notifications = Notification.objects.filter(
                user_id=self.user_id
            ).order_by('-created_at')[:limit]
            
            # Convert to dict for JSON serialization
            return [
                {
                    'id': str(notification.id),
                    'user_id': str(notification.user.id),
                    'message': notification.message,
                    'type': notification.notification_type,
                    'read': notification.read,
                    'displayed': notification.displayed,
                    'related_object_id': str(notification.related_object_id) if notification.related_object_id else None,
                    'related_object_type': notification.related_object_type,
                    'created_at': notification.created_at.isoformat()
                }
                for notification in notifications
            ]
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return []
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            notification.read = True
            notification.save(update_fields=['read'])
            return True
        except ObjectDoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {self.user_id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification read: {str(e)}")
            return False
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        try:
            result = Notification.objects.filter(
                user_id=self.user_id,
                read=False
            ).update(read=True)
            return result > 0  # True if at least one notification was updated
        except Exception as e:
            logger.error(f"Error marking all notifications read: {str(e)}")
            return False
    
    @database_sync_to_async
    def mark_notification_displayed(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            notification.displayed = True
            notification.save(update_fields=['displayed'])
            return True
        except ObjectDoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {self.user_id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification displayed: {str(e)}")
            return False