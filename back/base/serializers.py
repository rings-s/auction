# back/base/serializers.py
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import *

import json, logging
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, Sum, Avg, Max

# Set up proper logging instead of print statements
logger = logging.getLogger(__name__)

User = get_user_model()

class LocationSerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_coordinates(self, obj):
        return obj.coordinates

    def validate(self, attrs):
        latitude, longitude = attrs.get('latitude'), attrs.get('longitude')
        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise serializers.ValidationError(_("Both latitude and longitude must be provided together."))
        return attrs


class MediaSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    content_type_str = serializers.CharField(write_only=True, required=False)
    content_type_model = serializers.CharField(source='content_type.model', read_only=True)
    content_type_app_label = serializers.CharField(source='content_type.app_label', read_only=True)

    class Meta:
        model = Media
        fields = ['id', 'file', 'url', 'name', 'media_type', 'is_primary', 'order', 
                 'content_type', 'content_type_str', 'content_type_model', 'content_type_app_label',
                 'object_id', 'file_size', 'dimensions', 'created_at', 'updated_at']
        read_only_fields = ['file_size', 'dimensions', 'created_at', 'updated_at', 
                           'content_type_model', 'content_type_app_label']
        extra_kwargs = {
            'content_type': {'required': False},
            'file': {'required': True}
        }

    def get_url(self, obj):
        """Get full URL for the file, including domain if request is available"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_size(self, obj):
        """Get file size in bytes with safe error handling"""
        try:
            if hasattr(obj, 'file') and obj.file:
                # First check if file exists
                if hasattr(obj.file, 'path'):
                    import os
                    if os.path.exists(obj.file.path):
                        return obj.file_size if hasattr(obj, 'file_size') else 0
                    else:
                        logger.warning(f"File not found for media {obj.id}: {obj.file.path}")
                        return 0
                # Fallback for non-filesystem storage
                return obj.file_size if hasattr(obj, 'file_size') else 0
            return 0
        except Exception as e:
            logger.warning(f"Could not get file size for media {obj.id}: {str(e)}")
            return 0

    def get_dimensions(self, obj):
        """Get image dimensions if media is an image"""
        return obj.get_dimensions() if hasattr(obj, 'get_dimensions') else None

    def validate(self, data):
        """Validate the media data including content type resolution"""
        # Handle content_type_str to ContentType conversion
        content_type_str = data.pop('content_type_str', None)
        
        # If content_type is not directly provided, try to resolve from content_type_str
        if not data.get('content_type') and content_type_str:
            try:
                # Parse content_type_str - accept both 'app_label.model' and just 'model' formats
                if '.' in content_type_str:
                    app_label, model = content_type_str.lower().split('.')
                else:
                    # Default to 'base' app if not specified
                    app_label, model = 'base', content_type_str.lower()
                
                # Log for debugging in development only
                logger.debug(f"Looking for content type with app_label='{app_label}', model='{model}'")
                
                try:
                    content_type = ContentType.objects.get(app_label=app_label, model=model)
                    data['content_type'] = content_type
                    logger.debug(f"Found content type: {content_type.app_label}.{content_type.model} (id={content_type.id})")
                except ContentType.DoesNotExist:
                    # List available content types to help debugging
                    available = list(ContentType.objects.filter(app_label=app_label).values_list('model', flat=True))
                    msg = f"Content type '{app_label}.{model}' not found. Available models in '{app_label}': {available}"
                    logger.error(msg)
                    raise serializers.ValidationError({"content_type_str": msg})
                
            except Exception as e:
                # Provide detailed error for debugging
                logger.error(f"Error resolving content_type_str '{content_type_str}': {str(e)}")
                raise serializers.ValidationError({
                    "content_type_str": f"Invalid content type format: {content_type_str}. "
                                    f"Use format 'app_label.model' or just 'model'. Error: {str(e)}"
                })
        
        # Ensure both content_type and object_id are present
        if 'content_type' not in data and self.instance is None:
            raise serializers.ValidationError({
                "content_type": "Content type is required. Provide either content_type or content_type_str."
            })
            
        if 'object_id' not in data and self.instance is None:
            raise serializers.ValidationError({"object_id": "Object ID is required."})
            
        # Validate file is present for new uploads
        if 'file' not in data and self.instance is None:
            raise serializers.ValidationError({"file": "File is required for new media uploads."})
            
        # Validate and set media_type based on file
        if 'file' in data:
            file = data['file']
            
            # If media_type is explicitly set, use it
            if 'media_type' in data:
                logger.debug(f"Using explicitly provided media_type: {data['media_type']}")
            # Otherwise detect from file
            else:
                if hasattr(file, 'content_type'):
                    if file.content_type.startswith('image/'):
                        data['media_type'] = 'image'
                    elif file.content_type.startswith('video/'):
                        data['media_type'] = 'video'
                    elif file.content_type == 'application/pdf' or str(file.name).lower().endswith('.pdf'):
                        data['media_type'] = 'document'
                        logger.debug(f"Setting media_type to 'document' for PDF file: {file.name}")
                    else:
                        data['media_type'] = 'other'
                        
                # Fallback to extension detection
                elif hasattr(file, 'name'):
                    filename = str(file.name).lower()
                    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        data['media_type'] = 'image'
                    elif filename.endswith('.pdf'):
                        data['media_type'] = 'document'
                        logger.debug(f"Setting media_type to 'document' based on filename: {filename}")
                    elif filename.endswith(('.mp4', '.avi', '.mov')):
                        data['media_type'] = 'video'
                    else:
                        data['media_type'] = 'other'
                
                logger.debug(f"Detected media_type: {data['media_type']} for file: {file.name}")
        
        return data

    def create(self, validated_data):
        """Create a new media instance with proper error handling"""
        try:
            logger.debug(f"Creating media with validated data: media_type={validated_data.get('media_type')}, file={validated_data.get('file').name if 'file' in validated_data else None}")
            
            # Check that content_type and object_id point to a valid object
            content_type = validated_data.get('content_type')
            object_id = validated_data.get('object_id')
            
            if content_type and object_id:
                # Try to get the related object to verify it exists
                model_class = content_type.model_class()
                if model_class:
                    try:
                        related_object = model_class.objects.get(pk=object_id)
                        logger.debug(f"Found related object: {related_object}")
                    except model_class.DoesNotExist:
                        logger.error(f"Related object {content_type.model} with id={object_id} not found")
                        raise serializers.ValidationError({
                            "object_id": f"Object with id={object_id} of type {content_type.app_label}.{content_type.model} does not exist."
                        })
            
            # Remove 'owner' from validated_data if present, as Media model doesn't have it
            validated_data.pop('owner', None)

            # Proceed with creation
            instance = super().create(validated_data)
            logger.info(f"Media created successfully: id={instance.id}, media_type={instance.media_type}")
            
            return instance
            
        except Exception as e:
            logger.error(f"Error creating media: {str(e)}", exc_info=True)
            raise

# Continue with the rest of the serializers without print statements...
class RoomSerializer(serializers.ModelSerializer):
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
    def get_media(self, obj):
        media_items = Media.objects.filter(content_type__model='room', object_id=obj.id)
        return MediaSerializer(media_items, many=True, context=self.context).data

class PropertySerializer(serializers.ModelSerializer):
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    building_type_display = serializers.CharField(source='get_building_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    location = LocationSerializer(read_only=True)
    location_data = serializers.JSONField(write_only=True, required=False)
    rooms = RoomSerializer(many=True, read_only=True)
    media = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['property_number', 'slug', 'owner', 'is_verified', 'view_count', 'created_at', 'updated_at']

    def get_media(self, obj):
        media_items = Media.objects.filter(content_type__model='property', object_id=obj.id)
        return MediaSerializer(media_items, many=True, context=self.context).data

    def get_main_image(self, obj):
        image = obj.get_main_image()
        return MediaSerializer(image, context=self.context).data if image else None

    def validate(self, data):
        if self.context.get('request') and self.context['request'].method in ['POST', 'PUT']:
            if 'location_data' not in data and not self.instance:
                raise serializers.ValidationError({"location_data": _("Location is required for new properties.")})
        return data

    @transaction.atomic
    def create(self, validated_data):
        location_data = validated_data.pop('location_data', None)
        
        if location_data:
            if isinstance(location_data, str):
                location_data = json.loads(location_data)
            
            location = Location.objects.filter(
                city=location_data['city'], 
                state=location_data['state'],
                country=location_data.get('country', 'المملكة العربية السعودية')
            ).first()
            
            if not location:
                location = Location.objects.create(**location_data)
            
            validated_data['location'] = location

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        
        return super().create(validated_data)

class BidSerializer(serializers.ModelSerializer):
    bidder_info = serializers.SerializerMethodField()
    user_display_name = serializers.SerializerMethodField()  # Add this field
    auction_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Bid
        fields = [
            'id', 'auction', 'bid_amount', 'max_bid_amount', 'bid_time', 'status', 'status_display',
            'notes', 'ip_address', 'is_verified', 'bidder_info', 'user_display_name', 'auction_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['bidder', 'bid_time', 'status', 'ip_address', 'is_verified', 'created_at', 'updated_at']

    def get_bidder_info(self, obj):
        """Return comprehensive bidder information"""
        if not obj.bidder:
            return None
        
        user = obj.bidder
        
        # Get the display name safely
        display_name = self.get_safe_display_name(user)
        
        return {
            'id': user.id,
            'username': getattr(user, 'username', None),
            'name': display_name,
            'first_name': getattr(user, 'first_name', ''),
            'last_name': getattr(user, 'last_name', ''),
            'email': getattr(user, 'email', ''),
            'is_verified': getattr(user, 'is_verified', False)
        }
    
    def get_user_display_name(self, obj):
        """Return a safe display name for the user"""
        if not obj.bidder:
            return "Anonymous Bidder"
        
        return self.get_safe_display_name(obj.bidder)
    
    def get_safe_display_name(self, user):
        """Helper method to safely get a display name"""
        if not user:
            return "Anonymous Bidder"
        
        # Try different name combinations
        first_name = getattr(user, 'first_name', '') or ''
        last_name = getattr(user, 'last_name', '') or ''
        username = getattr(user, 'username', '') or ''
        email = getattr(user, 'email', '') or ''
        
        # Combine first and last name
        full_name = f"{first_name} {last_name}".strip()
        if full_name:
            return full_name
        
        # Use username if available
        if username:
            return username
        
        # Use email prefix as fallback
        if email and '@' in email:
            return email.split('@')[0]
        
        # Final fallback
        return f"User {user.id}" if hasattr(user, 'id') else "Anonymous Bidder"

    def get_auction_info(self, obj):
        if not obj.auction:
            return None
        return {
            'id': obj.auction.id,
            'title': obj.auction.title,
            'current_bid': float(obj.auction.current_bid) if obj.auction.current_bid else None,
            'status': obj.auction.status
        }

    def validate_bid_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be positive")
        return value

        
class AuctionSerializer(serializers.ModelSerializer):
    auction_type_display = serializers.CharField(source='get_auction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    related_property = PropertySerializer(read_only=True)
    related_property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(), source='related_property', write_only=True
    )
    
    bids = BidSerializer(many=True, read_only=True)
    media = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'slug', 'auction_type', 'auction_type_display', 'status', 'status_display',
            'description', 'start_date', 'end_date', 'registration_deadline', 'related_property', 
            'related_property_id', 'starting_bid', 'current_bid', 'minimum_increment',
            'minimum_participants', 'auto_extend_minutes', 'is_published', 'is_featured', 
            'view_count', 'media', 'bids', 'time_remaining', 'is_active', 'bid_count', 'created_at'
        ]
        read_only_fields = ['slug', 'current_bid', 'bid_count', 'view_count', 'created_at', 'updated_at']

    def get_media(self, obj):
        media_items = Media.objects.filter(content_type__model='auction', object_id=obj.id)
        return MediaSerializer(media_items, many=True, context=self.context).data

    def get_time_remaining(self, obj):
        return obj.time_remaining

    def get_is_active(self, obj):
        return obj.is_active()

    def validate(self, data):
        start_date, end_date = data.get('start_date'), data.get('end_date')
        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": _("End date must be after start date.")})
        return data

class MessageSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()
    recipient_info = serializers.SerializerMethodField()
    property_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    recipient_email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = Message
        fields = [
            'id', 'subject', 'body', 'status', 'status_display', 'priority', 'priority_display', 
            'sender_info', 'recipient_info', 'property_info', 'thread_id', 'parent_message',
            'is_read', 'created_at', 'read_at', 'replied_at',
            'recipient_email', 'sender', 'recipient', 'related_property'
        ]
        read_only_fields = [
            'id', 'sender_info', 'recipient_info', 'property_info', 
            'status_display', 'priority_display', 'thread_id', 
            'is_read', 'created_at', 'read_at', 'replied_at',
            'sender' # Sender is set by the view
        ]
        extra_kwargs = {
            'recipient': {'required': False, 'allow_null': True}, # Will be set from recipient_email
            'parent_message': {'required': False, 'allow_null': True},
            'related_property': {'required': False, 'allow_null': True},
            'status': {'required': False}, # Has default
            'priority': {'required': False}, # Has default
            'subject': {'required': True},
            'body': {'required': True},
        }

    def get_sender_info(self, obj):
        if not obj.sender:
            return None
        return {
            'id': obj.sender.id,
            'name': f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.email,
            'email': obj.sender.email
        }

    def get_recipient_info(self, obj):
        if not obj.recipient:
            return None
        return {
            'id': obj.recipient.id,
            'name': f"{obj.recipient.first_name} {obj.recipient.last_name}".strip() or obj.recipient.email,
            'email': obj.recipient.email
        }

    def get_property_info(self, obj):
        if not obj.related_property:
            return None
        return {
            'id': obj.related_property.id,
            'title': obj.related_property.title,
            'slug': obj.related_property.slug,
            'market_value': float(obj.related_property.market_value) if obj.related_property.market_value else None
        }

    def create(self, validated_data):
        recipient_email_str = validated_data.pop('recipient_email', None)
        
        if not recipient_email_str:
            raise serializers.ValidationError({'recipient_email': _('Recipient email is required for a new message.')})
        
        try:
            recipient_user = User.objects.get(email__iexact=recipient_email_str)
            validated_data['recipient'] = recipient_user
        except User.DoesNotExist:
            raise serializers.ValidationError({'recipient_email': _('User with this email does not exist.')})
        except User.MultipleObjectsReturned:
            raise serializers.ValidationError({'recipient_email': _('Multiple users found with this email. Please contact support.')})

        return super().create(validated_data)

class MessageReplySerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'body', 'sender_info', 'created_at', 'parent_message']
        read_only_fields = ['sender_info', 'created_at']

    def get_sender_info(self, obj):
        return {
            'id': obj.sender.id,
            'name': f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.email,
        }

    def validate(self, data):
        parent_message = data.get('parent_message')
        if parent_message:
            data['subject'] = f"Re: {parent_message.subject}"
            data['recipient'] = parent_message.sender
            data['related_property'] = parent_message.related_property
            data['thread_id'] = parent_message.thread_id
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
        
        parent_message = validated_data.get('parent_message')
        if parent_message:
            parent_message.mark_as_replied()
        
        return super().create(validated_data)





class DashboardMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetrics
        fields = '__all__'
        read_only_fields = ['user', 'last_updated']

# PropertyDashboardSerializer moved to dashboard serializers section below

class AuctionDashboardSerializer(serializers.ModelSerializer):
    """Simplified auction serializer for dashboard"""
    property_title = serializers.CharField(source='related_property.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    auction_type_display = serializers.CharField(source='get_auction_type_display', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    days_until_start = serializers.SerializerMethodField()
    
    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'slug', 'auction_type', 'auction_type_display', 'status', 'status_display',
            'start_date', 'end_date', 'starting_bid', 'current_bid', 'bid_count',
            'property_title', 'is_published', 'is_featured', 'view_count',
            'time_remaining', 'is_active', 'days_until_start', 'created_at'
        ]
        
    def get_time_remaining(self, obj):
        return obj.time_remaining
        
    def get_is_active(self, obj):
        return obj.is_active()
        
    def get_days_until_start(self, obj):
        if obj.start_date and obj.start_date > timezone.now():
            return (obj.start_date - timezone.now()).days
        return 0

class BidDashboardSerializer(serializers.ModelSerializer):
    """Simplified bid serializer for dashboard"""
    auction_title = serializers.CharField(source='auction.title', read_only=True)
    property_title = serializers.CharField(source='auction.related_property.title', read_only=True)
    bidder_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_winning = serializers.SerializerMethodField()
    
    class Meta:
        model = Bid
        fields = [
            'id', 'auction', 'auction_title', 'property_title', 'bid_amount',
            'max_bid_amount', 'status', 'status_display', 'bid_time', 'bidder_name',
            'is_verified', 'is_winning', 'created_at'
        ]
        
    def get_bidder_name(self, obj):
        return obj.bidder_name
        
    def get_is_winning(self, obj):
        return obj.status == 'winning'

class UserDashboardStatsSerializer(serializers.Serializer):
    """User-specific dashboard statistics"""
    user_priority = serializers.IntegerField()
    user_role = serializers.CharField()
    user_role_display = serializers.CharField()
    
    # Property stats
    total_properties = serializers.IntegerField()
    published_properties = serializers.IntegerField()
    draft_properties = serializers.IntegerField()
    featured_properties = serializers.IntegerField()
    verified_properties = serializers.IntegerField()
    properties_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Auction stats
    total_auctions = serializers.IntegerField()
    active_auctions = serializers.IntegerField()
    scheduled_auctions = serializers.IntegerField()
    ended_auctions = serializers.IntegerField()
    
    # Bid stats
    total_bids = serializers.IntegerField()
    winning_bids = serializers.IntegerField()
    total_bid_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Activity stats
    recent_properties = serializers.IntegerField()
    recent_auctions = serializers.IntegerField()
    recent_bids = serializers.IntegerField()
    messages_unread = serializers.IntegerField()
    
    # Performance metrics (for appraisers/data_entry)
    properties_this_month = serializers.IntegerField(required=False)
    auctions_this_month = serializers.IntegerField(required=False)
    avg_property_value = serializers.DecimalField(max_digits=20, decimal_places=2, required=False)

class SystemDashboardStatsSerializer(serializers.Serializer):
    """System-wide dashboard statistics for admins/appraisers"""
    
    # Overall system stats
    total_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    
    # Property stats
    total_properties = serializers.IntegerField()
    published_properties = serializers.IntegerField()
    properties_this_month = serializers.IntegerField()
    avg_property_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    highest_property_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Auction stats
    total_auctions = serializers.IntegerField()
    active_auctions = serializers.IntegerField()
    completed_auctions = serializers.IntegerField()
    total_auction_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Bid stats
    total_bids = serializers.IntegerField()
    unique_bidders = serializers.IntegerField()
    total_bid_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    avg_bid_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Activity stats
    bids_today = serializers.IntegerField()
    auctions_ending_soon = serializers.IntegerField()
    pending_verifications = serializers.IntegerField()
    
    # Geographic stats
    top_cities = serializers.ListField(child=serializers.DictField())
    
class RecentActivitySerializer(serializers.Serializer):
    """Recent activity feed for dashboard"""
    activity_type = serializers.CharField()  # 'property', 'auction', 'bid', 'message'
    title = serializers.CharField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()
    related_id = serializers.IntegerField()
    related_slug = serializers.CharField(required=False)
    priority = serializers.CharField()  # 'low', 'medium', 'high', 'urgent'
    user_name = serializers.CharField(required=False)


# -------------------------------------------------------------------------
# Property Management Serializers
# -------------------------------------------------------------------------

class RentalPropertySerializer(serializers.ModelSerializer):
    """Serializer for rental property management"""
    property_details = PropertySerializer(source='property', read_only=True)
    current_tenant = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()
    annual_income = serializers.SerializerMethodField()
    is_occupied = serializers.SerializerMethodField()
    
    class Meta:
        model = RentalProperty
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_rental_income']
        
    def get_current_tenant(self, obj):
        tenant = obj.current_tenant
        if tenant:
            return {
                'id': tenant.id,
                'full_name': tenant.full_name,
                'email': tenant.email,
                'phone': tenant.phone,
            }
        return None
        
    def get_occupancy_rate(self, obj):
        return round(obj.occupancy_rate, 2)
        
    def get_annual_income(self, obj):
        return obj.calculate_annual_income()
        
    def get_is_occupied(self, obj):
        return obj.is_occupied

    def validate(self, attrs):
        """Validate rental property data"""
        # Ensure monthly rent is reasonable
        monthly_rent = attrs.get('monthly_rent', 0)
        if monthly_rent <= 0:
            raise serializers.ValidationError("Monthly rent must be greater than zero")
            
        # Validate lease periods
        min_period = attrs.get('minimum_lease_period', 0)
        max_period = attrs.get('maximum_lease_period', 0)
        if min_period > max_period:
            raise serializers.ValidationError("Minimum lease period cannot be greater than maximum lease period")
            
        return attrs


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for tenant management"""
    full_name = serializers.SerializerMethodField()
    current_property = serializers.SerializerMethodField()
    current_lease = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'national_id': {'write_only': True},
            'bank_account_info': {'write_only': True},
        }
        
    def get_full_name(self, obj):
        return obj.full_name
        
    def get_current_property(self, obj):
        current_property = obj.current_property
        if current_property:
            return {
                'id': current_property.property.id,
                'title': current_property.property.title,
                'address': current_property.property.address,
            }
        return None
        
    def get_current_lease(self, obj):
        lease = obj.current_lease
        if lease:
            return {
                'id': lease.id,
                'lease_number': lease.lease_number,
                'start_date': lease.start_date,
                'end_date': lease.end_date,
                'monthly_rent': lease.monthly_rent,
                'status': lease.status,
            }
        return None

    def validate_email(self, value):
        """Ensure email is unique"""
        if self.instance and self.instance.email == value:
            return value
        if Tenant.objects.filter(email=value).exists():
            raise serializers.ValidationError("A tenant with this email already exists")
        return value

    def validate_national_id(self, value):
        """Ensure national ID is unique"""
        if self.instance and self.instance.national_id == value:
            return value
        if Tenant.objects.filter(national_id=value).exists():
            raise serializers.ValidationError("A tenant with this national ID already exists")
        return value


