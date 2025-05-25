import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import Auction, Bid
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'
        
        if not await self.auction_exists():
            await self.close(code=4004)
            return
        
        await self.channel_layer.group_add(self.auction_group_name, self.channel_name)
        await self.accept()
        
        auction_data = await self.get_auction_data()
        await self.send(text_data=json.dumps(auction_data))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.auction_group_name, self.channel_name)
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            handlers = {
                'place_bid': self.handle_place_bid,
                'get_auction_data': self.handle_get_auction_data,
                'join_auction': self.handle_join_auction,
            }
            
            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                await self.send_error(f'Unknown message type: {message_type}')
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {str(e)}")
            await self.send_error('An error occurred processing your request')
    
    async def handle_place_bid(self, data):
        if not self.is_authenticated():
            await self.send_error('Authentication required to place bids', 'AUTH_REQUIRED')
            return
        
        user = self.scope['user']
        if not getattr(user, 'is_verified', False):
            await self.send_error('Email verification required to place bids', 'VERIFICATION_REQUIRED')
            return
        
        amount = data.get('amount')
        if not amount or amount <= 0:
            await self.send_error('Invalid bid amount', 'INVALID_AMOUNT')
            return
        
        bid_result = await self.create_bid(user.id, amount, data.get('max_bid'))
        
        if bid_result['success']:
            await self.channel_layer.group_send(self.auction_group_name, {
                'type': 'auction_update',
                'auction': await self.get_auction_data(),
                'new_bid': bid_result.get('bid_data')
            })
            await self.send_success('Bid placed successfully', {'bid': bid_result.get('bid_data')})
        else:
            await self.send_error(bid_result['message'], bid_result.get('code', 'BID_FAILED'))

    async def handle_get_auction_data(self, data):
        auction_data = await self.get_auction_data()
        await self.send(text_data=json.dumps(auction_data))

    async def handle_join_auction(self, data):
        if not self.is_authenticated():
            await self.send_error('Authentication required to join auction', 'AUTH_REQUIRED')
            return
        
        user = self.scope['user']
        if not getattr(user, 'is_verified', False):
            await self.send_error('Email verification required to join auction', 'VERIFICATION_REQUIRED')
            return
        
        join_result = await self.join_auction(user.id)
        if join_result['success']:
            await self.send_success('Successfully joined auction')
        else:
            await self.send_error(join_result['message'], 'JOIN_FAILED')

    async def auction_update(self, event):
        await self.send(text_data=json.dumps(event['auction']))

    def is_authenticated(self):
        return hasattr(self.scope, 'user') and not isinstance(self.scope['user'], AnonymousUser)

    async def send_error(self, message, code=None):
        await self.send(text_data=json.dumps({
            'type': 'error', 'message': message, 'code': code
        }))

    async def send_success(self, message, data=None):
        response = {'type': 'success', 'message': message}
        if data:
            response.update(data)
        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def auction_exists(self):
        return Auction.objects.filter(id=self.auction_id).exists()
    
    @database_sync_to_async
    def get_auction_data(self):
        try:
            auction = Auction.objects.select_related('related_property').get(id=self.auction_id)
            bids = auction.bids.select_related('bidder').order_by('-bid_time')[:20]
            
            return {
                'type': 'auction_data',
                'auction': {
                    'id': auction.id, 'title': auction.title, 'slug': auction.slug,
                    'current_bid': float(auction.current_bid) if auction.current_bid else float(auction.starting_bid),
                    'starting_bid': float(auction.starting_bid), 'minimum_increment': float(auction.minimum_increment),
                    'start_date': auction.start_date.isoformat(), 'end_date': auction.end_date.isoformat(),
                    'status': auction.status, 'auction_type': auction.auction_type,
                    'bid_count': auction.bid_count, 'is_active': auction.is_active(),
                    'time_remaining': auction.time_remaining,
                    'property': {
                        'id': auction.related_property.id, 'title': auction.related_property.title,
                        'slug': auction.related_property.slug,
                    } if auction.related_property else None
                },
                'bids': [
                    {
                        'id': bid.id, 'amount': float(bid.bid_amount),
                        'bidder_info': {
                            'id': bid.bidder.id,
                            'name': f"{bid.bidder.first_name} {bid.bidder.last_name}".strip() or bid.bidder.email,
                            'is_verified': getattr(bid.bidder, 'is_verified', False)
                        } if bid.bidder else None,
                        'bid_time': bid.bid_time.isoformat(), 'status': bid.status, 'is_verified': bid.is_verified
                    } for bid in bids
                ]
            }
        except Auction.DoesNotExist:
            return {'type': 'error', 'message': 'Auction not found', 'code': 'AUCTION_NOT_FOUND'}
        except Exception as e:
            logger.error(f"Error getting auction data: {str(e)}")
            return {'type': 'error', 'message': 'Failed to get auction data', 'code': 'DATA_ERROR'}
    
    @database_sync_to_async
    def create_bid(self, user_id, amount, max_bid=None):
        try:
            user = User.objects.get(id=user_id)
            auction = Auction.objects.get(id=self.auction_id)
            
            if not auction.can_accept_bids():
                return {'success': False, 'message': 'Auction is not currently accepting bids', 'code': 'AUCTION_INACTIVE'}
            
            current_bid = auction.current_bid if auction.current_bid else auction.starting_bid
            min_bid = current_bid + auction.minimum_increment
            
            if amount < min_bid:
                return {
                    'success': False, 'message': f'Bid must be at least ${min_bid:,.2f}',
                    'code': 'BID_TOO_LOW', 'minimum_bid': float(min_bid)
                }
            
            client_ip = self.scope['client'][0] if hasattr(self.scope, 'client') and self.scope['client'] else None
            
            bid = Bid.objects.create(
                auction=auction, bidder=user, bid_amount=amount, max_bid_amount=max_bid,
                status='pending', ip_address=client_ip, is_verified=user.is_verified
            )
            
            return {
                'success': True,
                'bid_data': {
                    'id': bid.id, 'amount': float(bid.bid_amount),
                    'bidder_info': {'id': user.id, 'name': f"{user.first_name} {user.last_name}".strip() or user.email},
                    'bid_time': bid.bid_time.isoformat(), 'status': bid.status, 'is_verified': bid.is_verified
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating bid: {str(e)}")
            return {'success': False, 'message': 'Failed to place bid. Please try again.', 'code': 'BID_ERROR'}
    
    @database_sync_to_async
    def join_auction(self, user_id):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            
            if auction.status not in ['scheduled', 'live']:
                return {'success': False, 'message': 'Auction is not open for registration'}
            
            if auction.registration_deadline and timezone.now() > auction.registration_deadline:
                return {'success': False, 'message': 'Registration deadline has passed'}
            
            return {'success': True}
        except Exception as e:
            logger.error(f"Error joining auction: {str(e)}")
            return {'success': False, 'message': 'Failed to join auction'}