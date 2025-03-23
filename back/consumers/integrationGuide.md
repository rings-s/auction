# WebSocket Integration Guide

This guide explains how to integrate the WebSocket consumers into your Django project.

## 1. Update Project Settings

Add the following to your `settings.py`:

```python
# Django Channels Configuration
ASGI_APPLICATION = 'your_project.asgi.application'

# Channel layers for WebSocket support
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# For development, you can use the in-memory channel layer
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer',
#     },
# }

# JWT settings for WebSocket authentication
JWT_ALGORITHM = 'HS256'
```

## 2. Configure ASGI Application

Create or update your `asgi.py` file:

```python
# your_project/asgi.py
import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from consumers.middleware import JwtAuthMiddleware
from consumers.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

application = ProtocolTypeRouter({
    # Django's ASGI application for traditional HTTP requests
    "http": get_asgi_application(),
    
    # WebSocket handler with authentication middleware
    "websocket": AllowedHostsOriginValidator(
        JwtAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

## 3. Install Required Dependencies

Make sure you have the required packages installed:

```bash
pip install channels channels-redis djangorestframework-simplejwt pyjwt
```

## 4. Configure URL Routing for WebSockets

Your WebSocket URLs are already configured in `consumers/routing.py`. 

## 5. Using WebSockets in Templates

Here are examples of how to use WebSockets in your frontend:

### Connecting to the Dashboard

```javascript
// Create a WebSocket connection to the dashboard
const dashboardSocket = new WebSocket(
    `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/dashboard/${userId}/?token=${jwtToken}`
);

// Handle connection open
dashboardSocket.onopen = function(e) {
    console.log("Dashboard connection established");
};

// Handle incoming messages
dashboardSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'dashboard_data') {
        // Update dashboard with initial data
        updateDashboard(data.data);
    } else if (data.type === 'dashboard_update') {
        // Handle specific dashboard updates
        handleDashboardUpdate(data.update_type, data.data);
    } else if (data.type === 'error') {
        // Handle errors
        console.error("Dashboard error:", data.message);
    }
};

// Handle errors and connection close
dashboardSocket.onerror = function(error) {
    console.error(`Dashboard WebSocket Error: ${error.message}`);
};

dashboardSocket.onclose = function(e) {
    console.log('Dashboard connection closed');
    // Attempt to reconnect after a delay
    setTimeout(function() {
        console.log("Reconnecting to dashboard...");
        // Reconnection logic here
    }, 5000);
};

// Request specific data from the dashboard
function requestDashboardSection(section) {
    dashboardSocket.send(JSON.stringify({
        'action': 'get_section',
        'section': section
    }));
}

// Request to refresh the entire dashboard
function refreshDashboard() {
    dashboardSocket.send(JSON.stringify({
        'action': 'refresh_dashboard'
    }));
}
```

### Connecting to an Auction

```javascript
// Create a WebSocket connection to an auction
const auctionSocket = new WebSocket(
    `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/auction/${auctionId}/?token=${jwtToken}`
);

// Handle connection open
auctionSocket.onopen = function(e) {
    console.log("Auction connection established");
};

// Handle incoming messages
auctionSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'initial_state') {
        // Update UI with initial auction state
        updateAuctionUI(data);
    } else if (data.type === 'auction_update') {
        // Handle auction updates (price changes, etc.)
        handleAuctionUpdate(data.update_type, data.data);
    } else if (data.type === 'status_update') {
        // Handle status changes
        updateAuctionStatus(data.status, data.status_display, data.message);
    } else if (data.type === 'time_update') {
        // Update the countdown timer
        updateCountdown(data.time_remaining, data.end_date);
    } else if (data.type === 'extension_update') {
        // Handle auction time extension
        handleAuctionExtension(data.new_end_date, data.extension_minutes, data.reason);
    } else if (data.type === 'error') {
        // Handle errors
        console.error("Auction error:", data.message);
    }
};

// Handle errors and connection close
auctionSocket.onerror = function(error) {
    console.error(`Auction WebSocket Error: ${error.message}`);
};

auctionSocket.onclose = function(e) {
    console.log('Auction connection closed');
    // Attempt to reconnect after a delay
    setTimeout(function() {
        console.log("Reconnecting to auction...");
        // Reconnection logic here
    }, 5000);
};

// Request current auction state
function refreshAuctionState() {
    auctionSocket.send(JSON.stringify({
        'action': 'get_state'
    }));
}

// Add/remove from watchlist
function toggleWatchAuction(watching) {
    auctionSocket.send(JSON.stringify({
        'action': watching ? 'watch_auction' : 'unwatch_auction'
    }));
}
```

### Connecting to the Bidding System

```javascript
// Create a WebSocket connection to the bidding system
const biddingSocket = new WebSocket(
    `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/bidding/${auctionId}/?token=${jwtToken}`
);

