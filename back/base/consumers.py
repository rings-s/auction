# back/base/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Auction, Bid

User = get_user_model()

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
        
        # Send current auction data when connecting
        auction_data = await self.get_auction_data()
        await self.send(text_data=json.dumps(auction_data))
    
    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get('type') == 'place_bid':
            user_id = self.scope['user'].id
            amount = data.get('amount')
            
            # Create bid in database
            bid_result = await self.create_bid(user_id, amount)
            
            if bid_result['success']:
                # Send update to all connected clients
                await self.channel_layer.group_send(
                    self.auction_group_name,
                    {
                        'type': 'auction_update',
                        'auction': await self.get_auction_data()
                    }
                )
            else:
                # Send error back to client
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': bid_result['message']
                }))
    
    async def auction_update(self, event):
        # Send auction update to WebSocket
        await self.send(text_data=json.dumps(event['auction']))
    
    @database_sync_to_async
    def get_auction_data(self):
        auction = Auction.objects.get(id=self.auction_id)
        bids = auction.bids.all().order_by('-bid_time')[:10]
        
        return {
            'type': 'auction_data',
            'auction': {
                'id': auction.id,
                'title': auction.title,
                'current_bid': float(auction.current_bid) if auction.current_bid else float(auction.starting_bid),
                'end_time': auction.end_date.isoformat(),
                'status': auction.status,
                'bid_count': auction.bid_count
            },
            'bids': [
                {
                    'id': bid.id,
                    'amount': float(bid.bid_amount),
                    'bidder': bid.bidder.get_full_name() or bid.bidder.email,
                    'time': bid.bid_time.isoformat(),
                    'status': bid.status
                }
                for bid in bids
            ]
        }
    
    @database_sync_to_async
    def create_bid(self, user_id, amount):
        try:
            user = User.objects.get(id=user_id)
            auction = Auction.objects.get(id=self.auction_id)
            
            # Check if auction is active
            if not auction.can_accept_bids():
                return {'success': False, 'message': 'Auction is not active'}
            
            # Check minimum bid
            min_bid = auction.current_bid + auction.minimum_increment if auction.current_bid else auction.starting_bid
            if amount < min_bid:
                return {
                    'success': False, 
                    'message': f'Bid must be at least {min_bid}'
                }
            
            # Create the bid
            bid = Bid.objects.create(
                auction=auction,
                bidder=user,
                bid_amount=amount,
                status='pending'
            )
            
            # Process bid (mark as winning if highest)
            if not auction.current_bid or amount > auction.current_bid:
                # Update auction current bid
                auction.current_bid = amount
                auction.save(update_fields=['current_bid'])
                
                # Update bid status
                bid.status = 'winning'
                bid.save(update_fields=['status'])
                
                # Mark previous winning bids as outbid
                Bid.objects.filter(
                    auction=auction,
                    status='winning'
                ).exclude(id=bid.id).update(status='outbid')
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}