# consumers/metrics_middleware.py
import logging
import time
from channels.middleware import BaseMiddleware
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketMetricsMiddleware(BaseMiddleware):
    """
    Middleware to track WebSocket metrics such as connection time, message counts, and errors.
    """
    
    async def __call__(self, scope, receive, send):
        # Start time tracking
        start_time = time.time()
        
        # Extract data from scope
        connection_type = scope['type']
        path = scope.get('path', 'unknown')
        client_host = scope.get('client', ['unknown', 0])[0]
        
        # Skip non-websocket requests
        if connection_type != 'websocket':
            return await super().__call__(scope, receive, send)
            
        # Initialize connection metrics
        connection_id = f"{client_host}_{int(start_time)}"
        scope['_metrics'] = {
            'connection_id': connection_id,
            'connect_time': start_time,
            'messages_received': 0,
            'messages_sent': 0,
            'errors': 0,
            'path': path,
            'client_host': client_host,
        }
        
        # Create wrapped receive and send functions to track messages
        async def metrics_receive():
            message = await receive()
            if message['type'] == 'websocket.receive':
                scope['_metrics']['messages_received'] += 1
            return message
            
        async def metrics_send(message):
            if message['type'] == 'websocket.send':
                scope['_metrics']['messages_sent'] += 1
            elif message['type'] == 'websocket.close':
                # Log connection metrics when closing
                duration = time.time() - scope['_metrics']['connect_time']
                messages_received = scope['_metrics']['messages_received']
                messages_sent = scope['_metrics']['messages_sent']
                errors = scope['_metrics']['errors']
                
                logger.info(
                    f"WebSocket metrics - Connection ID: {connection_id}, "
                    f"Path: {path}, Duration: {duration:.2f}s, "
                    f"Messages received: {messages_received}, "
                    f"Messages sent: {messages_sent}, "
                    f"Errors: {errors}"
                )
                
                # You can also store these metrics in a database or send to monitoring system
                try:
                    await self.store_metrics(scope['_metrics'], duration)
                except Exception as e:
                    logger.error(f"Error storing WebSocket metrics: {str(e)}")
                
            await send(message)
        
        try:
            # Call the next middleware or consumer with our wrapped functions
            return await super().__call__(scope, metrics_receive, metrics_send)
        except Exception as e:
            # Track errors
            if '_metrics' in scope:
                scope['_metrics']['errors'] += 1
            
            # Log the error
            logger.error(f"WebSocket error: {str(e)}", exc_info=True)
            
            # Re-raise the exception
            raise
    
    async def store_metrics(self, metrics, duration):
        """
        Store WebSocket metrics - can be implemented to store in database
        or send to a monitoring system.
        
        This is a placeholder implementation.
        """
        # In a real implementation, you might store these metrics in your database
        # or send them to a monitoring system like Prometheus, Datadog, etc.
        pass