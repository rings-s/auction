# consumers/bidding_consumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
from base.models import Auction, Bid
from django.contrib.auth import get_user_model

User = get_user_model()

class BiddingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.bidding_group_name = f'bidding_{self.auction_id}'
        
        # Join bidding group
        await self.channel_layer.group_add(
            self.bidding_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send recent bids
        recent_bids = await self.get_recent_bids()
        for bid in recent_bids:
            await self.send(json.dumps({
                'type': 'new_bid',
                'bid': bid
            }))
    
    async def disconnect(self, close_code):
        # Leave bidding group
        await self.channel_layer.group_discard(
            self.bidding_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        
        if action == 'place_bid':
            # Get data from request
            amount = text_data_json.get('amount')
            auto_bid_limit = text_data_json.get('auto_bid_limit')
            user_id = text_data_json.get('user_id')
            
            # Create bid
            bid = await self.create_bid(user_id, amount, auto_bid_limit)
            
            if bid:
                # Notify all clients about new bid
                await self.channel_layer.group_send(
                    self.bidding_group_name,
                    {
                        'type': 'new_bid_message',
                        'bid': bid
                    }
                )
                
                # Also notify auction group about price update
                auction = await self.get_auction()
                if auction:
                    await self.channel_layer.group_send(
                        f'auction_{self.auction_id}',
                        {
                            'type': 'auction_update',
                            'id': str(datetime.now().timestamp()),
                            'auction_id': self.auction_id,
                            'action': 'price_update',
                            'data': {
                                'price': float(auction.current_price)
                            },
                            'timestamp': datetime.now().isoformat()
                        }
                    )
    
    # Receive bid from bidding group
    async def new_bid_message(self, event):
        # Send bid to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_bid',
            'bid': event['bid']
        }))
    
    @database_sync_to_async
    def get_recent_bids(self, limit=10):
        try:
            bids = Bid.objects.filter(auction_id=self.auction_id).order_by('-created_at')[:limit]
            
            # Convert to dict for JSON serialization
            return [
                {
                    'id': str(bid.id),
                    'auction': str(bid.auction.id),
                    'bidder': str(bid.bidder.id),
                    'bidder_details': {
                        'first_name': bid.bidder.first_name,
                        'last_name': bid.bidder.last_name
                    },
                    'amount': float(bid.amount),
                    'auto_bid_limit': float(bid.auto_bid_limit) if bid.auto_bid_limit else None,
                    'status': bid.status,
                    'created_at': bid.created_at.isoformat()
                }
                for bid in bids
            ]
        except Exception as e:
            print(f"Error getting recent bids: {e}")
            return []
    
    @database_sync_to_async
    def create_bid(self, user_id, amount, auto_bid_limit=None):
        try:
            # Get user and auction
            user = User.objects.get(id=user_id)
            auction = Auction.objects.get(id=self.auction_id)
            
            # Validate bid
            if auction.status != 'ACTIVE':
                return None
                
            if float(amount) <= float(auction.current_price):
                return None
                
            if auction.seller.id == user_id:
                return None
            
            # Get client IP from WebSocket scope
            client_ip = self.scope.get('client', ['unknown'])[0]
            if client_ip == 'unknown':
                client_ip = '0.0.0.0'  # Fallback IP if not available
            
            # Create bid with ip_address
            bid = Bid.objects.create(
                auction=auction,
                bidder=user,
                amount=amount,
                auto_bid_limit=auto_bid_limit,
                status='PLACED',
                ip_address=client_ip
            )
            
            # Update auction price
            auction.current_price = amount
            auction.save()
            
            # Return bid data
            return {
                'id': str(bid.id),
                'auction': str(bid.auction.id),
                'bidder': str(bid.bidder.id),
                'bidder_details': {
                    'first_name': bid.bidder.first_name,
                    'last_name': bid.bidder.last_name
                },
                'amount': float(bid.amount),
                'auto_bid_limit': float(bid.auto_bid_limit) if bid.auto_bid_limit else None,
                'status': bid.status,
                'created_at': bid.created_at.isoformat()
            }
        except Exception as e:
            print(f"Error creating bid: {e}")
            return None
    
    @database_sync_to_async
    def get_auction(self):
        try:
            return Auction.objects.get(id=self.auction_id)
        except Auction.DoesNotExist:
            return None