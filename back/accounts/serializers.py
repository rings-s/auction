from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import UserProfile
from django.db import transaction, IntegrityError
import logging
import re

logger = logging.getLogger(__name__)
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Enhanced user registration serializer with comprehensive validation."""
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password], 
        style={'input_type': 'password'},
        help_text=_("Password must be at least 8 characters long with a mix of letters, numbers, and symbols.")
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        help_text=_("Please confirm your password.")
    )
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES, 
        default='user', 
        required=False,
        help_text=_("Select your role in the system.")
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Phone number must be in format: '+999999999'. Max 15 digits allowed.")
        )],
        help_text=_("Enter your phone number with country code (optional).")
    )

    class Meta:
        model = User
        fields = (
            'email', 'password', 'confirm_password', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'role'
        )
        extra_kwargs = {
            'first_name': {
                'required': True, 
                'max_length': 150,
                'help_text': _("Enter your first name.")
            },
            'last_name': {
                'required': True, 
                'max_length': 150,
                'help_text': _("Enter your last name.")
            },
            'email': {
                'help_text': _("Enter a valid email address.")
            },
            'date_of_birth': {
                'required': False,
                'help_text': _("Enter your date of birth (optional).")
            },
        }

    def validate_email(self, value):
        """Enhanced email validation."""
        if not value:
            raise serializers.ValidationError(_("Email is required."))
        
        # Normalize email
        value = value.lower().strip()
        
        # Check for existing user
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        
        # Additional email format validation
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(value):
            raise serializers.ValidationError(_("Enter a valid email address."))
        
        return value

    def validate_first_name(self, value):
        """Validate first name."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("First name is required."))
        
        # Remove extra whitespace and validate length
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(_("First name must be at least 2 characters long."))
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", value):
            raise serializers.ValidationError(_("First name can only contain letters, spaces, hyphens, and apostrophes."))
        
        return value

    def validate_last_name(self, value):
        """Validate last name."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Last name is required."))
        
        # Remove extra whitespace and validate length
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(_("Last name must be at least 2 characters long."))
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", value):
            raise serializers.ValidationError(_("Last name can only contain letters, spaces, hyphens, and apostrophes."))
        
        return value

    def validate_phone_number(self, value):
        """Enhanced phone number validation."""
        if not value:
            return value
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', value)
        
        # Validate format
        if not re.match(r'^\+?1?\d{9,15}$', cleaned):
            raise serializers.ValidationError(
                _("Phone number must be in format: '+999999999'. Max 15 digits allowed.")
            )
        
        return cleaned

    def validate_date_of_birth(self, value):
        """Validate date of birth."""
        if value:
            from datetime import date, timedelta
            today = date.today()
            min_age = today - timedelta(days=18*365)  # 18 years
            max_age = today - timedelta(days=120*365)  # 120 years
            
            if value > today:
                raise serializers.ValidationError(_("Date of birth cannot be in the future."))
            
            if value > min_age:
                raise serializers.ValidationError(_("You must be at least 18 years old to register."))
            
            if value < max_age:
                raise serializers.ValidationError(_("Please enter a valid date of birth."))
        
        return value

    def validate_role(self, value):
        """Validate user role."""
        if value and value not in [choice[0] for choice in User.ROLE_CHOICES]:
            raise serializers.ValidationError(_("Invalid role selected."))
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password', None)
        
        # Password confirmation validation
        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": _("Passwords do not match.")
            })
        
        # Additional password strength validation
        if password:
            first_name = attrs.get('first_name', '').lower()
            last_name = attrs.get('last_name', '').lower()
            email = attrs.get('email', '').lower()
            
            # Check if password contains personal information
            if (first_name and first_name in password.lower()) or \
               (last_name and last_name in password.lower()) or \
               (email and email.split('@')[0] in password.lower()):
                raise serializers.ValidationError({
                    "password": _("Password cannot contain your personal information.")
                })
        
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create user with error handling and logging."""
        try:
            # Normalize email before creation
            validated_data['email'] = validated_data['email'].lower().strip()
            
            # Create user
            user = User.objects.create_user(**validated_data)
            
            # Log successful creation
            logger.info(
                f"User registration successful: {user.email} "
                f"(ID: {user.id}, Role: {user.role})"
            )
            
            return user
            
        except IntegrityError as e:
            logger.error(f"User registration failed - IntegrityError: {str(e)}")
            raise serializers.ValidationError({
                "email": _("A user with this email already exists.")
            })
        except Exception as e:
            logger.error(f"User registration failed - Unexpected error: {str(e)}")
            raise serializers.ValidationError({
                "non_field_errors": [_("An error occurred during registration. Please try again.")]
            })

