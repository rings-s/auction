from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from .models import Media, Property, Room, Auction, Bid, Location
import json

class LocationSerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_coordinates(self, obj):
        return obj.coordinates

    def validate(self, attrs):
        """Validate that both latitude and longitude are provided together"""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        # Only validate if one of them is provided
        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise serializers.ValidationError(
                _("Both latitude and longitude must be provided together.")
            )
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
        """Get file size in bytes"""
        return obj.file_size if hasattr(obj, 'file_size') else 0

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
                
                # Log for debugging
                print(f"Looking for content type with app_label='{app_label}', model='{model}'")
                
                try:
                    content_type = ContentType.objects.get(app_label=app_label, model=model)
                    data['content_type'] = content_type
                    print(f"Found content type: {content_type.app_label}.{content_type.model} (id={content_type.id})")
                except ContentType.DoesNotExist:
                    # List available content types to help debugging
                    available = list(ContentType.objects.filter(app_label=app_label).values_list('model', flat=True))
                    msg = f"Content type '{app_label}.{model}' not found. Available models in '{app_label}': {available}"
                    print(msg)
                    raise serializers.ValidationError({"content_type_str": msg})
                
            except Exception as e:
                # Provide detailed error for debugging
                print(f"Error resolving content_type_str '{content_type_str}': {str(e)}")
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
            
        # Validate media_type based on file extension
        if 'file' in data and 'media_type' not in data:
            # Auto-detect media type from file if not provided
            file = data['file']
            if hasattr(file, 'content_type'):
                if file.content_type.startswith('image/'):
                    data['media_type'] = 'image'
                elif file.content_type.startswith('video/'):
                    data['media_type'] = 'video'
                elif file.content_type.startswith('application/pdf'):
                    data['media_type'] = 'document'
                else:
                    data['media_type'] = 'other'
        
        return data

    def create(self, validated_data):
        """Create a new media instance with proper error handling"""
        try:
            # Check that content_type and object_id point to a valid object
            content_type = validated_data.get('content_type')
            object_id = validated_data.get('object_id')
            
            if content_type and object_id:
                # Try to get the related object to verify it exists
                model_class = content_type.model_class()
                if model_class:
                    try:
                        related_object = model_class.objects.get(pk=object_id)
                        print(f"Found related object: {related_object}")
                    except model_class.DoesNotExist:
                        print(f"Related object {content_type.model} with id={object_id} not found")
                        raise serializers.ValidationError({
                            "object_id": f"Object with id={object_id} of type {content_type.app_label}.{content_type.model} does not exist."
                        })
            
            # Proceed with creation
            instance = super().create(validated_data)
            
            # For image files, handle various processing tasks like thumbnails 
            # (already handled in the model's save method)
            
            return instance
            
        except Exception as e:
            import traceback
            print(f"Error creating media: {str(e)}")
            print(traceback.format_exc())
            raise

class RoomSerializer(serializers.ModelSerializer):
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
    def get_media(self, obj):
        """Get all media items for this room, ensuring correct content type and object_id match"""
        media_items = Media.objects.filter(
            content_type__model='room',
            object_id=obj.id
        )
        return MediaSerializer(media_items, many=True, context=self.context).data


