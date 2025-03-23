from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.gis.geos import Point
from .models import (
    Property, Document, Auction, Bid, Contract, Payment,
    Transaction, Message, MessageThread, ThreadParticipant, Notification, PropertyView
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Minimal serializer for user information in related objects"""
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'avatar_url')
        read_only_fields = ('id', 'email', 'full_name', 'avatar_url')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_avatar_url(self, obj):
        if hasattr(obj, 'avatar_url') and obj.avatar_url:
            return obj.avatar_url
        return None


class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for listing properties"""
    owner_name = serializers.SerializerMethodField()
    main_image_url = serializers.ReadOnlyField()
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    has_auction = serializers.ReadOnlyField()

    class Meta:
        model = Property
        fields = (
            'id', 'property_number', 'title', 'property_type', 'property_type_display',
            'city', 'district', 'area', 'bedrooms', 'bathrooms',
            'estimated_value', 'status', 'status_display', 'owner_name',
            'main_image_url', 'is_featured', 'is_published', 'has_auction',
            'views_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'property_number', 'created_at', 'updated_at')

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}"


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed property information"""
    owner = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    main_image_url = serializers.ReadOnlyField()
    has_auction = serializers.ReadOnlyField()

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('id', 'property_number', 'created_at', 'updated_at',
                           'is_verified', 'verified_by', 'verification_date')

    def validate(self, data):
        """Validate coordinates if provided"""
        latitude = data.get('latitude', None)
        longitude = data.get('longitude', None)

        if latitude and longitude:
            try:
                # Validate coordinates and create a Point
                data['location'] = Point(float(longitude), float(latitude), srid=4326)
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError({"coordinates": _("Invalid coordinates provided.")})

        return data


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating property"""
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Property
        exclude = ('property_number', 'is_verified', 'verified_by', 'verification_date', 'views_count')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate coordinates if provided"""
        latitude = data.get('latitude', None)
        longitude = data.get('longitude', None)

        if latitude and longitude:
            try:
                # Validate coordinates and create a Point
                data['location'] = Point(float(longitude), float(latitude), srid=4326)
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError({"coordinates": _("Invalid coordinates provided.")})

        return data

    def create(self, validated_data):
        """Generate property number and set owner"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user

        # Generate property number
        from datetime import datetime
        import random
        property_number = f"PROP-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        validated_data['property_number'] = property_number

        return super().create(validated_data)


class PropertyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating property"""
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Property
        exclude = ('property_number', 'is_verified', 'verified_by', 'verification_date', 'owner')
        read_only_fields = ('id', 'created_at', 'updated_at', 'views_count')

    def validate(self, data):
        """Validate coordinates if provided"""
        latitude = data.get('latitude', None)
        longitude = data.get('longitude', None)

        if latitude and longitude:
            try:
                # Validate coordinates and create a Point
                data['location'] = Point(float(longitude), float(latitude), srid=4326)
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError({"coordinates": _("Invalid coordinates provided.")})

        # Check if user is owner or has appropriate permissions
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_staff and self.instance.owner != request.user:
                raise serializers.ValidationError(
                    _("You don't have permission to update this property.")
                )

        return data


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for document model"""
    uploaded_by = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    verification_status_display = serializers.CharField(source='get_verification_status_display', read_only=True)
    is_expired = serializers.ReadOnlyField()
    main_file_url = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('id', 'document_number', 'created_at', 'updated_at',
                           'verified_by', 'verification_date', 'verification_status')

    def create(self, validated_data):
        """Generate document number and set uploader"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user

        # Generate document number
        from datetime import datetime
        import random
        document_number = f"DOC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        validated_data['document_number'] = document_number

        return super().create(validated_data)


class BidSerializer(serializers.ModelSerializer):
    """Serializer for auction bids"""
    bidder = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Bid
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'status', 'ip_address', 'user_agent', 'device_info')

    def validate(self, data):
        """Validate bid amount"""
        auction = data.get('auction')
        bid_amount = data.get('bid_amount')

        if not auction:
            raise serializers.ValidationError(_("Auction is required."))

        if not bid_amount:
            raise serializers.ValidationError(_("Bid amount is required."))

        # Check if auction is active
        if not auction.is_active:
            raise serializers.ValidationError(_("Auction is not active."))

        # Check if bid amount is greater than current bid + min increment
        min_bid = auction.current_bid + auction.min_bid_increment
        if bid_amount < min_bid:
            raise serializers.ValidationError(
                _("Bid amount must be at least {0}.").format(min_bid)
            )

        # Check for autobidding
        if data.get('is_auto_bid') and not data.get('max_bid_amount'):
            raise serializers.ValidationError(_("Max bid amount is required for auto bidding."))

        if data.get('max_bid_amount') and data.get('max_bid_amount') < bid_amount:
            raise serializers.ValidationError(_("Max bid amount must be greater than bid amount."))

        return data

    def create(self, validated_data):
        """Set bidder and tracking info"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['bidder'] = request.user

            # Track IP and user agent
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT')
            validated_data['device_info'] = {
                'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else None,
                'browser': request.user_agent.browser.family if hasattr(request, 'user_agent') else None,
                'os': request.user_agent.os.family if hasattr(request, 'user_agent') else None,
            }

        return super().create(validated_data)


class AuctionListSerializer(serializers.ModelSerializer):
    """Serializer for listing auctions"""
    property_title = serializers.CharField(source='related_property.title', read_only=True)
    property_type = serializers.CharField(source='related_property.property_type', read_only=True)
    auctioneer_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    auction_type_display = serializers.CharField(source='get_auction_type_display', read_only=True)
    featured_image_url = serializers.ReadOnlyField()
    bid_count = serializers.ReadOnlyField()
    time_remaining = serializers.ReadOnlyField()

    class Meta:
        model = Auction
        fields = (
            'id', 'uuid', 'title', 'slug', 'property_title', 'property_type',
            'auction_type', 'auction_type_display', 'status', 'status_display',
            'start_date', 'end_date', 'starting_price', 'current_bid',
            'min_bid_increment', 'featured_image_url', 'auctioneer_name',
            'bid_count', 'time_remaining', 'is_featured', 'is_published',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'uuid', 'created_at', 'updated_at', 'current_bid')

    def get_auctioneer_name(self, obj):
        return f"{obj.auctioneer.first_name} {obj.auctioneer.last_name}"


class AuctionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed auction information"""
    related_property = PropertyListSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    auctioneer = UserSerializer(read_only=True)
    winning_bidder = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    auction_type_display = serializers.CharField(source='get_auction_type_display', read_only=True)
    featured_image_url = serializers.ReadOnlyField()
    bid_count = serializers.ReadOnlyField()
    unique_bidders_count = serializers.ReadOnlyField()
    time_remaining = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    highest_bid = serializers.ReadOnlyField()

    # Recent bids
    recent_bids = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = '__all__'
        read_only_fields = ('id', 'uuid', 'created_at', 'updated_at', 'current_bid',
                           'winning_bid', 'winning_bidder', 'end_reason')

    def get_recent_bids(self, obj):
        """Get recent bids for this auction"""
        recent_bids = obj.bids.order_by('-bid_time')[:5]
        return BidSerializer(recent_bids, many=True).data


class AuctionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating auctions"""
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source='related_property',
        write_only=True
    )

    class Meta:
        model = Auction
        exclude = ('uuid', 'current_bid', 'winning_bid', 'winning_bidder', 'end_reason', 'views_count')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate auction data"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(_("End date must be after start date."))

        # Validate reserve price
        if data.get('reserve_price', 0) < data.get('starting_price', 0):
            raise serializers.ValidationError(_("Reserve price must be greater than or equal to starting price."))

        # Check if property already has an active auction
        property_obj = data.get('related_property')
        if property_obj and property_obj.has_auction:
            raise serializers.ValidationError(_("Property already has an active auction."))

        return data

    def create(self, validated_data):
        """Set creator and generate slug"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user

            # If auctioneer not specified, set to creator
            if 'auctioneer' not in validated_data:
                validated_data['auctioneer'] = request.user

        # Generate slug
        from django.utils.text import slugify
        import random
        title = validated_data.get('title', '')
        random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        validated_data['slug'] = f"{slugify(title)}-{random_suffix}"

        return super().create(validated_data)


class ContractSerializer(serializers.ModelSerializer):
    """Serializer for contracts"""
    related_property = PropertyListSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    agent = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    is_fully_signed = serializers.ReadOnlyField()
    main_file_url = serializers.ReadOnlyField()

    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ('id', 'contract_number', 'created_at', 'updated_at',
                           'is_verified', 'verification_authority', 'verification_date')

    def create(self, validated_data):
        """Generate contract number"""
        # Generate contract number
        from datetime import datetime
        import random
        contract_number = f"CONT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        validated_data['contract_number'] = contract_number

        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    payer = UserSerializer(read_only=True)
    payee = UserSerializer(read_only=True)
    confirmed_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    receipt_url = serializers.ReadOnlyField()

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'payment_number', 'created_at', 'updated_at',
                           'confirmed_at', 'confirmed_by')

    def create(self, validated_data):
        """Generate payment number"""
        # Generate payment number
        from datetime import datetime
        import random
        payment_number = f"PAY-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        validated_data['payment_number'] = payment_number

        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for financial transactions"""
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    processed_by = UserSerializer(read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('id', 'transaction_number', 'created_at', 'updated_at',
                           'processed_at', 'processed_by')

    def create(self, validated_data):
        """Generate transaction number"""
        # Generate transaction number
        from datetime import datetime
        import random
        transaction_number = f"TRANS-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        validated_data['transaction_number'] = transaction_number

        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    sender = UserSerializer(read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    has_attachments = serializers.ReadOnlyField()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at')

    def create(self, validated_data):
        """Set sender and timestamps"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user

        validated_data['sent_at'] = timezone.now()

        # Get thread and update last_message_at
        thread = validated_data.get('thread')
        if thread:
            thread.last_message_at = timezone.now()
            thread.save(update_fields=['last_message_at', 'updated_at'])

        return super().create(validated_data)


class ThreadParticipantSerializer(serializers.ModelSerializer):
    """Serializer for thread participants"""
    user = UserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    has_unread_messages = serializers.ReadOnlyField()
    unread_count = serializers.ReadOnlyField()

    class Meta:
        model = ThreadParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class MessageThreadListSerializer(serializers.ModelSerializer):
    """Serializer for listing message threads"""
    thread_type_display = serializers.CharField(source='get_thread_type_display', read_only=True)
    participants_count = serializers.SerializerMethodField()
    message_count = serializers.ReadOnlyField()
    unread_count = serializers.ReadOnlyField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = (
            'id', 'subject', 'thread_type', 'thread_type_display',
            'participants_count', 'message_count', 'unread_count',
            'last_message_at', 'is_active', 'is_resolved',
            'last_message_preview', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_message_at')

    def get_participants_count(self, obj):
        return obj.participants.count()

    def get_last_message_preview(self, obj):
        last_message = obj.last_message
        if last_message:
            return {
                'sender_name': f"{last_message.sender.first_name} {last_message.sender.last_name}",
                'content': last_message.content[:100] + ('...' if len(last_message.content) > 100 else ''),
                'sent_at': last_message.sent_at
            }
        return None


class MessageThreadDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed message thread information"""
    participants = serializers.SerializerMethodField()
    thread_type_display = serializers.CharField(source='get_thread_type_display', read_only=True)
    messages = serializers.SerializerMethodField()
    resolved_by = UserSerializer(read_only=True)

    class Meta:
        model = MessageThread
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_message_at',
                           'resolved_at', 'resolved_by')

    def get_participants(self, obj):
        """Get participants with roles"""
        participants = obj.thread_participants.select_related('user')
        return ThreadParticipantSerializer(participants, many=True).data

    def get_messages(self, obj):
        """Get messages for this thread"""
        messages = obj.messages.order_by('sent_at')
        return MessageSerializer(messages, many=True).data


class MessageThreadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating message threads"""
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    initial_message = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = MessageThread
        fields = (
            'subject', 'thread_type', 'related_property', 'related_auction',
            'related_contract', 'participant_ids', 'initial_message'
        )

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        initial_message = validated_data.pop('initial_message', None)

        # Create thread
        thread = super().create(validated_data)

        # Add creator as participant
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            ThreadParticipant.objects.create(
                thread=thread,
                user=request.user,
                role='owner'
            )

            # Add initial message if provided
            if initial_message:
                Message.objects.create(
                    thread=thread,
                    sender=request.user,
                    content=initial_message,
                    sent_at=timezone.now()
                )

                # Update last_message_at
                thread.last_message_at = timezone.now()
                thread.save(update_fields=['last_message_at'])

        # Add other participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                ThreadParticipant.objects.create(
                    thread=thread,
                    user=user,
                    role='member'
                )
            except User.DoesNotExist:
                pass

        return thread


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    recipient = UserSerializer(read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_sent', 'sent_at', 'is_read', 'read_at')

    def create(self, validated_data):
        """Set timestamps"""
        validated_data['is_sent'] = True
        validated_data['sent_at'] = timezone.now()

        return super().create(validated_data)


class BidCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bids"""

    class Meta:
        model = Bid
        fields = ('auction', 'bid_amount', 'is_auto_bid', 'max_bid_amount')

    def validate(self, data):
        """Validate bid amount"""
        auction = data.get('auction')
        bid_amount = data.get('bid_amount')

        if not auction:
            raise serializers.ValidationError(_("Auction is required."))

        if not bid_amount:
            raise serializers.ValidationError(_("Bid amount is required."))

        # Check if auction is active
        if not auction.is_active:
            raise serializers.ValidationError(_("Auction is not active."))

        # Check if bid amount is greater than current bid + min increment
        min_bid = auction.current_bid + auction.min_bid_increment
        if bid_amount < min_bid:
            raise serializers.ValidationError(
                _("Bid amount must be at least {0}.").format(min_bid)
            )

        # Check for autobidding
        if data.get('is_auto_bid') and not data.get('max_bid_amount'):
            raise serializers.ValidationError(_("Max bid amount is required for auto bidding."))

        if data.get('max_bid_amount') and data.get('max_bid_amount') < bid_amount:
            raise serializers.ValidationError(_("Max bid amount must be greater than bid amount."))

        return data

    def create(self, validated_data):
        """Set bidder and tracking info"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['bidder'] = request.user

            # Track IP and user agent
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT')
            validated_data['device_info'] = {
                'is_mobile': request.user_agent.is_mobile if hasattr(request, 'user_agent') else None,
                'browser': request.user_agent.browser.family if hasattr(request, 'user_agent') else None,
                'os': request.user_agent.os.family if hasattr(request, 'user_agent') else None,
            }

        return super().create(validated_data)


class AuctionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating auctions"""

    class Meta:
        model = Auction
        exclude = ('uuid', 'current_bid', 'winning_bid', 'winning_bidder', 'end_reason', 'created_by', 'views_count')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate auction data"""
        # Get instance values for partial updates
        instance = self.instance

        start_date = data.get('start_date', instance.start_date if instance else None)
        end_date = data.get('end_date', instance.end_date if instance else None)

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(_("End date must be after start date."))

        # Validate reserve price
        starting_price = data.get('starting_price', instance.starting_price if instance else None)
        reserve_price = data.get('reserve_price', instance.reserve_price if instance else None)

        if starting_price and reserve_price and reserve_price < starting_price:
            raise serializers.ValidationError(_("Reserve price must be greater than or equal to starting price."))

        # Validate status transitions
        if 'status' in data:
            new_status = data['status']
            old_status = instance.status if instance else None

            valid_transitions = {
                'draft': ['pending', 'cancelled'],
                'pending': ['active', 'cancelled'],
                'active': ['extended', 'closed', 'cancelled'],
                'extended': ['closed', 'cancelled'],
                'closed': ['sold', 'cancelled'],
                'sold': []  # Final state
            }

            if old_status and new_status not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError(
                    _("Invalid status transition from '{0}' to '{1}'").format(old_status, new_status)
                )

        return data

    def update(self, instance, validated_data):
        """Update auction and handle any location data"""
        # Handle location data if present
        if 'location_coordinates' in validated_data and isinstance(validated_data['location_coordinates'], dict):
            lat = validated_data['location_coordinates'].get('latitude')
            lng = validated_data['location_coordinates'].get('longitude')
            if lat is not None and lng is not None:
                validated_data['location_coordinates'] = Point(float(lng), float(lat), srid=4326)

        return super().update(instance, validated_data)


class ContractCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contracts"""
    auction_id = serializers.PrimaryKeyRelatedField(
        queryset=Auction.objects.all(),
        source='auction',
        write_only=True
    )

    class Meta:
        model = Contract
        exclude = ('contract_number', 'is_verified', 'verification_authority', 'verification_date',
                  'buyer_signed', 'seller_signed', 'agent_signed',
                  'buyer_signature_date', 'seller_signature_date', 'agent_signature_date')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate contract data"""
        auction = data.get('auction')

        if not auction:
            raise serializers.ValidationError(_("Auction is required."))

        # Ensure auction is closed or sold
        if auction.status not in ['closed', 'sold']:
            raise serializers.ValidationError(_("Contract can only be created for closed or sold auctions."))

        # Get property from auction
        property_obj = auction.related_property
        data['related_property'] = property_obj

        # Check if auction already has a contract
        if hasattr(auction, 'contract'):
            raise serializers.ValidationError(_("This auction already has a contract."))

        # Set buyer from winning bidder if not provided
        if 'buyer' not in data and auction.winning_bidder:
            data['buyer'] = auction.winning_bidder

        # Set seller from property owner if not provided
        if 'seller' not in data:
            data['seller'] = property_obj.owner

        # Set contract_amount from winning_bid if not provided
        if 'contract_amount' not in data and auction.winning_bid:
            data['contract_amount'] = auction.winning_bid

        # Validate total_amount calculation
        contract_amount = data.get('contract_amount', 0)
        commission_amount = data.get('commission_amount', 0)
        tax_amount = data.get('tax_amount', 0)
        total_amount = data.get('total_amount')

        calculated_total = contract_amount + commission_amount + tax_amount
        if total_amount is not None and total_amount != calculated_total:
            data['total_amount'] = calculated_total

        return data

    def create(self, validated_data):
        """Generate contract number and set agent if not provided"""
        # Set agent from request user if not provided
        request = self.context.get('request')
        if request and hasattr(request, 'user') and 'agent' not in validated_data:
            validated_data['agent'] = request.user

        # Generate contract number
        from datetime import datetime
        import random
        contract_number = f"CONT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        validated_data['contract_number'] = contract_number

        # Set contract date to now if not provided
        if 'contract_date' not in validated_data:
            validated_data['contract_date'] = datetime.now().date()

        return super().create(validated_data)


class ContractUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating contracts"""

    class Meta:
        model = Contract
        exclude = ('contract_number', 'auction', 'related_property', 'buyer', 'seller',
                  'is_verified', 'verification_authority', 'verification_date')
        read_only_fields = ('id', 'created_at', 'updated_at',
                           'buyer_signed', 'seller_signed', 'agent_signed',
                           'buyer_signature_date', 'seller_signature_date', 'agent_signature_date')

    def validate(self, data):
        """Validate contract update data"""
        instance = self.instance

        # Validate status transitions
        if 'status' in data:
            new_status = data['status']
            old_status = instance.status

            valid_transitions = {
                'draft': ['pending_review', 'cancelled'],
                'pending_review': ['pending_buyer', 'pending_seller', 'cancelled'],
                'pending_buyer': ['pending_seller', 'signed', 'cancelled'],
                'pending_seller': ['pending_buyer', 'signed', 'cancelled'],
                'pending_payment': ['active', 'cancelled'],
                'signed': ['pending_payment', 'active', 'disputed'],
                'active': ['completed', 'disputed'],
                'completed': ['disputed'],
                'cancelled': [],
                'disputed': ['active', 'cancelled', 'completed']
            }

            if new_status not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError(
                    _("Invalid status transition from '{0}' to '{1}'").format(old_status, new_status)
                )

        # Validate total_amount calculation
        contract_amount = data.get('contract_amount', instance.contract_amount)
        commission_amount = data.get('commission_amount', instance.commission_amount)
        tax_amount = data.get('tax_amount', instance.tax_amount)
        total_amount = data.get('total_amount')

        calculated_total = contract_amount + commission_amount + tax_amount
        if total_amount is not None and total_amount != calculated_total:
            data['total_amount'] = calculated_total

        return data


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transactions"""
    payment_id = serializers.PrimaryKeyRelatedField(
        queryset=Payment.objects.all(),
        source='payment',
        required=False,
        allow_null=True,
        write_only=True
    )
    auction_id = serializers.PrimaryKeyRelatedField(
        queryset=Auction.objects.all(),
        source='auction',
        required=False,
        allow_null=True,
        write_only=True
    )
    contract_id = serializers.PrimaryKeyRelatedField(
        queryset=Contract.objects.all(),
        source='contract',
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = Transaction
        exclude = ('transaction_number', 'processed_at', 'processed_by')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate transaction data"""
        # Validate from_user and to_user
        from_user = data.get('from_user')
        to_user = data.get('to_user')

        if from_user == to_user:
            raise serializers.ValidationError(_("Sender and recipient cannot be the same user."))

        # Validate transaction amount
        amount = data.get('amount')
        if amount is not None and amount <= 0:
            raise serializers.ValidationError(_("Transaction amount must be greater than zero."))

        # Validate transaction date
        transaction_date = data.get('transaction_date')
        if transaction_date is not None:
            from django.utils import timezone
            if transaction_date > timezone.now():
                raise serializers.ValidationError(_("Transaction date cannot be in the future."))

        # Set transaction date to now if not provided
        if 'transaction_date' not in data:
            from django.utils import timezone
            data['transaction_date'] = timezone.now()

        return data

    def create(self, validated_data):
        """Generate transaction number"""
        # Generate transaction number
        from datetime import datetime
        import random
        transaction_number = f"TRANS-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        validated_data['transaction_number'] = transaction_number

        return super().create(validated_data)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating transactions"""

    class Meta:
        model = Transaction
        exclude = ('transaction_number', 'from_user', 'to_user', 'payment', 'auction', 'contract',
                  'processed_at', 'processed_by')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate transaction update data"""
        instance = self.instance

        # Validate status transitions
        if 'status' in data:
            new_status = data['status']
            old_status = instance.status

            valid_transitions = {
                'pending': ['processing', 'completed', 'failed', 'cancelled'],
                'processing': ['completed', 'failed', 'disputed'],
                'completed': ['disputed', 'refunded'],
                'failed': ['processing', 'cancelled'],
                'cancelled': [],
                'disputed': ['completed', 'failed', 'refunded'],
                'refunded': []
            }

            if new_status not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError(
                    _("Invalid status transition from '{0}' to '{1}'").format(old_status, new_status)
                )

        return data

    def update(self, instance, validated_data):
        """Update transaction and set processed info if status changes"""
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        # If status is changing, record who processed it
        if old_status != new_status:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['processed_by'] = request.user

            from django.utils import timezone
            validated_data['processed_at'] = timezone.now()

        return super().update(instance, validated_data)




class PropertyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyView
        fields = [
            'id', 'auction', 'view_type', 'size_sqm', 'location', 'address',
            'elevation', 'view_direction', 'legal_description', 'condition',
            'historical_views', 'images'  # Updated to JSONField
        ]
        read_only_fields = ['id']  # Add 'created_at', 'modified_at' if using TimeStampedModel

    def validate_images(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(_("Images must be a list."))
        return value

    def validate_size_sqm(self, value):
        if value <= 0:
            raise serializers.ValidationError(_("Size must be greater than zero."))
        return value