class LeaseSerializer(serializers.ModelSerializer):
    """Serializer for lease agreements"""
    tenant_details = TenantSerializer(source='tenant', read_only=True)
    property_details = serializers.SerializerMethodField()
    duration_months = serializers.SerializerMethodField()
    total_rent_amount = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Lease
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'lease_number']
        
    def get_property_details(self, obj):
        if obj.rental_property:
            return {
                'id': obj.rental_property.property.id,
                'title': obj.rental_property.property.title,
                'address': obj.rental_property.property.address,
                'rental_id': obj.rental_property.id,
            }
        return None
        
    def get_duration_months(self, obj):
        return obj.duration_months
        
    def get_total_rent_amount(self, obj):
        return obj.total_rent_amount
        
    def get_is_active(self, obj):
        return obj.is_active
        
    def get_days_remaining(self, obj):
        return obj.days_remaining

    def validate(self, attrs):
        """Validate lease data"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
            
        # Validate rent amount
        monthly_rent = attrs.get('monthly_rent', 0)
        if monthly_rent <= 0:
            raise serializers.ValidationError("Monthly rent must be greater than zero")
            
        return attrs


class MaintenanceCategorySerializer(serializers.ModelSerializer):
    """Serializer for maintenance categories"""
    request_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceCategory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
    def get_request_count(self, obj):
        return obj.requests.count()


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Serializer for maintenance requests"""
    property_details = serializers.SerializerMethodField()
    category_details = MaintenanceCategorySerializer(source='category', read_only=True)
    requested_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    cost_variance = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reported_date']
        
    def get_property_details(self, obj):
        return {
            'id': obj.property.id,
            'title': obj.property.title,
            'address': obj.property.address,
        } if obj.property else None
        
    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip()
        return None
        
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return None
        
    def get_is_overdue(self, obj):
        return obj.is_overdue
        
    def get_duration_days(self, obj):
        return obj.duration_days
        
    def get_cost_variance(self, obj):
        return obj.cost_variance

    def validate(self, attrs):
        """Validate maintenance request"""
        due_date = attrs.get('due_date')
        if due_date and due_date < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past")
            
        estimated_cost = attrs.get('estimated_cost')
        actual_cost = attrs.get('actual_cost')
        
        if estimated_cost is not None and estimated_cost < 0:
            raise serializers.ValidationError("Estimated cost cannot be negative")
            
        if actual_cost is not None and actual_cost < 0:
            raise serializers.ValidationError("Actual cost cannot be negative")
            
        return attrs


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Serializer for expense categories"""
    expense_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
    def get_expense_count(self, obj):
        return obj.expenses.count()
        
    def get_total_amount(self, obj):
        return obj.expenses.aggregate(total=Sum('total_amount'))['total'] or 0


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense management"""
    property_details = serializers.SerializerMethodField()
    category_details = ExpenseCategorySerializer(source='category', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_amount']
        
    def get_property_details(self, obj):
        return {
            'id': obj.property.id,
            'title': obj.property.title,
            'address': obj.property.address,
        } if obj.property else None
        
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None
        
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}".strip()
        return None
        
    def get_is_overdue(self, obj):
        return obj.is_overdue
        
    def get_days_until_due(self, obj):
        return obj.days_until_due

    def validate(self, attrs):
        """Validate expense data"""
        amount = attrs.get('amount')
        tax_amount = attrs.get('tax_amount', 0)
        
        if amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
            
        if tax_amount < 0:
            raise serializers.ValidationError("Tax amount cannot be negative")
            
        # Auto-calculate total amount
        attrs['total_amount'] = amount + tax_amount
        
        return attrs


class PropertyAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for property analytics"""
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = PropertyAnalytics
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'calculation_date']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for generated reports"""
    generated_by_name = serializers.SerializerMethodField()
    properties_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'generation_time']
        
    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return f"{obj.generated_by.first_name} {obj.generated_by.last_name}".strip()
        return None
        
    def get_properties_count(self, obj):
        return obj.properties.count()


# -------------------------------------------------------------------------
# Dashboard Serializers for Property Management
# -------------------------------------------------------------------------

class PropertyDashboardSerializer(serializers.ModelSerializer):
    """Comprehensive dashboard serializer for properties with rental and maintenance info"""
    rental_info = serializers.SerializerMethodField()
    maintenance_status = serializers.SerializerMethodField()
    location_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'property_number', 'property_type', 'property_type_display',
            'status', 'status_display', 'market_value', 'size_sqm', 'location_display',
            'is_published', 'is_featured', 'is_verified', 'view_count', 'created_at',
            'days_since_created', 'rental_info', 'maintenance_status'
        ]
        
    def get_rental_info(self, obj):
        if hasattr(obj, 'rental_info'):
            rental = obj.rental_info
            return {
                'rental_status': rental.rental_status,
                'monthly_rent': float(rental.monthly_rent),
                'is_occupied': rental.is_occupied,
                'current_tenant': rental.current_tenant.full_name if rental.current_tenant else None,
            }
        return None
        
    def get_maintenance_status(self, obj):
        pending_requests = obj.maintenance_requests.filter(status='pending').count()
        overdue_requests = obj.maintenance_requests.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'assigned', 'in_progress']
        ).count()
        
        return {
            'pending_requests': pending_requests,
            'overdue_requests': overdue_requests,
        }
        
    def get_location_display(self, obj):
        if obj.location:
            return f"{obj.location.city}, {obj.location.state}"
        return obj.address[:50] + "..." if len(obj.address) > 50 else obj.address
    
    def get_days_since_created(self, obj):
        if obj.created_at:
            return (timezone.now() - obj.created_at).days
        return 0