class UserProfileSerializer(serializers.ModelSerializer):
    """Enhanced user profile serializer with comprehensive field handling."""
    
    # User basic fields
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    full_name = serializers.SerializerMethodField()
    phone_number = serializers.CharField(read_only=True)
    date_of_birth = serializers.DateField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    role_color = serializers.SerializerMethodField()
    
    # Image fields with error handling
    avatar_url = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()

    # Identity fields with safe access
    identity_type = serializers.SerializerMethodField()
    identity_type_display = serializers.SerializerMethodField()
    identity_number = serializers.SerializerMethodField()

    # Profile fields with safe access
    bio = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    company_registration = serializers.SerializerMethodField()
    tax_id = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    postal_code = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    credit_limit = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    license_number = serializers.SerializerMethodField()
    license_expiry = serializers.SerializerMethodField()
    preferred_locations = serializers.SerializerMethodField()
    property_preferences = serializers.SerializerMethodField()
    profile_created_at = serializers.SerializerMethodField()
    profile_updated_at = serializers.SerializerMethodField()

    # Permission fields
    is_property_professional = serializers.SerializerMethodField()
    is_admin_level = serializers.SerializerMethodField()
    is_financial_role = serializers.SerializerMethodField()
    can_manage_maintenance = serializers.SerializerMethodField()
    can_create_auctions = serializers.SerializerMethodField()
    can_manage_properties = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            # User fields
            'id', 'uuid', 'email', 'first_name', 'last_name', 'full_name', 'phone_number', 
            'date_of_birth', 'is_verified', 'is_active', 'is_staff', 'date_joined', 'role', 
            'role_display', 'role_color',
            
            # Image fields
            'avatar_url', 'profile_image_url',
            
            # Identity fields
            'identity_type', 'identity_type_display', 'identity_number',
            
            # Profile fields
            'bio', 'company_name', 'company_registration', 'tax_id', 'address', 'city', 
            'state', 'postal_code', 'country', 'license_number', 'license_expiry', 
            'preferred_locations', 'property_preferences', 'credit_limit', 'rating',
            'profile_created_at', 'profile_updated_at',
            
            # Permission fields
            'is_property_professional', 'is_admin_level', 'is_financial_role', 
            'can_manage_maintenance', 'can_create_auctions', 'can_manage_properties',
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        """Get user's full name."""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    def get_role_color(self, obj):
        """Get role color for UI display."""
        try:
            return obj.get_role_display_color()
        except Exception as e:
            logger.warning(f"Could not get role color for user {obj.id}: {e}")
            return '#6c757d'  # Default gray

    def get_avatar_url(self, obj):
        """Get avatar URL with error handling."""
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url') and request:
            try:
                return request.build_absolute_uri(obj.avatar.url)
            except Exception as e:
                logger.warning(f"Could not build avatar URL for user {obj.id}: {e}")
        return None

    def get_profile_image_url(self, obj):
        """Get profile image URL with error handling."""
        request = self.context.get('request')
        try:
            profile = getattr(obj, 'profile', None)
            if profile and profile.profile_image and hasattr(profile.profile_image, 'url') and request:
                return request.build_absolute_uri(profile.profile_image.url)
        except Exception as e:
            logger.warning(f"Could not build profile image URL for user {obj.id}: {e}")
        return None

    def _get_profile_field(self, obj, field_name, default=None):
        """Safely get profile field value."""
        try:
            profile = getattr(obj, 'profile', None)
            if profile:
                return getattr(profile, field_name, default)
        except Exception as e:
            logger.warning(f"Could not get profile field {field_name} for user {obj.id}: {e}")
        return default

    # Identity field methods
    def get_identity_type(self, obj):
        return self._get_profile_field(obj, 'identity_type', '')

    def get_identity_type_display(self, obj):
        """Get identity type display with error handling."""
        try:
            profile = getattr(obj, 'profile', None)
            if profile and profile.identity_type:
                return profile.get_identity_type_display()
        except Exception as e:
            logger.warning(f"Could not get identity type display for user {obj.id}: {e}")
        return None

    def get_identity_number(self, obj):
        return self._get_profile_field(obj, 'identity_number', '')

    # Profile field methods
    def get_bio(self, obj):
        return self._get_profile_field(obj, 'bio', '')

    def get_company_name(self, obj):
        return self._get_profile_field(obj, 'company_name', '')

    def get_company_registration(self, obj):
        return self._get_profile_field(obj, 'company_registration', '')

    def get_tax_id(self, obj):
        return self._get_profile_field(obj, 'tax_id', '')

    def get_address(self, obj):
        return self._get_profile_field(obj, 'address', '')

    def get_city(self, obj):
        return self._get_profile_field(obj, 'city', '')

    def get_state(self, obj):
        return self._get_profile_field(obj, 'state', '')

    def get_postal_code(self, obj):
        return self._get_profile_field(obj, 'postal_code', '')

    def get_country(self, obj):
        return self._get_profile_field(obj, 'country', '')

    def get_credit_limit(self, obj):
        return self._get_profile_field(obj, 'credit_limit', 0.00)

    def get_rating(self, obj):
        return self._get_profile_field(obj, 'rating', None)

    def get_license_number(self, obj):
        return self._get_profile_field(obj, 'license_number', '')

    def get_license_expiry(self, obj):
        return self._get_profile_field(obj, 'license_expiry', None)

    def get_preferred_locations(self, obj):
        return self._get_profile_field(obj, 'preferred_locations', '')

    def get_property_preferences(self, obj):
        return self._get_profile_field(obj, 'property_preferences', '')

    def get_profile_created_at(self, obj):
        return self._get_profile_field(obj, 'created_at', None)

    def get_profile_updated_at(self, obj):
        return self._get_profile_field(obj, 'updated_at', None)

    # Permission method implementations with error handling
    def get_is_property_professional(self, obj):
        try:
            return obj.is_property_professional()
        except Exception as e:
            logger.warning(f"Could not check property professional status for user {obj.id}: {e}")
            return False

    def get_is_admin_level(self, obj):
        try:
            return obj.is_admin_level()
        except Exception as e:
            logger.warning(f"Could not check admin level for user {obj.id}: {e}")
            return False

    def get_is_financial_role(self, obj):
        try:
            return obj.is_financial_role()
        except Exception as e:
            logger.warning(f"Could not check financial role for user {obj.id}: {e}")
            return False

    def get_can_manage_maintenance(self, obj):
        try:
            return obj.can_manage_maintenance()
        except Exception as e:
            logger.warning(f"Could not check maintenance management permission for user {obj.id}: {e}")
            return False

    def get_can_create_auctions(self, obj):
        try:
            return obj.can_create_auctions()
        except Exception as e:
            logger.warning(f"Could not check auction creation permission for user {obj.id}: {e}")
            return False

    def get_can_manage_properties(self, obj):
        try:
            return obj.can_manage_properties()
        except Exception as e:
            logger.warning(f"Could not check property management permission for user {obj.id}: {e}")
            return False

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Enhanced user profile update serializer with comprehensive validation."""
    
    # User fields with validation
    first_name = serializers.CharField(
        required=False, 
        max_length=150,
        help_text=_("Enter your first name.")
    )
    last_name = serializers.CharField(
        required=False, 
        max_length=150,
        help_text=_("Enter your last name.")
    )
    phone_number = serializers.CharField(
        required=False, 
        allow_blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Phone number must be in format: '+999999999'. Max 15 digits allowed.")
        )],
        help_text=_("Enter your phone number with country code.")
    )
    date_of_birth = serializers.DateField(
        required=False, 
        allow_null=True,
        help_text=_("Enter your date of birth.")
    )
    avatar = serializers.ImageField(
        required=False, 
        allow_null=True,
        help_text=_("Upload your avatar image (max 5MB).")
    )

    # Identity fields with validation
    identity_type = serializers.ChoiceField(
        source='profile.identity_type',
        choices=UserProfile.IDENTITY_TYPE_CHOICES,
        required=False,
        allow_null=True,
        help_text=_("Select your identity document type.")
    )
    identity_number = serializers.CharField(
        source='profile.identity_number', 
        required=False, 
        allow_blank=True,
        max_length=50,
        help_text=_("Enter your identity document number.")
    )
    profile_image = serializers.ImageField(
        source='profile.profile_image',
        required=False,
        allow_null=True,
        help_text=_("Upload your profile image (max 5MB).")
    )

    # Profile fields with validation
    bio = serializers.CharField(
        source='profile.bio', 
        required=False, 
        allow_blank=True,
        max_length=1000,
        help_text=_("Tell us about yourself (max 1000 characters).")
    )
    company_name = serializers.CharField(
        source='profile.company_name', 
        required=False, 
        allow_blank=True,
        max_length=200,
        help_text=_("Enter your company name.")
    )
    company_registration = serializers.CharField(
        source='profile.company_registration', 
        required=False, 
        allow_blank=True, 
        allow_null=True,
        max_length=100,
        help_text=_("Enter your company registration number.")
    )
    tax_id = serializers.CharField(
        source='profile.tax_id', 
        required=False, 
        allow_blank=True,
        max_length=50,
        help_text=_("Enter your tax identification number.")
    )
    address = serializers.CharField(
        source='profile.address', 
        required=False, 
        allow_blank=True,
        max_length=500,
        help_text=_("Enter your full address.")
    )
    city = serializers.CharField(
        source='profile.city', 
        required=False, 
        allow_blank=True,
        max_length=100,
        help_text=_("Enter your city.")
    )
    state = serializers.CharField(
        source='profile.state', 
        required=False, 
        allow_blank=True,
        max_length=100,
        help_text=_("Enter your state/province.")
    )
    postal_code = serializers.CharField(
        source='profile.postal_code', 
        required=False, 
        allow_blank=True,
        max_length=20,
        help_text=_("Enter your postal/ZIP code.")
    )
    country = serializers.CharField(
        source='profile.country', 
        required=False, 
        allow_blank=True,
        max_length=100,
        help_text=_("Enter your country.")
    )
    license_number = serializers.CharField(
        source='profile.license_number', 
        required=False, 
        allow_blank=True,
        max_length=50,
        help_text=_("Enter your professional license number.")
    )
    license_expiry = serializers.DateField(
        source='profile.license_expiry', 
        required=False, 
        allow_null=True,
        help_text=_("Enter your license expiry date.")
    )
    preferred_locations = serializers.CharField(
        source='profile.preferred_locations', 
        required=False, 
        allow_blank=True,
        max_length=1000,
        help_text=_("Enter your preferred property locations.")
    )
    property_preferences = serializers.CharField(
        source='profile.property_preferences', 
        required=False, 
        allow_blank=True,
        max_length=1000,
        help_text=_("Describe your property preferences.")
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 'avatar',
            'identity_type', 'identity_number', 'profile_image',
            'bio', 'company_name', 'company_registration', 'tax_id', 'address',
            'city', 'state', 'postal_code', 'country', 'license_number',
            'license_expiry', 'preferred_locations', 'property_preferences',
        )

    def validate_first_name(self, value):
        """Validate first name."""
        if value is not None:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError(_("First name must be at least 2 characters long."))
            if not re.match(r"^[a-zA-Z\s\-']+$", value):
                raise serializers.ValidationError(_("First name can only contain letters, spaces, hyphens, and apostrophes."))
        return value

    def validate_last_name(self, value):
        """Validate last name."""
        if value is not None:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError(_("Last name must be at least 2 characters long."))
            if not re.match(r"^[a-zA-Z\s\-']+$", value):
                raise serializers.ValidationError(_("Last name can only contain letters, spaces, hyphens, and apostrophes."))
        return value

    def validate_phone_number(self, value):
        """Enhanced phone number validation."""
        if value:
            # Remove all non-digit characters except +
            cleaned = re.sub(r'[^\d+]', '', value)
            if not re.match(r'^\+?1?\d{9,15}$', cleaned):
                raise serializers.ValidationError(
                    _("Phone number must be in format: '+999999999'. Max 15 digits allowed.")
                )
            return cleaned
        return value

    def validate_date_of_birth(self, value):
        """Validate date of birth."""
        if value:
            from datetime import date, timedelta
            today = date.today()
            min_age = today - timedelta(days=18*365)  # 18 years
            max_age = today - timedelta(days=120*365)  # 120 years
            
            if value > today:
                raise serializers.ValidationError(_("Date of birth cannot be in the future."))
            if value > min_age:
                raise serializers.ValidationError(_("You must be at least 18 years old."))
            if value < max_age:
                raise serializers.ValidationError(_("Please enter a valid date of birth."))
        return value

    def validate_avatar(self, value):
        """Validate avatar image."""
        if value:
            # Check file size (5MB limit)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(_("Avatar image must be smaller than 5MB."))
            
            # Check file type
            if not value.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                raise serializers.ValidationError(_("Avatar must be a valid image file (PNG, JPG, JPEG, GIF, or WebP)."))
        return value

    def validate_profile_image(self, value):
        """Validate profile image."""
        if value:
            # Check file size (5MB limit)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(_("Profile image must be smaller than 5MB."))
            
            # Check file type
            if not value.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                raise serializers.ValidationError(_("Profile image must be a valid image file (PNG, JPG, JPEG, GIF, or WebP)."))
        return value

    def validate_identity_number(self, value):
        """Validate identity number format."""
        if value and value.strip():
            value = value.strip()
            # Basic validation - adjust pattern based on your requirements
            if not re.match(r'^[A-Za-z0-9\-\s]{5,50}$', value):
                raise serializers.ValidationError(_("Identity number format is invalid."))
        return value

    def validate_company_registration(self, value):
        """Validate company registration number."""
        if value and value.strip():
            value = value.strip()
            # Check for duplicate company registration
            if UserProfile.objects.filter(
                company_registration=value
            ).exclude(user=self.instance).exists():
                raise serializers.ValidationError(_("A company with this registration number already exists."))
        return value

    def validate_postal_code(self, value):
        """Validate postal code format."""
        if value and value.strip():
            value = value.strip()
            # Basic postal code validation
            if not re.match(r'^[A-Za-z0-9\-\s]{3,20}$', value):
                raise serializers.ValidationError(_("Postal code format is invalid."))
        return value

    def validate_license_expiry(self, value):
        """Validate license expiry date."""
        if value:
            from datetime import date
            today = date.today()
            if value < today:
                raise serializers.ValidationError(_("License expiry date cannot be in the past."))
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update user profile with comprehensive error handling."""
        try:
            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(user=instance)
            
            if created:
                logger.info(f"Created new profile for user {instance.id}")

            profile_data = {}
            user_data = {}

            # Separate user and profile data
            for field_name, value in validated_data.items():
                field_obj = self.fields.get(field_name)
                if field_obj and hasattr(field_obj, 'source') and field_obj.source and field_obj.source.startswith('profile.'):
                    profile_field_name = field_obj.source.split('.')[-1]
                    profile_data[profile_field_name] = value
                else:
                    user_data[field_name] = value

            # Update user fields
            if user_data:
                for attr, value in user_data.items():
                    setattr(instance, attr, value)
                instance.save(update_fields=user_data.keys())
                logger.info(f"Updated user fields for user {instance.id}: {list(user_data.keys())}")

            # Update profile fields
            if profile_data:
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save(update_fields=profile_data.keys())
                logger.info(f"Updated profile fields for user {instance.id}: {list(profile_data.keys())}")

            return instance

        except IntegrityError as e:
            logger.error(f"Profile update failed - IntegrityError for user {instance.id}: {str(e)}")
            raise serializers.ValidationError({
                "non_field_errors": [_("A user with this information already exists.")]
            })
        except Exception as e:
            logger.error(f"Profile update failed - Unexpected error for user {instance.id}: {str(e)}")
            raise serializers.ValidationError({
                "non_field_errors": [_("An error occurred while updating your profile. Please try again.")]
            })

