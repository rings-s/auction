from rest_framework import serializers
from .models import (
    Category, Subcategory, AuctionTimer, Auction, RealEstate, Vehicle,
    Machinery, Factory, HeavyVehicleAuction, Bid, Transaction,
    Document, Contract, ContractTermRevision, Message, PaymentMethod, Notification
)
from accounts.models import CustomUser

import logging

logger = logging.getLogger(__name__)


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for User information.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['email']


class SubcategorySerializer(serializers.ModelSerializer):
    """
    Serializer for auction subcategories.
    """
    # Remove category_details to break circular reference
    class Meta:
        model = Subcategory
        fields = [
            'id', 'category', 'name', 'slug',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for auction categories.
    """
    subcategories = SubcategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'subcategories',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']


class AuctionTimerSerializer(serializers.ModelSerializer):
    """
    Serializer for auction timers.
    """
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = AuctionTimer
        fields = [
            'id', 'auction', 'duration', 'custom_duration',
            'start_time', 'end_time', 'is_extended', 'extension_count',
            'last_extension', 'auto_extend', 'extension_threshold',
            'extension_duration', 'remaining_time',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at', 'remaining_time']
    
    def get_remaining_time(self, obj):
        """
        Get the remaining time for this auction.
        """
        return obj.get_remaining_time()
    
    def validate(self, data):
        """
        Validate that end time is after start time and check for
        custom duration when needed.
        """
        if 'end_time' in data and 'start_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError(
                    "End time must be after start time."
                )
                
        if data.get('duration') == 'CUSTOM' and not data.get('custom_duration'):
            raise serializers.ValidationError(
                "Custom duration is required for custom timer."
            )
            
        return data

class BidSerializer(serializers.ModelSerializer):
    """
    Serializer for bids.
    """
    bidder_details = CustomUserSerializer(source='bidder', read_only=True)
    
    class Meta:
        model = Bid
        fields = [
            'id', 'auction', 'bidder', 'bidder_details', 'amount',
            'auto_bid_limit', 'status', 'ip_address',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at', 'ip_address']
    
    def validate(self, data):
        """
        Validate that bid amount is greater than current price.
        """
        amount = data.get('amount')
        auction = data.get('auction')
        
        # Handle case where auction might be an ID (UUID) or an Auction object
        if amount and auction:
            if not isinstance(auction, Auction):
                # If auction is an ID, fetch the Auction object
                try:
                    auction = Auction.objects.get(id=auction)
                except Auction.DoesNotExist:
                    raise serializers.ValidationError("Invalid auction ID.")
            
            # Now validate amount against auction's current price
            if amount <= auction.current_price:
                raise serializers.ValidationError(
                    "Bid amount must be greater than current price."
                )
                
        # Validate auto_bid_limit if provided
        if 'auto_bid_limit' in data and amount:
            if data['auto_bid_limit'] < amount:
                raise serializers.ValidationError(
                    "Auto bid limit cannot be less than the bid amount."
                )
                
        return data
    
    def create(self, validated_data):
        """
        Create a new bid and capture the client IP address.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'META'):
            validated_data['ip_address'] = self._get_client_ip(request)
        return super().create(validated_data)
    
    def _get_client_ip(self, request):
        """
        Extract the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuctionSerializer(serializers.ModelSerializer):
    """
    Serializer for auctions.
    """
    category_details = serializers.SerializerMethodField()
    subcategory_details = serializers.SerializerMethodField()
    seller_details = serializers.SerializerMethodField()
    timer_details = AuctionTimerSerializer(source='timer', read_only=True)
    current_highest_bid = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    specific_data = serializers.SerializerMethodField()
    # Add these fields for image handling
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = [
            'id', 'category', 'category_details', 'subcategory', 'subcategory_details',
            'title', 'description', 'seller', 'seller_details',
            'start_time', 'end_time', 'current_price',
            'reserve_price', 'minimum_bid_increment',
            'status', 'currency', 'main_image', 'image_1', 'image_2',
            'image_3', 'image_4', 'image_5', 'timer_details',
            'current_highest_bid', 'total_bids', 'specific_data',
            'created_at', 'modified_at',
            # Add new fields to fields list
            'image_url', 'images'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

    def get_category_details(self, obj):
        logger.debug(f"Serializing category_details for auction {obj.id}")
        return {
            'id': obj.category.id,
            'name': obj.category.name,
            'slug': obj.category.slug
        }

    def get_subcategory_details(self, obj):
        logger.debug(f"Serializing subcategory_details for auction {obj.id}")
        if obj.subcategory:
            return {
                'id': obj.subcategory.id,
                'name': obj.subcategory.name,
                'slug': obj.subcategory.slug
            }
        return None

    def get_seller_details(self, obj):
        logger.debug(f"Serializing seller_details for auction {obj.id}")
        return {
            'id': obj.seller.id,
            'email': obj.seller.email,
            'first_name': obj.seller.first_name,
            'last_name': obj.seller.last_name
        }

    def get_current_highest_bid(self, obj):
        logger.debug(f"Serializing current_highest_bid for auction {obj.id}")
        highest_bid = obj.bids.order_by('-amount').first()
        if highest_bid:
            return {
                'id': str(highest_bid.id),
                'amount': float(highest_bid.amount),
                'bidder_id': highest_bid.bidder.id,
                'created_at': highest_bid.created_at.isoformat()
            }
        return None

    def get_total_bids(self, obj):
        logger.debug(f"Serializing total_bids for auction {obj.id}")
        return obj.bids.count()

    def get_specific_data(self, obj):
        logger.debug(f"Serializing specific_data for auction {obj.id}")
        auction_types = {
            'real_estate': {'model': RealEstate, 'serializer': RealEstateSerializer},
            'vehicle': {'model': Vehicle, 'serializer': VehicleSerializer},
            'machinery': {'model': Machinery, 'serializer': MachinerySerializer},
            'factory': {'model': Factory, 'serializer': FactorySerializer},
            'heavy_vehicle': {'model': HeavyVehicleAuction, 'serializer': HeavyVehicleAuctionSerializer},
        }

        for type_name, type_data in auction_types.items():
            try:
                if type_name in ['machinery', 'heavy_vehicle']:
                    instance = type_data['model'].objects.filter(auction=obj).first()
                else:
                    instance = type_data['model'].objects.get(auction=obj)

                if instance:
                    logger.debug(f"Found {type_name} instance for auction {obj.id}")
                    serializer = type_data['serializer'](instance, context=self.context)
                    specific_data = {
                        key: value for key, value in serializer.data.items()
                        if key != 'auction_details'
                    }
                    return {
                        'auction_type': type_name,
                        'data': specific_data
                    }
            except type_data['model'].DoesNotExist:
                continue
        
        logger.debug(f"No specific data found for auction {obj.id}")
        return None

    def validate(self, data):
        logger.debug("Validating auction data")
        if 'end_time' in data and 'start_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("End time must be after start time.")
        if 'current_price' in data and data['current_price'] < 0:
            raise serializers.ValidationError("Current price cannot be negative.")
        if 'reserve_price' in data and data['reserve_price'] < 0:
            raise serializers.ValidationError("Reserve price cannot be negative.")
        return data

    # New methods for image handling
    def get_image_url(self, obj):
        """
        Get the main image URL for the auction.
        """
        request = self.context.get('request')
        
        # Try main_image first
        if obj.main_image and hasattr(obj.main_image, 'url'):
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        
        # If no main image, try image_1 through image_5
        for i in range(1, 6):
            image_field = getattr(obj, f'image_{i}', None)
            if image_field and hasattr(image_field, 'url'):
                if request:
                    return request.build_absolute_uri(image_field.url)
                return image_field.url
                
        return None

    def get_images(self, obj):
        """
        Get all image URLs for the auction.
        """
        request = self.context.get('request')
        images = []
        
        # Add main image first if it exists
        if obj.main_image and hasattr(obj.main_image, 'url'):
            main_image_url = request.build_absolute_uri(obj.main_image.url) if request else obj.main_image.url
            images.append(main_image_url)
        
        # Add additional images
        for i in range(1, 6):
            image_field = getattr(obj, f'image_{i}', None)
            if image_field and hasattr(image_field, 'url'):
                image_url = request.build_absolute_uri(image_field.url) if request else image_field.url
                images.append(image_url)
        
        return images

class RealEstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstate
        fields = [
            'id', 'auction', 'property_type', 'size_sqm', 'location', 'address',
            'bedrooms', 'bathrooms', 'year_built', 'zoning_info', 'legal_description',
            'property_condition', 'historical_value', 'property_image_1', 'property_image_2',
            'property_image_3', 'property_image_4', 'property_image_5', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('auction_details', None)
        return data

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'id', 'auction', 'make', 'model', 'year', 'mileage', 'condition', 'vin',
            'engine_type', 'transmission', 'fuel_type', 'color', 'registration_number',
            'service_history', 'vehicle_image_1', 'vehicle_image_2', 'vehicle_image_3',
            'vehicle_image_4', 'vehicle_image_5', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

    def validate_vin(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.vin == value:
            return value
        if Vehicle.objects.filter(vin=value).exists():
            raise serializers.ValidationError("This VIN is already in use.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('auction_details', None)
        return data

class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = [
            'id', 'auction', 'total_area_sqm', 'built_up_area_sqm', 'location', 'address',
            'production_capacity', 'power_capacity', 'water_supply', 'waste_management',
            'environmental_certificates', 'infrastructure_details', 'utility_connections',
            'factory_image_1', 'factory_image_2', 'factory_image_3', 'factory_image_4',
            'factory_image_5', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('auction_details', None)
        return data

class HeavyVehicleAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeavyVehicleAuction
        fields = [
            'id', 'auction', 'vehicle_type', 'make', 'model', 'year', 'load_capacity',
            'operating_hours', 'engine_power', 'registration_number', 'compliance_certificates',
            'maintenance_history', 'heavy_vehicle_image_1', 'heavy_vehicle_image_2',
            'heavy_vehicle_image_3', 'heavy_vehicle_image_4', 'heavy_vehicle_image_5',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('auction_details', None)
        return data
    
    
    
class MachinerySerializer(serializers.ModelSerializer):
    """
    Serializer for machinery auctions.
    """
    class Meta:
        model = Machinery
        fields = [
            'id', 'auction', 'machine_type', 'manufacturer', 'model_number',
            'year_manufactured', 'operating_hours', 'power_requirements',
            'dimensions', 'weight', 'capacity', 'maintenance_history',
            'safety_certificates', 'technical_specifications',
            'machinery_image_1', 'machinery_image_2', 'machinery_image_3',
            'machinery_image_4', 'machinery_image_5',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Explicitly remove auction_details if it’s being added elsewhere
        data.pop('auction_details', None)
        return data
    
    
  


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for auction transactions.
    """
    auction_details = AuctionSerializer(source='auction', read_only=True)
    winner_details = CustomUserSerializer(source='winner', read_only=True)
    escrow_agent_details = CustomUserSerializer(source='escrow_agent', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'auction', 'auction_details', 'winner', 'winner_details',
            'winning_bid', 'amount', 'currency', 'payment_type',
            'payment_method', 'status', 'reference_number',
            'payment_proof', 'payment_date', 'stripe_payment_id',
            'paypal_transaction_id', 'escrow_agent', 'escrow_agent_details',
            'notes', 'metadata', 'created_at', 'modified_at'
        ]
        read_only_fields = [
            'id', 'reference_number', 'created_at', 'modified_at'
        ]
    
    def validate(self, data):
        """
        Validate transaction data.
        """
        if 'amount' in data and data['amount'] <= 0:
            raise serializers.ValidationError(
                "Transaction amount must be greater than zero."
            )
            
        if data.get('payment_method') == 'ESCROW' and not data.get('escrow_agent'):
            raise serializers.ValidationError(
                "Escrow agent is required for escrow payments."
            )
            
        return data


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for auction documents.
    """
    uploaded_by_details = CustomUserSerializer(source='uploaded_by', read_only=True)
    verified_by_details = CustomUserSerializer(source='verified_by', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'auction', 'document_type', 'title', 'file',
            'description', 'uploaded_by', 'uploaded_by_details',
            'verification_status', 'verified_by', 'verified_by_details',
            'typed_signature', 'signer_role', 'metadata',
            'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class ContractSerializer(serializers.ModelSerializer):
    """
    Serializer for auction contracts.
    """
    seller_details = CustomUserSerializer(source='seller', read_only=True)
    buyer_details = CustomUserSerializer(source='buyer', read_only=True)
    seller_legal_rep_details = CustomUserSerializer(
        source='seller_legal_rep', read_only=True
    )
    buyer_legal_rep_details = CustomUserSerializer(
        source='buyer_legal_rep', read_only=True
    )
    reviewed_by_details = CustomUserSerializer(source='reviewed_by', read_only=True)
    signatures = serializers.SerializerMethodField()
    current_terms = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'auction', 'seller', 'seller_details',
            'buyer', 'buyer_details', 'contract_type', 'status',
            'contract_value', 'deposit_amount', 'start_date',
            'end_date', 'contract_number', 'seller_legal_rep',
            'seller_legal_rep_details', 'buyer_legal_rep',
            'buyer_legal_rep_details', 'seller_signature_date',
            'buyer_signature_date', 'reviewed_by', 'reviewed_by_details',
            'review_date', 'review_notes', 'signatures', 'current_terms',
            'created_at', 'modified_at'
        ]
        read_only_fields = [
            'id', 'contract_number', 'created_at', 'modified_at',
            'signatures', 'current_terms'
        ]
    
    def get_signatures(self, obj):
        """
        Get signatures for this contract.
        """
        return DocumentSerializer(
            obj.get_signatures(),
            many=True,
            context=self.context
        ).data
    
    def get_current_terms(self, obj):
        """
        Get current terms for all term types.
        """
        term_types = [choice[0] for choice in ContractTermRevision.TERM_TYPE_CHOICES]
        result = {}
        
        for term_type in term_types:
            terms = obj.get_current_terms(term_type)
            if terms:
                result[term_type] = ContractTermRevisionSerializer(terms).data
                
        return result
    
    def validate(self, data):
        """
        Validate contract data.
        """
        if 'end_date' in data and 'start_date' in data:
            if data['end_date'] and data['start_date'] > data['end_date']:
                raise serializers.ValidationError(
                    "End date must be after start date."
                )
                
        if 'deposit_amount' in data and 'contract_value' in data:
            if data['deposit_amount'] > data['contract_value']:
                raise serializers.ValidationError(
                    "Deposit amount cannot be greater than contract value."
                )
                
        return data


class ContractTermRevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for contract term revisions.
    """
    revised_by_details = CustomUserSerializer(source='revised_by', read_only=True)
    approved_by_details = CustomUserSerializer(source='approved_by', read_only=True)
    
    class Meta:
        model = ContractTermRevision
        fields = [
            'id', 'contract', 'terms_type', 'terms_content',
            'previous_terms', 'revision_reason', 'revised_by',
            'revised_by_details', 'approved_by', 'approved_by_details',
            'approval_date', 'version_number', 'is_current_version',
            'created_at', 'modified_at'
        ]
        read_only_fields = [
            'id', 'version_number', 'created_at', 'modified_at'
        ]


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages.
    """
    sender_details = CustomUserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_details', 'room_id',
            'content', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for user payment methods.
    """
    user_details = CustomUserSerializer(source='user', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'user', 'user_details', 'method_type', 
            'details', 'created_at', 'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']
        extra_kwargs = {
            'details': {'write_only': True}  # Payment details should be write-only for security
        }
    
    def validate(self, data):
        """
        Validate payment method data.
        """
        if data.get('method_type') == 'CREDIT_CARD':
            details = data.get('details', {})
            
            # Make sure we don't store complete card details for security
            if 'card_number' in details:
                # Only store last 4 digits
                details['last4'] = details['card_number'][-4:]
                details.pop('card_number')
                
            # Remove CVV entirely
            if 'cvv' in details:
                details.pop('cvv')
                
            data['details'] = details
            
        return data


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for user notifications.
    """
    user_details = CustomUserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_details', 'message', 'notification_type',
            'read', 'displayed', 'related_object_id', 'related_object_type',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']