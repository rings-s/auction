from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from .models import Media, Property, Room, Auction, Bid, Location, Message, MessageAttachment
import json, logging

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

    class Meta:
        model = Media
        fields = ['id', 'file', 'url', 'name', 'media_type', 'is_primary', 'order', 
                 'content_type', 'content_type_str', 'object_id', 'file_size', 'dimensions', 'created_at']
        read_only_fields = ['file_size', 'dimensions', 'created_at']

    def get_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

    def get_file_size(self, obj):
        return obj.file_size

    def get_dimensions(self, obj):
        return obj.get_dimensions()

    def validate(self, data):
        content_type_str = data.pop('content_type_str', None)
        
        if not data.get('content_type') and content_type_str:
            if '.' in content_type_str:
                app_label, model = content_type_str.lower().split('.')
            else:
                app_label, model = 'base', content_type_str.lower()
            
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                data['content_type'] = content_type
            except ContentType.DoesNotExist:
                raise serializers.ValidationError({"content_type_str": f"Content type '{app_label}.{model}' not found"})
        
        if 'file' in data and not data.get('media_type'):
            file = data['file']
            if hasattr(file, 'content_type'):
                if file.content_type.startswith('image/'):
                    data['media_type'] = 'image'
                elif file.content_type.startswith('video/'):
                    data['media_type'] = 'video'
                elif 'pdf' in file.content_type.lower():
                    data['media_type'] = 'document'
                else:
                    data['media_type'] = 'other'
        
        return data

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
    auction_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Bid
        fields = '__all__'
        read_only_fields = ['bidder', 'bid_time', 'status', 'ip_address', 'is_verified', 'created_at', 'updated_at']

    def get_bidder_info(self, obj):
        if not obj.bidder:
            return None
        return {
            'id': obj.bidder.id,
            'name': obj.bidder_name,
            'email': obj.bidder.email,
            'is_verified': getattr(obj.bidder, 'is_verified', False)
        }

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
    
    class Meta:
        model = Message
        fields = [
            'id', 'subject', 'body', 'status', 'status_display', 'priority', 'priority_display', 
            'sender_info', 'recipient_info', 'property_info', 'thread_id', 'parent_message',
            'is_read', 'created_at', 'read_at', 'replied_at'
        ]
        read_only_fields = ['sender_info', 'recipient_info', 'thread_id', 'is_read', 'created_at', 'read_at', 'replied_at']

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