class PropertySerializer(serializers.ModelSerializer):
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    building_type_display = serializers.CharField(source='get_building_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Nested serializers
    location = LocationSerializer(read_only=True)
    location_data = serializers.JSONField(write_only=True, required=False)
    
    rooms = RoomSerializer(many=True, read_only=True)
    media = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = [
            'property_number', 'slug', 'owner', 'is_verified', 
            'view_count', 'created_at', 'updated_at'
        ]

    def get_media(self, obj):
        """Get all media items directly associated with this property"""
        media_items = Media.objects.filter(
            content_type__model='property',
            object_id=obj.id
        )
        return MediaSerializer(media_items, many=True, context=self.context).data

    def get_main_image(self, obj):
        """Get the primary image for this property"""
        image = obj.get_main_image()
        return MediaSerializer(image, context=self.context).data if image else None

    def validate(self, data):
        """Validate property data"""
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT']:
            # Only require location_data for new properties
            if 'location_data' not in data and not self.instance:
                raise serializers.ValidationError(
                    {"location_data": _("Location is required for new properties.")}
                )

        # Validate minimum_bid and market_value
        minimum_bid = data.get('minimum_bid')
        market_value = data.get('market_value')
        if minimum_bid is not None and market_value is not None:
            if minimum_bid >= market_value:
                raise serializers.ValidationError(
                    {"minimum_bid": _("Minimum bid must be less than market value.")}
                )
                
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create a new property with nested objects"""
        location_data = validated_data.pop('location_data', None)
        
        if location_data:
            # Handle JSON string if provided
            if isinstance(location_data, str):
                try:
                    location_data = json.loads(location_data)
                except (json.JSONDecodeError, TypeError):
                    raise serializers.ValidationError(
                        {"location_data": _("Invalid location data format.")}
                    )
            
            # Process location
            try:
                # Try to find existing location
                location = None
                if all(key in location_data for key in ['city', 'state']):
                    location = Location.objects.filter(
                        city=location_data['city'],
                        state=location_data['state'],
                        country=location_data.get('country', 'المملكة العربية السعودية')
                    ).first()
                
                # Create new location if not found
                if not location:
                    location_serializer = LocationSerializer(data=location_data)
                    location_serializer.is_valid(raise_exception=True)
                    location = location_serializer.save()
                
                validated_data['location'] = location
            except Exception as e:
                raise serializers.ValidationError({"location_data": str(e)})

        # Set the owner from the request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        
        # Create the property
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a property with nested objects"""
        location_data = validated_data.pop('location_data', None)
        
        if location_data:
            # Handle JSON string
            if isinstance(location_data, str):
                try:
                    location_data = json.loads(location_data)
                except (json.JSONDecodeError, TypeError):
                    raise serializers.ValidationError(
                        {"location_data": _("Invalid location data format.")}
                    )
            
            # Update or create location
            try:
                if instance.location:
                    location_serializer = LocationSerializer(
                        instance.location, data=location_data, partial=True
                    )
                    location_serializer.is_valid(raise_exception=True)
                    location_serializer.save()
                else:
                    location_serializer = LocationSerializer(data=location_data)
                    location_serializer.is_valid(raise_exception=True)
                    location = location_serializer.save()
                    validated_data['location'] = location
            except Exception as e:
                raise serializers.ValidationError({"location_data": str(e)})

        return super().update(instance, validated_data)


class BidSerializer(serializers.ModelSerializer):
    bidder_info = serializers.SerializerMethodField()
    auction_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Bid
        fields = '__all__'
        read_only_fields = [
            'bidder', 'bid_time', 'status', 'ip_address',
            'is_verified', 'created_at', 'updated_at'
        ]

    def get_bidder_info(self, obj):
        if not obj.bidder:
            return None
        return {
            'id': obj.bidder.id,
            'name': obj.bidder_name,
            'email': obj.bidder.email
        }

    def get_auction_info(self, obj):
        if not obj.auction:
            return None
        return {
            'id': obj.auction.id,
            'title': obj.auction.title,
            'current_bid': float(obj.auction.current_bid) if obj.auction.current_bid else None
        }

    def validate(self, data):
        """Validate bid amount and auction requirements"""
        auction = data.get('auction')
        if not auction:
            raise serializers.ValidationError({"auction": _("Auction is required.")})

        # Verify auction is active
        if not auction.can_accept_bids():
            raise serializers.ValidationError(
                {"auction": _("This auction is not currently accepting bids.")}
            )

        # Validate bid amount
        bid_amount = data.get('bid_amount')
        current_bid = auction.current_bid or auction.starting_bid
        min_increment = auction.minimum_increment
        
        if bid_amount < current_bid + min_increment:
            raise serializers.ValidationError({
                "bid_amount": _("Bid must be at least {0} higher than current bid of {1}.").format(
                    min_increment, current_bid
                )
            })
            
        return data

    def create(self, validated_data):
        """Create a new bid with automatic bidder assignment"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['bidder'] = request.user
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
        
        return super().create(validated_data)


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
    highest_bid = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = '__all__'
        read_only_fields = [
            'slug', 'current_bid', 'bid_count', 'view_count', 
            'registered_bidders', 'created_at', 'updated_at'
        ]

    def get_media(self, obj):
        """Get all media items for this auction"""
        media_items = Media.objects.filter(
            content_type__model='auction',
            object_id=obj.id
        )
        return MediaSerializer(media_items, many=True, context=self.context).data

    def get_time_remaining(self, obj):
        return obj.time_remaining

    def get_highest_bid(self, obj):
        highest_bid = obj.bids.order_by('-bid_amount').first()
        return BidSerializer(highest_bid, context=self.context).data if highest_bid else None
        
    def get_is_active(self, obj):
        return obj.is_active()

    def validate(self, data):
        """Validate auction dates and requirements"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        registration_deadline = data.get('registration_deadline')

        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError(
                {"end_date": _("End date must be after start date.")}
            )
            
        if registration_deadline and start_date and registration_deadline >= start_date:
            raise serializers.ValidationError(
                {"registration_deadline": _("Registration deadline must be before start date.")}
            )
            
        request = self.context.get('request')
        if request and request.method == 'POST':
            if 'related_property' not in data:
                raise serializers.ValidationError(
                    {"related_property_id": _("Property is required.")}
                )
                
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create auction with properly linked property"""
        # Verify property is available for auction
        related_property = validated_data.get('related_property')
        if related_property and related_property.status not in ['available', 'auction']:
            raise serializers.ValidationError({
                "related_property_id": _("Property is not available for auction.")
            })
            
        return super().create(validated_data)