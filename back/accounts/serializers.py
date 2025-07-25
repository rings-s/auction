from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, BankAccount, Payment
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='user', required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'role')
        extra_kwargs = {
            'first_name': {'required': True}, 'last_name': {'required': True},
            'phone_number': {'required': False}, 'date_of_birth': {'required': False},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.pop('confirm_password', None):
            raise serializers.ValidationError({"confirm_password": _("Passwords do not match.")})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        logger.info(f"User '{user.email}' created successfully")
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    date_of_birth = serializers.DateField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()

    # Identity fields
    identity_type = serializers.CharField(source='profile.identity_type', read_only=True, allow_null=True)
    identity_type_display = serializers.SerializerMethodField()
    identity_number = serializers.CharField(source='profile.identity_number', read_only=True, allow_null=True)

    # Profile fields
    bio = serializers.CharField(source='profile.bio', read_only=True, allow_null=True)
    company_name = serializers.CharField(source='profile.company_name', read_only=True, allow_null=True)
    company_registration = serializers.CharField(source='profile.company_registration', read_only=True, allow_null=True)
    tax_id = serializers.CharField(source='profile.tax_id', read_only=True, allow_null=True)
    address = serializers.CharField(source='profile.address', read_only=True, allow_null=True)
    city = serializers.CharField(source='profile.city', read_only=True, allow_null=True)
    state = serializers.CharField(source='profile.state', read_only=True, allow_null=True)
    postal_code = serializers.CharField(source='profile.postal_code', read_only=True, allow_null=True)
    country = serializers.CharField(source='profile.country', read_only=True, allow_null=True)
    credit_limit = serializers.DecimalField(source='profile.credit_limit', max_digits=15, decimal_places=2, read_only=True)
    rating = serializers.DecimalField(source='profile.rating', max_digits=3, decimal_places=2, read_only=True, allow_null=True)
    license_number = serializers.CharField(source='profile.license_number', read_only=True, allow_null=True)
    license_expiry = serializers.DateField(source='profile.license_expiry', read_only=True, allow_null=True)
    preferred_locations = serializers.CharField(source='profile.preferred_locations', read_only=True, allow_null=True)
    property_preferences = serializers.CharField(source='profile.property_preferences', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'uuid', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'avatar_url', 'profile_image_url', 'is_verified', 'is_active', 'is_staff', 'date_joined',
            'identity_type', 'identity_type_display', 'identity_number',
            'bio', 'company_name', 'company_registration', 'tax_id', 'address', 'city', 'state',
            'postal_code', 'country', 'license_number', 'license_expiry', 'preferred_locations',
            'property_preferences', 'credit_limit', 'rating',
        )
        read_only_fields = fields

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url') and request:
            try:
                return request.build_absolute_uri(obj.avatar.url)
            except Exception as e:
                logger.warning(f"Could not build avatar URL: {e}")
        return None

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        profile = getattr(obj, 'profile', None)
        if profile and profile.profile_image and hasattr(profile.profile_image, 'url') and request:
            try:
                return request.build_absolute_uri(profile.profile_image.url)
            except Exception as e:
                logger.warning(f"Could not build profile image URL: {e}")
        return None

    def get_identity_type_display(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and profile.identity_type:
            return profile.get_identity_type_display()
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        profile = getattr(instance, 'profile', None)

        text_fields = [
            'bio', 'company_name', 'company_registration', 'tax_id', 'address',
            'city', 'state', 'postal_code', 'country', 'license_number',
            'preferred_locations', 'property_preferences', 'identity_type', 'identity_number'
        ]
        decimal_fields = ['credit_limit', 'rating']
        date_fields = ['license_expiry']

        for field in text_fields:
            rep[field] = getattr(profile, field, '') if profile else ''

        for field in decimal_fields:
            rep[field] = getattr(profile, field, None) if profile else (0.0 if field == 'credit_limit' else None)

        for field in date_fields:
            rep[field] = getattr(profile, field, None) if profile else None

        return rep

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    # Identity fields  
    identity_type = serializers.ChoiceField(
        source='profile.identity_type',
        choices=UserProfile.IDENTITY_TYPE_CHOICES,
        required=False,
        allow_null=True
    )
    identity_number = serializers.CharField(
        source='profile.identity_number', 
        required=False, 
        allow_blank=True,
        max_length=50
    )
    profile_image = serializers.ImageField(
        source='profile.profile_image',
        required=False,
        allow_null=True
    )

    # Profile fields
    bio = serializers.CharField(source='profile.bio', required=False, allow_blank=True)
    company_name = serializers.CharField(source='profile.company_name', required=False, allow_blank=True)
    company_registration = serializers.CharField(source='profile.company_registration', required=False, allow_blank=True, allow_null=True)
    tax_id = serializers.CharField(source='profile.tax_id', required=False, allow_blank=True)
    address = serializers.CharField(source='profile.address', required=False, allow_blank=True)
    city = serializers.CharField(source='profile.city', required=False, allow_blank=True)
    state = serializers.CharField(source='profile.state', required=False, allow_blank=True)
    postal_code = serializers.CharField(source='profile.postal_code', required=False, allow_blank=True)
    country = serializers.CharField(source='profile.country', required=False, allow_blank=True)
    license_number = serializers.CharField(source='profile.license_number', required=False, allow_blank=True)
    license_expiry = serializers.DateField(source='profile.license_expiry', required=False, allow_null=True)
    preferred_locations = serializers.CharField(source='profile.preferred_locations', required=False, allow_blank=True)
    property_preferences = serializers.CharField(source='profile.property_preferences', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 'avatar',
            'identity_type', 'identity_number', 'profile_image',
            'bio', 'company_name', 'company_registration', 'tax_id', 'address',
            'city', 'state', 'postal_code', 'country', 'license_number',
            'license_expiry', 'preferred_locations', 'property_preferences',
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        profile, _ = UserProfile.objects.get_or_create(user=instance)

        profile_data = {}
        user_data = {}

        for field_name, value in validated_data.items():
            field_obj = self.fields.get(field_name)
            if field_obj and hasattr(field_obj, 'source') and field_obj.source and field_obj.source.startswith('profile.'):
                profile_field_name = field_obj.source.split('.')[-1]
                profile_data[profile_field_name] = value
            else:
                user_data[field_name] = value

        if user_data:
            for attr, value in user_data.items():
                setattr(instance, attr, value)
            instance.save(update_fields=user_data.keys())

        if profile_data:
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save(update_fields=profile_data.keys())

        return instance

class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'uuid', 'email', 'full_name', 'role_display', 'avatar', 'phone_number']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


# -------------------------------------------------------------------------
# Bank Account Serializers
# -------------------------------------------------------------------------

class BankAccountSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BankAccount
        fields = [
            'id', 'user', 'user_name', 'bank_account_name', 'bank_name', 
            'iban_number', 'account_number', 'swift_code', 'is_primary', 
            'is_verified', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email

class BankAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'bank_account_name', 'bank_name', 'iban_number', 'account_number', 
            'swift_code', 'is_primary', 'notes'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BankAccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'bank_account_name', 'bank_name', 'iban_number', 'account_number', 
            'swift_code', 'is_primary', 'notes'
        ]

class BankAccountBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'bank_account_name', 'bank_name', 'iban_number', 'is_primary']


# -------------------------------------------------------------------------
# Payment Serializers  
# -------------------------------------------------------------------------

class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    property_title = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()
    bank_account_name = serializers.SerializerMethodField()
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'user', 'user_name', 'amount', 'currency', 
            'payment_type', 'payment_type_display', 'status', 'status_display',
            'property_reference', 'property_title', 'tenant_reference', 'tenant_name',
            'payment_date', 'due_date', 'description', 'notes', 'bank_account',
            'bank_account_name', 'is_overdue', 'days_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payment_id', 'user', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def get_property_title(self, obj):
        return obj.property_reference.title if obj.property_reference else None
    
    def get_tenant_name(self, obj):
        return obj.tenant_reference.full_name if obj.tenant_reference else None
    
    def get_bank_account_name(self, obj):
        return obj.bank_account.bank_account_name if obj.bank_account else None

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'amount', 'currency', 'payment_type', 'status', 'property_reference', 
            'tenant_reference', 'payment_date', 'due_date', 'description', 
            'notes', 'bank_account'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'amount', 'currency', 'payment_type', 'status', 'property_reference', 
            'tenant_reference', 'payment_date', 'due_date', 'description', 
            'notes', 'bank_account'
        ]

class PaymentBriefSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'amount', 'currency', 'payment_type', 
            'payment_type_display', 'status', 'status_display', 'payment_date'
        ]