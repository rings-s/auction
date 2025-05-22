# Enhanced back/base/consumers.py
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
        
        # Check if auction exists
        auction_exists = await self.auction_exists()
        if not auction_exists:
            await self.close(code=4004)
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
        
        # Log connection with user info
        user_info = "Anonymous"
        if hasattr(self.scope, 'user') and not isinstance(self.scope['user'], AnonymousUser):
            user_info = f"{self.scope['user'].email} (ID: {self.scope['user'].id})"
        
        logger.info(f"WebSocket connected to auction {self.auction_id} by {user_info}")
    
    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )
        
        # Log disconnection
        user_info = "Anonymous"
        if hasattr(self.scope, 'user') and not isinstance(self.scope['user'], AnonymousUser):
            user_info = f"{self.scope['user'].email} (ID: {self.scope['user'].id})"
        
        logger.info(f"WebSocket disconnected from auction {self.auction_id} by {user_info}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'place_bid':
                await self.handle_place_bid(data)
            elif message_type == 'get_auction_data':
                auction_data = await self.get_auction_data()
                await self.send(text_data=json.dumps(auction_data))
            elif message_type == 'join_auction':
                await self.handle_join_auction(data)
            elif message_type == 'extend_auction':
                await self.handle_extend_auction(data)
            elif message_type == 'end_auction':
                await self.handle_end_auction(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred processing your request'
            }))
    
    async def handle_place_bid(self, data):
        # Check if user is authenticated - consistent with accounts app
        if not hasattr(self.scope, 'user') or isinstance(self.scope['user'], AnonymousUser):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required to place bids',
                'code': 'AUTH_REQUIRED'
            }))
            return
        
        user = self.scope['user']
        
        # Check if user is verified (consistent with accounts app verification)
        if not getattr(user, 'is_verified', False):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Email verification required to place bids',
                'code': 'VERIFICATION_REQUIRED'
            }))
            return
        
        # Check if user is active
        if not user.is_active:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Account is inactive',
                'code': 'ACCOUNT_INACTIVE'
            }))
            return
        
        user_id = user.id
        amount = data.get('amount')
        max_bid = data.get('max_bid')  # For auto-bidding
        
        # Validate bid amount
        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid bid amount',
                'code': 'INVALID_AMOUNT'
            }))
            return
        
        # Create bid in database
        bid_result = await self.create_bid(user_id, amount, max_bid)
        
        if bid_result['success']:
            # Send update to all connected clients
            await self.channel_layer.group_send(
                self.auction_group_name,
                {
                    'type': 'auction_update',
                    'auction': await self.get_auction_data(),
                    'new_bid': bid_result.get('bid_data')
                }
            )
            
            # Send success confirmation to bidder
            await self.send(text_data=json.dumps({
                'type': 'bid_success',
                'message': 'Bid placed successfully',
                'bid': bid_result.get('bid_data')
            }))
        else:
            # Send error back to client
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': bid_result['message'],
                'code': bid_result.get('code', 'BID_FAILED')
            }))
    
    async def handle_join_auction(self, data):
        # Handle auction registration/joining
        if not hasattr(self.scope, 'user') or isinstance(self.scope['user'], AnonymousUser):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required to join auction',
                'code': 'AUTH_REQUIRED'
            }))
            return
        
        user = self.scope['user']
        
        # Check if user is verified
        if not getattr(user, 'is_verified', False):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Email verification required to join auction',
                'code': 'VERIFICATION_REQUIRED'
            }))
            return
        
        # Add user to auction participants (you might want to implement this)
        join_result = await self.join_auction(user.id)
        
        if join_result['success']:
            await self.send(text_data=json.dumps({
                'type': 'join_success',
                'message': 'Successfully joined auction'
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': join_result['message'],
                'code': 'JOIN_FAILED'
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
            auction = Auction.objects.select_related('related_property').get(id=self.auction_id)
            bids = auction.bids.select_related('bidder').order_by('-bid_time')[:20]
            
            return {
                'type': 'auction_data',
                'auction': {
                    'id': auction.id,
                    'title': auction.title,
                    'slug': auction.slug,
                    'current_bid': float(auction.current_bid) if auction.current_bid else float(auction.starting_bid),
                    'starting_bid': float(auction.starting_bid),
                    'minimum_increment': float(auction.minimum_increment),
                    'start_date': auction.start_date.isoformat(),
                    'end_date': auction.end_date.isoformat(),
                    'status': auction.status,
                    'auction_type': auction.auction_type,
                    'bid_count': auction.bid_count,
                    'registered_bidders': auction.registered_bidders,
                    'is_active': auction.is_active(),
                    'time_remaining': auction.time_remaining,
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
                            'email': bid.bidder.email if bid.bidder.email else None,
                            'is_verified': getattr(bid.bidder, 'is_verified', False)
                        } if bid.bidder else None,
                        'bid_time': bid.bid_time.isoformat(),
                        'status': bid.status,
                        'is_verified': bid.is_verified
                    }
                    for bid in bids
                ]
            }
        except Auction.DoesNotExist:
            return {
                'type': 'error',
                'message': 'Auction not found',
                'code': 'AUCTION_NOT_FOUND'
            }
        except Exception as e:
            logger.error(f"Error getting auction data: {str(e)}")
            return {
                'type': 'error',
                'message': 'Failed to get auction data',
                'code': 'DATA_ERROR'
            }
    
    @database_sync_to_async
    def create_bid(self, user_id, amount, max_bid=None):
        try:
            user = User.objects.get(id=user_id)
            auction = Auction.objects.select_related('related_property').get(id=self.auction_id)
            
            # Check if auction is active
            if not auction.can_accept_bids():
                return {
                    'success': False, 
                    'message': 'Auction is not currently accepting bids',
                    'code': 'AUCTION_INACTIVE'
                }
            
            # Check minimum bid
            current_bid = auction.current_bid if auction.current_bid else auction.starting_bid
            min_bid = current_bid + auction.minimum_increment
            
            if amount < min_bid:
                return {
                    'success': False, 
                    'message': f'Bid must be at least ${min_bid:,.2f}',
                    'code': 'BID_TOO_LOW',
                    'minimum_bid': float(min_bid)
                }
            
            # Check if user is bidding on their own auction (prevent self-bidding)
            if hasattr(auction, 'created_by') and auction.created_by == user:
                return {
                    'success': False,
                    'message': 'You cannot bid on your own auction',
                    'code': 'SELF_BID_NOT_ALLOWED'
                }
            
            # Get client IP for tracking
            client_ip = None
            if hasattr(self.scope, 'client') and self.scope['client']:
                client_ip = self.scope['client'][0]
            
            # Create the bid
            bid = Bid.objects.create(
                auction=auction,
                bidder=user,
                bid_amount=amount,
                max_bid_amount=max_bid,
                status='pending',
                ip_address=client_ip,
                is_verified=user.is_verified
            )
            
            # Process bid (this will trigger the model's save method which handles bid processing)
            bid.save()
            
            # Refresh auction from database
            auction.refresh_from_db()
            
            return {
                'success': True,
                'bid_data': {
                    'id': bid.id,
                    'amount': float(bid.bid_amount),
                    'bidder_info': {
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}".strip() or user.email,
                        'email': user.email
                    },
                    'bid_time': bid.bid_time.isoformat(),
                    'status': bid.status,
                    'is_verified': bid.is_verified
                }
            }
            
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {
                'success': False, 
                'message': 'User not found',
                'code': 'USER_NOT_FOUND'
            }
        except Auction.DoesNotExist:
            logger.error(f"Auction {self.auction_id} not found")
            return {
                'success': False, 
                'message': 'Auction not found',
                'code': 'AUCTION_NOT_FOUND'
            }
        except Exception as e:
            logger.error(f"Error creating bid: {str(e)}")
            return {
                'success': False, 
                'message': 'Failed to place bid. Please try again.',
                'code': 'BID_ERROR'
            }
    
    @database_sync_to_async
    def join_auction(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            auction = Auction.objects.get(id=self.auction_id)
            
            # Check if auction allows joining
            if auction.status not in ['scheduled', 'live']:
                return {
                    'success': False,
                    'message': 'Auction is not open for registration'
                }
            
            # Check registration deadline
            if auction.registration_deadline and timezone.now() > auction.registration_deadline:
                return {
                    'success': False,
                    'message': 'Registration deadline has passed'
                }
            
            # Here you could implement auction participant tracking
            # For now, just return success
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error joining auction: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to join auction'
            }


    async def handle_extend_auction(self, data):
        """Handle auction extension request"""
        if not hasattr(self.scope, 'user') or isinstance(self.scope['user'], AnonymousUser):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }))
            return
        
        user = self.scope['user']
        extension_hours = data.get('extension_hours', 24)
        reason = data.get('reason', '')
        
        try:
            # Check if user is the auction owner
            auction = await database_sync_to_async(Auction.objects.get)(id=self.auction_id)
            
            if auction.created_by != user and not user.is_staff:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only auction owner can extend auction',
                    'code': 'PERMISSION_DENIED'
                }))
                return
            
            # Extend the auction
            from datetime import timedelta
            new_end_date = auction.end_date + timedelta(hours=extension_hours)
            auction.end_date = new_end_date
            auction.save()
            
            # Notify all connected clients
            await self.channel_layer.group_send(
                self.auction_group_name,
                {
                    'type': 'auction_extended',
                    'auction': await self.get_auction_data(),
                    'extension_hours': extension_hours,
                    'reason': reason
                }
            )
            
            await self.send(text_data=json.dumps({
                'type': 'extension_success',
                'message': f'Auction extended by {extension_hours} hours'
            }))
            
        except Exception as e:
            logger.error(f"Error extending auction: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to extend auction'
            }))

    async def handle_end_auction(self, data):
        """Handle auction completion by owner"""
        if not hasattr(self.scope, 'user') or isinstance(self.scope['user'], AnonymousUser):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }))
            return
        
        user = self.scope['user']
        winning_bid_id = data.get('winning_bid_id')
        notes = data.get('notes', '')
        
        try:
            auction = await database_sync_to_async(Auction.objects.get)(id=self.auction_id)
            
            if auction.created_by != user and not user.is_staff:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Only auction owner can end auction',
                    'code': 'PERMISSION_DENIED'
                }))
                return
            
            # Get the winning bid
            winning_bid = await database_sync_to_async(Bid.objects.get)(
                id=winning_bid_id, 
                auction=auction
            )
            
            # Update auction status
            auction.status = 'completed'
            auction.save()
            
            # Update winning bid status
            winning_bid.status = 'winning'
            winning_bid.save()
            
            # Update other bids to outbid
            await database_sync_to_async(
                Bid.objects.filter(auction=auction).exclude(id=winning_bid_id).update
            )(status='outbid')
            
            # Notify all connected clients
            await self.channel_layer.group_send(
                self.auction_group_name,
                {
                    'type': 'auction_completed',
                    'auction': await self.get_auction_data(),
                    'winning_bid': {
                        'id': winning_bid.id,
                        'amount': float(winning_bid.bid_amount),
                        'bidder_name': winning_bid.bidder.get_full_name() or winning_bid.bidder.email
                    },
                    'notes': notes
                }
            )
            
            await self.send(text_data=json.dumps({
                'type': 'auction_end_success',
                'message': 'Auction completed successfully'
            }))
            
        except Exception as e:
            logger.error(f"Error ending auction: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to end auction'
            }))

    async def auction_extended(self, event):
        """Send auction extension notification"""
        await self.send(text_data=json.dumps({
            'type': 'auction_extended',
            'auction': event['auction'],
            'extension_hours': event['extension_hours'],
            'reason': event.get('reason', ''),
            'message': f"Auction extended by {event['extension_hours']} hours"
        }))

    async def auction_completed(self, event):
        """Send auction completion notification"""
        await self.send(text_data=json.dumps({
            'type': 'auction_completed',
            'auction': event['auction'],
            'winning_bid': event['winning_bid'],
            'notes': event.get('notes', ''),
            'message': f"Auction completed! Winner: {event['winning_bid']['bidder_name']}"
        }))

    