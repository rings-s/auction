# consumers/dashboard_consumer.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from datetime import datetime
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from base.models import Auction, Bid, Transaction, Notification

User = get_user_model()
logger = logging.getLogger(__name__)

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.dashboard_group_name = f'dashboard_{self.user_id}'
        
        # Authenticate
        user = self.scope.get('user')
        if not user or not user.is_authenticated or str(user.id) != self.user_id:
            logger.warning(f"Unauthorized connection attempt to dashboard for user_id: {self.user_id}")
            await self.close(code=4003)  # Custom close code for authentication failure
            return
        
        # Join dashboard group
        await self.channel_layer.group_add(
            self.dashboard_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        try:
            dashboard_data = await self.get_dashboard_data()
            await self.send(text_data=json.dumps({
                'type': 'dashboard_data',
                'data': dashboard_data
            }))
        except Exception as e:
            logger.error(f"Error sending initial dashboard data: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Failed to load dashboard data'
            }))
    
    async def disconnect(self, close_code):
        # Leave dashboard group
        try:
            await self.channel_layer.group_discard(
                self.dashboard_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            
            # Handle ping messages for connection keepalive
            if text_data_json.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
                return
                
            action = text_data_json.get('action')
            
            if action == 'refresh_dashboard':
                # User requested a refresh of dashboard data
                dashboard_data = await self.get_dashboard_data()
                await self.send(text_data=json.dumps({
                    'type': 'dashboard_data',
                    'data': dashboard_data
                }))
                
            elif action == 'get_section':
                # Get specific dashboard section data
                section = text_data_json.get('section')
                if section:
                    section_data = await self.get_section_data(section)
                    await self.send(text_data=json.dumps({
                        'type': 'section_data',
                        'section': section,
                        'data': section_data
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'error': 'Invalid section specified'
                    }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': f'An error occurred: {str(e)}'
            }))
    
    # Event handlers for group messages
    async def dashboard_update(self, event):
        """Handle dashboard update event"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'update_type': event['update_type'],
            'data': event['data']
        }))
    
    async def auction_update(self, event):
        """Handle auction update event that affects dashboard"""
        await self.send(text_data=json.dumps({
            'type': 'auction_update',
            'auction_id': event['auction_id'],
            'update_type': event['update_type'],
            'data': event['data']
        }))
    
    async def bid_update(self, event):
        """Handle bid update event that affects dashboard"""
        await self.send(text_data=json.dumps({
            'type': 'bid_update',
            'auction_id': event['auction_id'],
            'update_type': event['update_type'],
            'data': event['data']
        }))
    
    async def transaction_update(self, event):
        """Handle transaction update event"""
        await self.send(text_data=json.dumps({
            'type': 'transaction_update',
            'transaction_id': event['transaction_id'],
            'update_type': event['update_type'],
            'data': event['data']
        }))
    
    async def notification_event(self, event):
        """Handle notification event that affects dashboard"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    # Database access methods
    @database_sync_to_async
    def get_dashboard_data(self):
        """Get complete dashboard data for the user"""
        try:
            user = User.objects.get(id=self.user_id)
            
            # Active auctions where user is seller
            selling_auctions = Auction.objects.filter(
                seller=user,
                status='ACTIVE'
            ).count()
            
            # Active auctions where user has placed bids
            bidding_auctions = Auction.objects.filter(
                bids__bidder=user,
                status='ACTIVE'
            ).distinct().count()
            
            # Won auctions
            won_auctions = Transaction.objects.filter(
                winner=user
            ).count()
            
            # Sold auctions
            sold_auctions = Transaction.objects.filter(
                auction__seller=user
            ).count()
            
            # Recent auctions (user is seller)
            recent_auctions = self._serialize_auctions(
                Auction.objects.filter(
                    seller=user
                ).order_by('-created_at')[:5]
            )
            
            # Recent bids (user is bidder)
            recent_bids = self._serialize_bids(
                Bid.objects.filter(
                    bidder=user
                ).select_related('auction').order_by('-created_at')[:5]
            )
            
            # Recent transactions (user is buyer or seller)
            recent_transactions = self._serialize_transactions(
                Transaction.objects.filter(
                    Q(winner=user) | Q(auction__seller=user)
                ).select_related('auction', 'winner').order_by('-created_at')[:5]
            )
            
            # Recent notifications
            recent_notifications = self._serialize_notifications(
                Notification.objects.filter(
                    user=user
                ).order_by('-created_at')[:5]
            )
            
            # Total value of bids
            total_bid_value = Bid.objects.filter(
                bidder=user
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Total value of transactions
            total_transaction_value = Transaction.objects.filter(
                winner=user,
                status='COMPLETED'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Compile all dashboard data
            dashboard_data = {
                'statistics': {
                    'selling_auctions': selling_auctions,
                    'bidding_auctions': bidding_auctions,
                    'won_auctions': won_auctions,
                    'sold_auctions': sold_auctions,
                    'total_bid_value': float(total_bid_value),
                    'total_transaction_value': float(total_transaction_value),
                },
                'recent_auctions': recent_auctions,
                'recent_bids': recent_bids,
                'recent_transactions': recent_transactions,
                'recent_notifications': recent_notifications,
                'timestamp': datetime.now().isoformat()
            }
            
            return dashboard_data
        except User.DoesNotExist:
            logger.error(f"User {self.user_id} not found when fetching dashboard data")
            return {
                'error': 'User not found',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {
                'error': f'Failed to load dashboard data: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    @database_sync_to_async
    def get_section_data(self, section):
        """Get data for a specific dashboard section"""
        try:
            user = User.objects.get(id=self.user_id)
            
            if section == 'statistics':
                # Active auctions where user is seller
                selling_auctions = Auction.objects.filter(
                    seller=user,
                    status='ACTIVE'
                ).count()
                
                # Active auctions where user has placed bids
                bidding_auctions = Auction.objects.filter(
                    bids__bidder=user,
                    status='ACTIVE'
                ).distinct().count()
                
                # Won auctions
                won_auctions = Transaction.objects.filter(
                    winner=user
                ).count()
                
                # Sold auctions
                sold_auctions = Transaction.objects.filter(
                    auction__seller=user
                ).count()
                
                return {
                    'selling_auctions': selling_auctions,
                    'bidding_auctions': bidding_auctions,
                    'won_auctions': won_auctions,
                    'sold_auctions': sold_auctions,
                }
                
            elif section == 'recent_auctions':
                return self._serialize_auctions(
                    Auction.objects.filter(
                        seller=user
                    ).order_by('-created_at')[:5]
                )
                
            elif section == 'recent_bids':
                return self._serialize_bids(
                    Bid.objects.filter(
                        bidder=user
                    ).select_related('auction').order_by('-created_at')[:5]
                )
                
            elif section == 'recent_transactions':
                return self._serialize_transactions(
                    Transaction.objects.filter(
                        Q(winner=user) | Q(auction__seller=user)
                    ).select_related('auction', 'winner').order_by('-created_at')[:5]
                )
                
            elif section == 'recent_notifications':
                return self._serialize_notifications(
                    Notification.objects.filter(
                        user=user
                    ).order_by('-created_at')[:5]
                )
                
            else:
                return {
                    'error': f'Unknown section: {section}',
                }
                
        except User.DoesNotExist:
            logger.error(f"User {self.user_id} not found when fetching section data")
            return {'error': 'User not found'}
        except Exception as e:
            logger.error(f"Error getting section data: {str(e)}")
            return {'error': f'Failed to load section data: {str(e)}'}
    
    # Helper methods for serializing models
    def _serialize_auctions(self, auctions):
        """
        Serialize auction objects for dashboard display
        """
        result = []
        for auction in auctions:
            result.append({
                'id': str(auction.id),
                'title': auction.title,
                'current_price': float(auction.current_price),
                'currency': auction.currency,
                'status': auction.status,
                'start_time': auction.start_time.isoformat() if auction.start_time else None,
                'end_time': auction.end_time.isoformat() if auction.end_time else None,
                'created_at': auction.created_at.isoformat(),
                'bids_count': auction.bids.count(),
                'image_url': auction.main_image.url if auction.main_image else None,
            })
        return result
    
    def _serialize_bids(self, bids):
        """
        Serialize bid objects for dashboard display
        """
        result = []
        for bid in bids:
            result.append({
                'id': str(bid.id),
                'auction': str(bid.auction.id),
                'auction_details': {
                    'title': bid.auction.title,
                    'status': bid.auction.status,
                    'end_time': bid.auction.end_time.isoformat() if bid.auction.end_time else None,
                },
                'amount': float(bid.amount),
                'auto_bid_limit': float(bid.auto_bid_limit) if bid.auto_bid_limit else None,
                'status': bid.status,
                'created_at': bid.created_at.isoformat(),
            })
        return result
    
    def _serialize_transactions(self, transactions):
        """
        Serialize transaction objects for dashboard display
        """
        result = []
        for transaction in transactions:
            result.append({
                'id': str(transaction.id),
                'auction': str(transaction.auction.id),
                'auction_details': {
                    'title': transaction.auction.title,
                },
                'winner': str(transaction.winner.id),
                'winner_details': {
                    'first_name': transaction.winner.first_name,
                    'last_name': transaction.winner.last_name,
                },
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'payment_type': transaction.payment_type,
                'status': transaction.status,
                'reference_number': transaction.reference_number,
                'created_at': transaction.created_at.isoformat(),
            })
        return result
    
    def _serialize_notifications(self, notifications):
        """
        Serialize notification objects for dashboard display
        """
        result = []
        for notification in notifications:
            result.append({
                'id': str(notification.id),
                'message': notification.message,
                'notification_type': notification.notification_type,
                'read': notification.read,
                'related_object_id': str(notification.related_object_id) if notification.related_object_id else None,
                'related_object_type': notification.related_object_type,
                'created_at': notification.created_at.isoformat(),
            })
        return result