# consumers/utils.py
import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

logger = logging.getLogger(__name__)

def send_user_notification(user_id, notification_data):
    """
    Send a notification to a specific user via WebSocket
    
    Args:
        user_id: The ID of the user to send the notification to
        notification_data: The notification data to send
    """
    try:
        channel_layer = get_channel_layer()
        
        # Add timestamp if not present
        if 'timestamp' not in notification_data:
            notification_data['timestamp'] = timezone.now().isoformat()
        
        # Send to user's notification group
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user_id}',
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
        
        # Also send to user's dashboard if they are viewing it
        async_to_sync(channel_layer.group_send)(
            f'dashboard_{user_id}',
            {
                'type': 'notification_event',
                'notification': notification_data
            }
        )
        
        return True
    except Exception as e:
        logger.error(f"Error sending WebSocket notification: {e}")
        return False

def send_auction_update(auction_id, update_type, data):
    """
    Send an update about an auction
    
    Args:
        auction_id: The ID of the auction
        update_type: The type of update (e.g., 'price_update', 'status_update')
        data: The update data
    """
    try:
        channel_layer = get_channel_layer()
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = timezone.now().isoformat()
        
        # Send to auction group
        async_to_sync(channel_layer.group_send)(
            f'auction_{auction_id}',
            {
                'type': 'auction_update',
                'auction_id': str(auction_id),
                'update_type': update_type,
                'data': data
            }
        )
        
        # Send to bidding group as well
        async_to_sync(channel_layer.group_send)(
            f'bidding_{auction_id}',
            {
                'type': 'bidding_update',
                'update_type': update_type,
                'data': data
            }
        )
        
        return True
    except Exception as e:
        logger.error(f"Error sending auction update: {e}")
        return False

def send_chat_message(room_name, message_data):
    """
    Send a chat message to a room
    
    Args:
        room_name: The name of the chat room
        message_data: The message data to send
    """
    try:
        channel_layer = get_channel_layer()
        
        # Add timestamp if not present
        if 'timestamp' not in message_data:
            message_data['timestamp'] = timezone.now().isoformat()
        
        # Add type if not present
        if 'type' not in message_data:
            message_data['type'] = 'chat_message'
        
        # Send to chat room group
        async_to_sync(channel_layer.group_send)(
            f'chat_{room_name}',
            message_data
        )
        
        return True
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")
        return False

def send_dashboard_update(user_id, update_type, data):
    """
    Send a dashboard update to a user
    
    Args:
        user_id: The ID of the user
        update_type: The type of update (e.g., 'auction_update', 'bid_update')
        data: The update data
    """
    try:
        channel_layer = get_channel_layer()
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = timezone.now().isoformat()
        
        # Send to dashboard group
        async_to_sync(channel_layer.group_send)(
            f'dashboard_{user_id}',
            {
                'type': 'dashboard_update',
                'update_type': update_type,
                'data': data
            }
        )
        
        return True
    except Exception as e:
        logger.error(f"Error sending dashboard update: {e}")
        return False