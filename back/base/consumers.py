# Enhanced back/base/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from .models import Auction, Bid
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'
        
        # Check if auction exists
        auction_exists = await self.auction_exists()
        if not auction_exists:
            await self.close()
            return
        
        # Join auction group
        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current auction data when connecting
        auction_data = await self.get_auction_data()
        await self.send(text_data=json.dumps(auction_data))
        
        logger.info(f"WebSocket connected to auction {self.auction_id}")
    
    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from auction {self.auction_id}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'place_bid':
                await self.handle_place_bid(data)
            elif data.get('type') == 'get_auction_data':
                auction_data = await self.get_auction_data()
                await self.send(text_data=json.dumps(auction_data))
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred processing your request'
            }))
    
    async def handle_place_bid(self, data):
        # Check if user is authenticated
        if isinstance(self.scope['user'], AnonymousUser):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required'
            }))
            return
        
        user_id = self.scope['user'].id
        amount = data.get('amount')
        
        if not amount or not isinstance(amount, (int, float)):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid bid amount'
            }))
            return
        
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
    def auction_exists(self):
        return Auction.objects.filter(id=self.auction_id).exists()
    
    @database_sync_to_async
    def get_auction_data(self):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            bids = auction.bids.all().order_by('-bid_time')[:10]
            
            return {
                'type': 'auction_data',
                'auction': {
                    'id': auction.id,
                    'title': auction.title,
                    'current_bid': float(auction.current_bid) if auction.current_bid else float(auction.starting_bid),
                    'starting_bid': float(auction.starting_bid),
                    'minimum_increment': float(auction.minimum_increment),
                    'end_date': auction.end_date.isoformat(),
                    'status': auction.status,
                    'bid_count': auction.bid_count
                },
                'bids': [
                    {
                        'id': bid.id,
                        'amount': float(bid.bid_amount),
                        'bidder_info': {
                            'id': bid.bidder.id,
                            'name': bid.bidder.get_full_name() or bid.bidder.email
                        },
                        'bid_time': bid.bid_time.isoformat(),
                        'status': bid.status
                    }
                    for bid in bids
                ]
            }
        except Auction.DoesNotExist:
            return {
                'type': 'error',
                'message': 'Auction not found'
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
            logger.error(f"Error creating bid: {str(e)}")
            return {'success': False, 'message': str(e)}