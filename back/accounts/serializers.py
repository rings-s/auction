from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import UserProfile
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
    role = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()

    # Basic profile fields
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

    # Enhanced profile fields
    identification_type = serializers.CharField(source='profile.identification_type', read_only=True, allow_null=True)
    identification_number = serializers.CharField(source='profile.identification_number', read_only=True, allow_null=True)
    identification_expiry = serializers.DateField(source='profile.identification_expiry', read_only=True, allow_null=True)
    tax_certification_number = serializers.CharField(source='profile.tax_certification_number', read_only=True, allow_null=True)
    bank_account_name = serializers.CharField(source='profile.bank_account_name', read_only=True, allow_null=True)
    bank_account_number = serializers.CharField(source='profile.bank_account_number', read_only=True, allow_null=True)
    bank_name = serializers.CharField(source='profile.bank_name', read_only=True, allow_null=True)
    digital_signature = serializers.CharField(source='profile.digital_signature', read_only=True, allow_null=True)
    signature_created_date = serializers.DateTimeField(source='profile.signature_created_date', read_only=True, allow_null=True)
    emergency_contact_name = serializers.CharField(source='profile.emergency_contact_name', read_only=True, allow_null=True)
    emergency_contact_phone = serializers.CharField(source='profile.emergency_contact_phone', read_only=True, allow_null=True)
    identity_verified = serializers.BooleanField(source='profile.identity_verified', read_only=True)
    bank_verified = serializers.BooleanField(source='profile.bank_verified', read_only=True)
    tax_verified = serializers.BooleanField(source='profile.tax_verified', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'uuid', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'avatar_url', 'is_verified', 'is_active', 'is_staff', 'date_joined', 'role', 'role_display',
            'verification_status',
            # Basic profile fields
            'bio', 'company_name', 'company_registration', 'tax_id', 'address', 'city', 'state',
            'postal_code', 'country', 'license_number', 'license_expiry', 'preferred_locations',
            'property_preferences', 'credit_limit', 'rating',
            # Enhanced profile fields
            'identification_type', 'identification_number', 'identification_expiry',
            'tax_certification_number', 'bank_account_name', 'bank_account_number', 'bank_name',
            'digital_signature', 'signature_created_date', 'emergency_contact_name', 'emergency_contact_phone',
            'identity_verified', 'bank_verified', 'tax_verified',
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

    def get_verification_status(self, obj):
        """Get verification status summary"""
        profile = getattr(obj, 'profile', None)
        if profile:
            return {
                'is_fully_verified': profile.is_fully_verified,
                'identity_verified': profile.identity_verified,
                'bank_verified': profile.bank_verified,
                'tax_verified': profile.tax_verified,
            }
        return {
            'is_fully_verified': False,
            'identity_verified': False,
            'bank_verified': False,
            'tax_verified': False,
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        profile = getattr(instance, 'profile', None)

        text_fields = [
            # Basic fields
            'bio', 'company_name', 'company_registration', 'tax_id', 'address',
            'city', 'state', 'postal_code', 'country', 'license_number',
            'preferred_locations', 'property_preferences',
            # Enhanced fields
            'identification_type', 'identification_number', 'tax_certification_number',
            'bank_account_name', 'bank_account_number', 'bank_name', 'digital_signature',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        decimal_fields = ['credit_limit', 'rating']
        date_fields = ['license_expiry', 'identification_expiry']
        datetime_fields = ['signature_created_date']
        boolean_fields = ['identity_verified', 'bank_verified', 'tax_verified']

        for field in text_fields:
            rep[field] = getattr(profile, field, '') if profile else ''

        for field in decimal_fields:
            rep[field] = getattr(profile, field, None) if profile else (0.0 if field == 'credit_limit' else None)

        for field in date_fields:
            rep[field] = getattr(profile, field, None) if profile else None

        for field in datetime_fields:
            rep[field] = getattr(profile, field, None) if profile else None

        for field in boolean_fields:
            rep[field] = getattr(profile, field, False) if profile else False

        return rep

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    # Basic profile fields
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

    # Enhanced profile fields
    identification_type = serializers.CharField(source='profile.identification_type', required=False, allow_blank=True)
    identification_number = serializers.CharField(source='profile.identification_number', required=False, allow_blank=True)
    identification_expiry = serializers.DateField(source='profile.identification_expiry', required=False, allow_null=True)
    tax_certification_number = serializers.CharField(source='profile.tax_certification_number', required=False, allow_blank=True)
    bank_account_name = serializers.CharField(source='profile.bank_account_name', required=False, allow_blank=True)
    bank_account_number = serializers.CharField(source='profile.bank_account_number', required=False, allow_blank=True)
    bank_name = serializers.CharField(source='profile.bank_name', required=False, allow_blank=True)
    digital_signature = serializers.CharField(source='profile.digital_signature', required=False, allow_blank=True)
    emergency_contact_name = serializers.CharField(source='profile.emergency_contact_name', required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(source='profile.emergency_contact_phone', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 'avatar',
            # Basic profile fields
            'bio', 'company_name', 'company_registration', 'tax_id', 'address',
            'city', 'state', 'postal_code', 'country', 'license_number',
            'license_expiry', 'preferred_locations', 'property_preferences',
            # Enhanced profile fields
            'identification_type', 'identification_number', 'identification_expiry',
            'tax_certification_number', 'bank_account_name', 'bank_account_number', 'bank_name',
            'digital_signature', 'emergency_contact_name', 'emergency_contact_phone',
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        from django.utils import timezone
        
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

        # Handle digital signature date update
        if 'digital_signature' in profile_data and profile_data['digital_signature']:
            profile_data['signature_created_date'] = timezone.now()

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