// Handle connection open
biddingSocket.onopen = function(e) {
    console.log("Bidding connection established");
};

// Handle incoming messages
biddingSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'bidding_init') {
        // Initialize the bidding UI
        initBiddingUI(data.auction, data.recent_bids);
    } else if (data.type === 'new_bid') {
        // Handle new bid
        handleNewBid(data.bid);
    } else if (data.type === 'recent_bids') {
        // Update recent bids list
        updateRecentBids(data.bids);
    } else if (data.type === 'bid_history') {
        // Update complete bid history
        updateBidHistory(data.bids, data.page, data.total_pages);
    } else if (data.type === 'error') {
        // Handle errors
        handleBidError(data.message, data.client_id);
    }
};

// Handle errors and connection close
biddingSocket.onerror = function(error) {
    console.error(`Bidding WebSocket Error: ${error.message}`);
};

biddingSocket.onclose = function(e) {
    console.log('Bidding connection closed');
    // Attempt to reconnect after a delay
    setTimeout(function() {
        console.log("Reconnecting to bidding system...");
        // Reconnection logic here
    }, 5000);
};

// Place a bid
function placeBid(amount, autoBidLimit = null) {
    // Generate a client ID for optimistic UI updates
    const clientId = `bid_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
    
    // Show optimistic UI update
    showPendingBid(amount, clientId);
    
    // Send the bid
    biddingSocket.send(JSON.stringify({
        'action': 'place_bid',
        'amount': amount,
        'auto_bid_limit': autoBidLimit,
        'user_id': currentUserId,
        'client_id': clientId
    }));
    
    return clientId;
}

// Get recent bids
function getRecentBids(limit = 10) {
    biddingSocket.send(JSON.stringify({
        'action': 'get_recent_bids',
        'limit': limit
    }));
}

// Get bid history with pagination
function getBidHistory(page = 1, pageSize = 20) {
    biddingSocket.send(JSON.stringify({
        'action': 'get_bid_history',
        'page': page,
        'page_size': pageSize
    }));
}
```

### Connecting to the Notification System

```javascript
// Create a WebSocket connection to the notification system
const notificationSocket = new WebSocket(
    `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/notifications/${userId}/?token=${jwtToken}`
);

// Handle connection open
notificationSocket.onopen = function(e) {
    console.log("Notification connection established");
};

// Handle incoming messages
notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'notifications') {
        // Update notifications list
        updateNotificationsList(data.notifications);
    } else if (data.type === 'new_notification') {
        // Handle a new notification
        handleNewNotification(data.notification);
    } else if (data.type === 'notification_read') {
        // Update UI to mark notification as read
        markNotificationRead(data.notification_id);
    } else if (data.type === 'all_read') {
        // Update UI to mark all notifications as read
        markAllNotificationsRead();
    } else if (data.type === 'unread_count') {
        // Update notification badge count
        updateNotificationBadge(data.count);
    } else if (data.type === 'error') {
        // Handle errors
        console.error("Notification error:", data.message);
    }
};

// Handle errors and connection close
notificationSocket.onerror = function(error) {
    console.error(`Notification WebSocket Error: ${error.message}`);
};

notificationSocket.onclose = function(e) {
    console.log('Notification connection closed');
    // Attempt to reconnect after a delay
    setTimeout(function() {
        console.log("Reconnecting to notification system...");
        // Reconnection logic here
    }, 5000);
};

// Mark a notification as read
function markNotificationRead(notificationId) {
    notificationSocket.send(JSON.stringify({
        'action': 'mark_read',
        'notification_id': notificationId
    }));
}

// Mark all notifications as read
function markAllNotificationsRead() {
    notificationSocket.send(JSON.stringify({
        'action': 'mark_all_read'
    }));
}

// Get notifications (with optional pagination)
function getNotifications(limit = 50, offset = 0) {
    notificationSocket.send(JSON.stringify({
        'action': 'get_notifications',
        'limit': limit,
        'offset': offset
    }));
}

// Get unread notification count
function getUnreadCount() {
    notificationSocket.send(JSON.stringify({
        'action': 'get_unread_count'
    }));
}
```

### Connecting to a Chat Room

```javascript
// Create a WebSocket connection to a chat room
const chatSocket = new WebSocket(
    `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/chat/${roomName}/?token=${jwtToken}`
);

// Handle connection open
chatSocket.onopen = function(e) {
    console.log("Chat connection established");
};

// Handle incoming messages
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'chat_history') {
        // Initialize chat with message history
        initChatHistory(data.messages, data.thread);
    } else if (data.type === 'message') {
        // Handle a new chat message
        handleChatMessage(data);
    } else if (data.type === 'system') {
        // Handle system messages (join/leave)
        handleSystemMessage(data.message, data.event);
    } else if (data.type === 'typing') {
        // Handle typing indicator
        updateTypingIndicator(data.user_id, data.username, data.is_typing);
    } else if (data.type === 'read_receipt') {
        // Handle read receipt
        updateReadReceipt(data.message_id, data.user_id);
    } else if (data.type === 'message_history') {
        // Handle loading more message history
        appendMessageHistory(data.messages, data.has_more);
    } else if (data.type === 'error') {
        // Handle errors
        handleChatError(data.message, data.client_id);
    }
};

// Handle errors and connection close
chatSocket.onerror = function(error) {
    console.error(`Chat WebSocket Error: ${error.message}`);
};

chatSocket.onclose = function(e) {
    console.log('Chat connection closed');
    // Attempt to reconnect after a delay
    setTimeout(function() {
        console.log("Reconnecting to chat...");
        // Reconnection logic here
    }, 5000);
};

// Send a chat message
function sendChatMessage(message) {
    // Generate a client ID for optimistic UI updates
    const clientId = `msg_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
    
    // Show optimistic UI update
    showPendingMessage(message, clientId);
    
    // Send the message
    chatSocket.send(JSON.stringify({
        'type': 'message',
        'message': message,
        'client_id': clientId
    }));
    
    return clientId;
}