class TenantDashboardSerializer(serializers.ModelSerializer):
    """Dashboard serializer for tenants"""
    current_lease_info = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = ['id', 'full_name', 'email', 'phone', 'status', 
                 'current_lease_info', 'payment_status', 'created_at']
        
    def get_current_lease_info(self, obj):
        lease = obj.current_lease
        if lease:
            return {
                'property_title': lease.rental_property.property.title,
                'monthly_rent': float(lease.monthly_rent),
                'start_date': lease.start_date,
                'end_date': lease.end_date,
                'days_remaining': lease.days_remaining,
            }
        return None
        
    def get_payment_status(self, obj):
        # This would be implemented with a payment tracking system
        return {
            'last_payment': None,
            'next_due_date': None,
            'overdue_amount': 0,
        }


class MaintenanceDashboardSerializer(serializers.ModelSerializer):
    """Dashboard serializer for maintenance requests"""
    property_title = serializers.CharField(source='property.title')
    category_name = serializers.CharField(source='category.name')
    days_since_reported = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRequest
        fields = ['id', 'title', 'property_title', 'category_name', 'priority', 
                 'status', 'estimated_cost', 'days_since_reported', 'is_overdue', 'reported_date']
        
    def get_days_since_reported(self, obj):
        if obj.reported_date:
            return (timezone.now() - obj.reported_date).days
        return 0


