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
        
        # Send initial auction data with auto-updated status
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
                'check_status': self.handle_check_status,
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
        """Enhanced bid placement with simplified logic"""
        if not self.is_authenticated():
            await self.send_error('Authentication required', 'AUTH_REQUIRED')
            return
        
        user = self.scope['user']
        if not getattr(user, 'is_verified', False):
            await self.send_error('Email verification required', 'VERIFICATION_REQUIRED')
            return
        
        amount = data.get('amount')
        if not amount or amount <= 0:
            await self.send_error('Invalid bid amount', 'INVALID_AMOUNT')
            return
        
        # Use the simplified bid creation
        bid_result = await self.create_simplified_bid(user.id, amount, data.get('max_bid'))
        
        if bid_result['success']:
            # Notify all auction participants about the new bid
            updated_auction_data = await self.get_auction_data()
            
            await self.channel_layer.group_send(self.auction_group_name, {
                'type': 'auction_update',
                'auction': updated_auction_data,
                'new_bid': bid_result['bid_data'],
                'extension_info': bid_result.get('extension_info')
            })
            
            await self.send_success('Bid placed successfully', {
                'bid': bid_result['bid_data'],
                'auction_status': bid_result.get('auction_status'),
                'extension_info': bid_result.get('extension_info')
            })
        else:
            await self.send_error(bid_result['message'], bid_result.get('code'))

    async def handle_get_auction_data(self, data):
        """Get current auction data with auto-status update"""
        auction_data = await self.get_auction_data()
        await self.send(text_data=json.dumps(auction_data))

    async def handle_check_status(self, data):
        """Check and update auction status"""
        status_info = await self.check_auction_status()
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            **status_info
        }))

    async def handle_join_auction(self, data):
        """Join auction with auto-status check"""
        if not self.is_authenticated():
            await self.send_error('Authentication required', 'AUTH_REQUIRED')
            return
        
        user = self.scope['user']
        if not getattr(user, 'is_verified', False):
            await self.send_error('Email verification required', 'VERIFICATION_REQUIRED')
            return
        
        join_result = await self.join_auction(user.id)
        if join_result['success']:
            await self.send_success('Successfully joined auction', {
                'auction_status': join_result.get('auction_status')
            })
        else:
            await self.send_error(join_result['message'], 'JOIN_FAILED')

    async def auction_update(self, event):
        """Handle auction update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'auction_update',
            'auction': event['auction'],
            'new_bid': event.get('new_bid'),
            'extension_info': event.get('extension_info')
        }))

    async def status_changed(self, event):
        """Handle auction status change broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'status_changed',
            'old_status': event.get('old_status'),
            'new_status': event.get('new_status'),
            'auction_id': event.get('auction_id')
        }))

    def is_authenticated(self):
        return hasattr(self.scope, 'user') and not isinstance(self.scope['user'], AnonymousUser)

    async def send_error(self, message, code=None):
        await self.send(text_data=json.dumps({
            'type': 'error', 
            'message': message, 
            'code': code,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_success(self, message, data=None):
        response = {
            'type': 'success', 
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        if data:
            response.update(data)
        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def auction_exists(self):
        return Auction.objects.filter(id=self.auction_id).exists()
    
    @database_sync_to_async
    def get_auction_data(self):
        """Get auction data with auto-status update"""
        try:
            auction = Auction.objects.select_related('related_property').get(id=self.auction_id)
            
            # Auto-update auction status every time data is requested
            old_status = auction.status
            auction.update_status_based_on_time()
            
            # Get recent bids
            bids = auction.bids.select_related('bidder').order_by('-bid_time')[:20]
            
            auction_data = {
                'type': 'auction_data',
                'auction': {
                    'id': auction.id,
                    'title': auction.title,
                    'slug': auction.slug,
                    'current_bid': float(auction.get_current_high_bid()),
                    'starting_bid': float(auction.starting_bid),
                    'minimum_increment': float(auction.minimum_increment),
                    'minimum_next_bid': float(auction.get_minimum_next_bid()),
                    'start_date': auction.start_date.isoformat(),
                    'end_date': auction.end_date.isoformat(),
                    'status': auction.status,
                    'status_display': auction.get_status_display(),
                    'auction_type': auction.auction_type,
                    'bid_count': auction.bid_count,
                    'is_active': auction.is_active(),
                    'is_biddable': auction.is_biddable(),
                    'time_remaining': auction.time_remaining,
                    'auto_extend_info': {
                        'minutes': auction.auto_extend_minutes,
                        'extension_count': auction.extension_count,
                        'max_extensions': auction.max_extensions,
                    },
                    'property': {
                        'id': auction.related_property.id,
                        'title': auction.related_property.title,
                        'slug': auction.related_property.slug,
                    } if auction.related_property else None
                },
                'bids': [
                    {
                        'id': bid.id,
                        'amount': float(bid.bid_amount),
                        'bidder_info': {
                            'id': bid.bidder.id,
                            'name': f"{bid.bidder.first_name} {bid.bidder.last_name}".strip() or bid.bidder.email,
                            'is_verified': getattr(bid.bidder, 'is_verified', False)
                        } if bid.bidder else None,
                        'bid_time': bid.bid_time.isoformat(),
                        'status': bid.status,
                        'is_verified': bid.is_verified,
                        'is_winning': bid.status == 'winning'
                    } for bid in bids
                ],
                'status_changed': old_status != auction.status
            }
            
            return auction_data
            
        except Auction.DoesNotExist:
            return {'type': 'error', 'message': 'Auction not found', 'code': 'AUCTION_NOT_FOUND'}
        except Exception as e:
            logger.error(f"Error getting auction data: {str(e)}")
            return {'type': 'error', 'message': 'Failed to get auction data', 'code': 'DATA_ERROR'}
    
    @database_sync_to_async
    def create_simplified_bid(self, user_id, amount, max_bid=None):
        """Simplified bid creation with enhanced logic"""
        try:
            user = User.objects.get(id=user_id)
            auction = Auction.objects.select_for_update().get(id=self.auction_id)
            
            # Auto-update auction status before processing bid
            old_status = auction.status
            auction.update_status_based_on_time()
            
            # Check if auction can accept bids (includes auto-update check)
            if not auction.is_biddable():
                return {
                    'success': False,
                    'message': f'Auction is {auction.get_status_display().lower()} and not accepting bids',
                    'code': 'AUCTION_NOT_ACTIVE',
                    'auction_status': auction.status
                }
            
            # Check minimum bid
            min_bid = auction.get_minimum_next_bid()
            if amount < min_bid:
                return {
                    'success': False,
                    'message': f'Minimum bid is ${min_bid:,.2f}',
                    'code': 'BID_TOO_LOW',
                    'minimum_bid': float(min_bid),
                    'current_bid': float(auction.get_current_high_bid())
                }
            
            # Get client IP
            client_ip = self.scope['client'][0] if hasattr(self.scope, 'client') and self.scope['client'] else None
            
            # Create the bid (will auto-process via model save method)
            bid = Bid.objects.create(
                auction=auction,
                bidder=user,
                bid_amount=amount,
                max_bid_amount=max_bid,
                status='accepted',  # Auto-accept valid bids
                ip_address=client_ip,
                is_verified=getattr(user, 'is_verified', False)
            )
            
            # Refresh auction to get updated data after bid creation
            auction.refresh_from_db()
            
            # Check for auto-extension
            extension_info = None
            if auction.check_auto_extension(bid.bid_time):
                extension_info = {
                    'extended': True,
                    'new_end_time': auction.end_date.isoformat(),
                    'extension_minutes': auction.auto_extend_minutes,
                    'extension_count': auction.extension_count
                }
            
            return {
                'success': True,
                'auction_status': auction.status,
                'extension_info': extension_info,
                'bid_data': {
                    'id': bid.id,
                    'amount': float(bid.bid_amount),
                    'bidder_info': {
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}".strip() or user.email,
                        'is_verified': getattr(user, 'is_verified', False)
                    },
                    'bid_time': bid.bid_time.isoformat(),
                    'status': bid.status,
                    'is_verified': bid.is_verified,
                    'is_winning': bid.status == 'winning'
                }
            }
            
        except User.DoesNotExist:
            return {'success': False, 'message': 'User not found', 'code': 'USER_NOT_FOUND'}
        except Auction.DoesNotExist:
            return {'success': False, 'message': 'Auction not found', 'code': 'AUCTION_NOT_FOUND'}
        except Exception as e:
            logger.error(f"Error creating bid: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to place bid. Please try again.',
                'code': 'BID_ERROR'
            }
    
    @database_sync_to_async
    def check_auction_status(self):
        """Check and return auction status information"""
        try:
            auction = Auction.objects.get(id=self.auction_id)
            old_status = auction.status
            auction.update_status_based_on_time()
            
            return {
                'auction_id': auction.id,
                'status': auction.status,
                'status_display': auction.get_status_display(),
                'is_active': auction.is_active(),
                'is_biddable': auction.is_biddable(),
                'time_remaining': auction.time_remaining,
                'status_changed': old_status != auction.status,
                'old_status': old_status if old_status != auction.status else None
            }
        except Exception as e:
            logger.error(f"Error checking auction status: {str(e)}")
            return {
                'error': 'Failed to check auction status',
                'code': 'STATUS_CHECK_ERROR'
            }
    
    @database_sync_to_async
    def join_auction(self, user_id):
        """Join auction with status validation"""
        try:
            auction = Auction.objects.get(id=self.auction_id)
            
            # Auto-update status first
            auction.update_status_based_on_time()
            
            if auction.status not in ['scheduled', 'live']:
                return {
                    'success': False,
                    'message': f'Auction is {auction.get_status_display().lower()} and not open for registration',
                    'auction_status': auction.status
                }
            
            if auction.registration_deadline and timezone.now() > auction.registration_deadline:
                return {
                    'success': False,
                    'message': 'Registration deadline has passed',
                    'auction_status': auction.status
                }
            
            return {
                'success': True,
                'message': 'Successfully joined auction',
                'auction_status': auction.status
            }
            
        except Exception as e:
            logger.error(f"Error joining auction: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to join auction',
                'code': 'JOIN_ERROR'
            }