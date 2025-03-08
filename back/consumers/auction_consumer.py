# consumers/auction_consumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
from base.models import Auction

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'
        
        # Join auction group
        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial auction state
        auction = await self.get_auction()
        if auction:
            await self.send(json.dumps({
                'type': 'initial_state',
                'auction_id': str(auction.id),
                'current_price': float(auction.current_price),
                'status': auction.status,
                'end_time': auction.end_time.isoformat() if auction.end_time else None
            }))
    
    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        
        if action == 'get_state':
            # Send current auction state
            auction = await self.get_auction()
            if auction:
                await self.send(json.dumps({
                    'type': 'auction_state',
                    'auction_id': str(auction.id),
                    'current_price': float(auction.current_price),
                    'status': auction.status,
                    'end_time': auction.end_time.isoformat() if auction.end_time else None
                }))
    
    # Broadcast auction updates
    async def auction_update(self, event):
        # Send update to WebSocket
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def get_auction(self):
        try:
            return Auction.objects.get(id=self.auction_id)
        except Auction.DoesNotExist:
            return None