# -------------------------------------------------------------------------
# Worker Management Serializers
# -------------------------------------------------------------------------

class WorkerCategorySerializer(serializers.ModelSerializer):
    worker_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkerCategory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_worker_count(self, obj):
        return obj.workers.filter(status='active').count()

class WorkerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    category_names = serializers.SerializerMethodField()
    current_jobs_count = serializers.SerializerMethodField()
    can_take_new_job = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Worker
        fields = '__all__'
        read_only_fields = ['employee_id', 'total_jobs_completed', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_category_names(self, obj):
        return [category.name for category in obj.categories.all()]
    
    def get_current_jobs_count(self, obj):
        return obj.current_active_jobs
    
    def get_can_take_new_job(self, obj):
        return obj.can_take_new_job
    
    def get_supervisor_name(self, obj):
        if obj.supervisor:
            return f"{obj.supervisor.first_name} {obj.supervisor.last_name}"
        return None

class WorkerBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    category_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Worker
        fields = ['id', 'employee_id', 'full_name', 'phone', 'category_names', 
                 'is_available', 'status', 'rating']
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_category_names(self, obj):
        return [category.name for category in obj.categories.all()]




class PropertyManagementCompanySerializer(serializers.ModelSerializer):
    total_properties = serializers.SerializerMethodField()
    total_workers = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyManagementCompany
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_properties(self, obj):
        return obj.total_properties
    
    def get_total_workers(self, obj):
        return obj.total_workers

class WorkerPropertyAssignmentSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='worker.full_name', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = WorkerPropertyAssignment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class PropertyMaintenanceWorkflowSerializer(serializers.ModelSerializer):
    maintenance_request_title = serializers.CharField(source='maintenance_request.title', read_only=True)
    
    class Meta:
        model = PropertyMaintenanceWorkflow
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']