class UserBriefSerializer(serializers.ModelSerializer):
    """Lightweight user serializer for brief displays and listings."""
    
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    role_color = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'uuid', 'email', 'full_name', 'first_name', 'last_name',
            'role', 'role_display', 'role_color', 'avatar_url', 'phone_number', 
            'is_verified', 'is_active'
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        """Get user's full name with fallback."""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    def get_role_color(self, obj):
        """Get role color for UI display."""
        try:
            return obj.get_role_display_color()
        except Exception as e:
            logger.warning(f"Could not get role color for user {obj.id}: {e}")
            return '#6c757d'  # Default gray

    def get_avatar_url(self, obj):
        """Get avatar URL with error handling."""
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url') and request:
            try:
                return request.build_absolute_uri(obj.avatar.url)
            except Exception as e:
                logger.warning(f"Could not build avatar URL for user {obj.id}: {e}")
        return None


# Additional serializers for specific use cases

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change functionality."""
    
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_("Enter your current password.")
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text=_("Enter your new password.")
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_("Confirm your new password.")
    )

    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Current password is incorrect."))
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        
        if new_password != confirm_new_password:
            raise serializers.ValidationError({
                "confirm_new_password": _("New passwords do not match.")
            })
        
        # Check if new password is different from current
        current_password = attrs.get('current_password')
        if new_password == current_password:
            raise serializers.ValidationError({
                "new_password": _("New password must be different from your current password.")
            })
        
        return attrs

    def save(self):
        """Change the user's password."""
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save(update_fields=['password'])
        logger.info(f"Password changed successfully for user {user.id}")
        return user


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset functionality."""
    
    email = serializers.EmailField(
        required=True,
        help_text=_("Enter the email address associated with your account.")
    )

    def validate_email(self, value):
        """Validate email exists."""
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No account found with this email address."))
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    email = serializers.EmailField(required=True)
    reset_code = serializers.CharField(
        required=True,
        max_length=6,
        help_text=_("Enter the 6-digit reset code sent to your email.")
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text=_("Enter your new password.")
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_("Confirm your new password.")
    )

    def validate_email(self, value):
        """Validate email exists."""
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No account found with this email address."))
        return value

    def validate_reset_code(self, value):
        """Validate reset code format."""
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError(_("Reset code must be 6 digits."))
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        
        if new_password != confirm_new_password:
            raise serializers.ValidationError({
                "confirm_new_password": _("Passwords do not match.")
            })
        
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(
        required=True,
        max_length=6,
        help_text=_("Enter the 6-digit verification code sent to your email.")
    )

    def validate_email(self, value):
        """Validate email exists."""
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No account found with this email address."))
        return value

    def validate_verification_code(self, value):
        """Validate verification code format."""
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError(_("Verification code must be 6 digits."))
        return value


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user roles (admin only)."""
    
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        help_text=_("Select the new role for this user.")
    )

    class Meta:
        model = User
        fields = ['role']

    def validate_role(self, value):
        """Validate role change permissions."""
        request_user = self.context['request'].user
        
        # Only superusers and administrators can change roles
        if not (request_user.is_superuser or request_user.has_role('administrator')):
            raise serializers.ValidationError(_("You don't have permission to change user roles."))
        
        # Prevent non-superusers from creating administrators or superusers
        if not request_user.is_superuser and value in ['administrator']:
            raise serializers.ValidationError(_("Only superusers can assign administrator roles."))
        
        return value

    def update(self, instance, validated_data):
        """Update user role with logging."""
        old_role = instance.role
        new_role = validated_data['role']
        
        instance.role = new_role
        instance.save(update_fields=['role'])
        
        request_user = self.context['request'].user
        logger.info(
            f"User role updated: {instance.email} ({instance.id}) "
            f"from '{old_role}' to '{new_role}' by {request_user.email} ({request_user.id})"
        )
        
        return instance