// Send typing indicator
function sendTypingIndicator(isTyping) {
    chatSocket.send(JSON.stringify({
        'type': 'typing',
        'is_typing': isTyping
    }));
}

// Mark a message as read
function markMessageRead(messageId) {
    chatSocket.send(JSON.stringify({
        'type': 'read_receipt',
        'message_id': messageId
    }));
}

// Load more message history
function loadMoreMessages(beforeId) {
    chatSocket.send(JSON.stringify({
        'type': 'load_more',
        'before_id': beforeId,
        'limit': 20
    }));
}
```

## 6. Using WebSockets in Django Views

You can use the WebSocket utilities in your Django views to send real-time updates:

```python
from consumers.utils import (
    send_user_notification, 
    send_auction_update,
    send_chat_message,
    send_dashboard_update
)

def complete_auction(request, auction_id):
    # Your business logic here...
    
    # Send WebSocket update to all clients watching this auction
    send_auction_update(
        auction_id=auction_id,
        update_type='status_update',
        data={
            'status': 'closed',
            'status_display': 'Closed',
            'message': 'Auction has ended'
        }
    )
    
    # Send notification to the auction winner
    send_user_notification(
        user_id=winning_bidder_id,
        notification_data={
            'title': 'You won the auction!',
            'content': f'Congratulations! You won the auction for {auction_title}',
            'notification_type': 'winning_bid',
            'related_auction_id': auction_id,
            'icon': 'trophy',
            'color': 'success',
            'action_url': f'/auctions/{auction_id}/contracts/create/'
        }
    )
    
    # Update the dashboard for the seller
    send_dashboard_update(
        user_id=seller_id,
        update_type='auction_completed',
        data={
            'auction_id': auction_id,
            'title': auction_title,
            'final_price': final_price,
            'winner_name': winner_name
        }
    )
    
    # Other response logic...
```

## 7. Testing WebSockets

Here's a simple script to test your WebSocket connections from the command line:

```python
# test_websocket.py
import asyncio
import websockets
import json
import time

async def test_auction_socket():
    uri = "ws://localhost:8000/ws/auction/YOUR_AUCTION_ID/?token=YOUR_JWT_TOKEN"
    
    async with websockets.connect(uri) as websocket:
        # Get initial state
        initial_response = await websocket.recv()
        print(f"Initial state: {initial_response}")
        
        # Send a state request
        await websocket.send(json.dumps({
            'action': 'get_state'
        }))
        
        # Get response
        response = await websocket.recv()
        print(f"State response: {response}")
        
        # Keep connection open to receive updates
        for _ in range(10):
            try:
                update = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Update received: {update}")
            except asyncio.TimeoutError:
                print("No updates received in the last 5 seconds")
            await asyncio.sleep(5)

asyncio.run(test_auction_socket())
```

Run this with:

```bash
python test_websocket.py
```

## 8. Troubleshooting

If you encounter issues with your WebSocket connections:

1. Check your `CHANNEL_LAYERS` configuration - make sure Redis is running if using Redis.
2. Verify your WebSocket URLs are correctly set up in `routing.py`.
3. Ensure your authentication middleware is correctly validating the JWT token.
4. Check for any errors in your Django development server logs.
5. Look for WebSocket connection errors in your browser's JavaScript console.
6. Make sure your ASGI application is properly configured in `asgi.py`.
7. If using deployment platforms like Daphne or Uvicorn, ensure they are configured to handle WebSockets.