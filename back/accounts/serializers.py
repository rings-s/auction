from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from typing import Dict, Any, List
from .models import Role, UserProfile
from django.db import transaction

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for the Role model"""
    display_name = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Role
        fields = ('name', 'display_name', 'description')
        read_only_fields = ('name', 'display_name', 'description')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with role assignment
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.ChoiceField(
        choices=Role.ROLE_CHOICES,
        required=True,
        write_only=True,
        help_text="User's primary role in the auction platform"
    )

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'password_confirmation',
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'role'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs.get('password') != attrs.get('password_confirmation'):
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
            
        # Validate role
        role = attrs.get('role')
        if role == Role.ADMIN:
            raise serializers.ValidationError({
                "role": "Admin role cannot be assigned during registration."
            })

        # Remove password_confirmation from attrs after validation
        if 'password_confirmation' in attrs:
            attrs.pop('password_confirmation')
            
        return attrs
    
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> User:
        # Extract role data before creating user
        role_name = validated_data.pop('role')
        
        # Create user - UserProfile is automatically created by the model's save method
        user = User.objects.create_user(**validated_data)
        
        # Assign role using M2M relationship
        try:
            role, created = Role.objects.get_or_create(name=role_name)
            user.roles.add(role)
        except Exception as e:
            # Roll back transaction if something goes wrong
            user.delete()
            raise serializers.ValidationError({
                "role": f"Error assigning role: {str(e)}"
            })
            
        return user


class RoleInfoSerializer(serializers.Serializer):
    """Serializer for role information"""
    code = serializers.CharField()
    name = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving user profile information
    Combines User and UserProfile models
    """
    primary_role = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='profile.company_name', required=False, allow_null=True, allow_blank=True)
    company_registration = serializers.CharField(source='profile.company_registration', required=False, allow_null=True, allow_blank=True)
    tax_id = serializers.CharField(source='profile.tax_id', required=False, allow_null=True, allow_blank=True)
    address = serializers.CharField(source='profile.address', required=False, allow_null=True, allow_blank=True)
    bio = serializers.CharField(source='profile.bio', required=False, allow_null=True, allow_blank=True)
    credit_limit = serializers.DecimalField(source='profile.credit_limit', max_digits=15, decimal_places=2, read_only=True)
    rating = serializers.DecimalField(source='profile.rating', max_digits=3, decimal_places=2, read_only=True, allow_null=True)
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'avatar',
            'is_verified',
            'primary_role',
            'roles',
            'bio',
            'company_name',
            'company_registration',
            'tax_id',
            'address',
            'credit_limit',
            'rating',
            'date_joined',
            'is_active',
        )
        read_only_fields = (
            'id',
            'email',
            'is_verified',
            'credit_limit',
            'rating',
            'date_joined',
            'is_active',
            'primary_role',
            'roles',
        )
    
    def get_primary_role(self, obj):
        """Return the user's primary role information"""
        primary_role = obj.primary_role
        if primary_role:
            role_obj = next((r for r in obj.roles.all() if r.name == primary_role), None)
            if role_obj:
                return {
                    'code': role_obj.name,
                    'name': role_obj.get_name_display()
                }
        return None
    
    def get_roles(self, obj):
        """Return all roles assigned to the user"""
        roles_data = []
        for role in obj.roles.all():
            roles_data.append({
                'code': role.name,
                'name': role.get_name_display()
            })
        return roles_data
    
    def to_representation(self, instance):
        """Ensure profile data is handled even if profile doesn't exist"""
        rep = super().to_representation(instance)
        
        # Default values for profile fields if profile doesn't exist
        if not hasattr(instance, 'profile') or not instance.profile:
            profile_fields = ['bio', 'company_name', 'company_registration', 'tax_id', 'address']
            for field in profile_fields:
                rep[field] = ''
            rep['credit_limit'] = 0
            rep['rating'] = None
        
        return rep


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information
    """
    bio = serializers.CharField(write_only=True, required=False, allow_blank=True)
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    company_registration = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tax_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    roles = serializers.MultipleChoiceField(
        choices=Role.ROLE_CHOICES,
        required=False,
        write_only=True,
        help_text="User's roles in the auction platform"
    )
    
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'avatar',
            'bio',
            'company_name',
            'company_registration',
            'tax_id',
            'address',
            'roles',
        )
    
    def validate_roles(self, roles):
        """Validate roles to prevent unauthorized role assignment"""
        # Only admins can assign the admin role
        request = self.context.get('request')
        if Role.ADMIN in roles and (not request or not request.user.has_role(Role.ADMIN)):
            raise serializers.ValidationError(
                "Admin role can only be assigned by existing administrators."
            )
        return roles
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update user and related profile
        """
        # Extract and handle roles if provided
        if 'roles' in validated_data:
            role_names = validated_data.pop('roles')
            
            # Clear existing roles
            instance.roles.clear()
            
            # Add new roles
            for role_name in role_names:
                role, created = Role.objects.get_or_create(name=role_name)
                instance.roles.add(role)
        
        # Extract profile fields
        profile_fields = {
            'bio': validated_data.pop('bio', None),
            'company_name': validated_data.pop('company_name', None),
            'company_registration': validated_data.pop('company_registration', None),
            'tax_id': validated_data.pop('tax_id', None),
            'address': validated_data.pop('address', None),
        }
        
        # Remove None values (fields not provided in the update)
        profile_fields = {k: v for k, v in profile_fields.items() if v is not None}
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_fields:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_fields.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class UserRoleUpdateSerializer(serializers.Serializer):
    """
    Serializer for adding or removing roles from a user
    """
    action = serializers.ChoiceField(
        choices=['add', 'remove'],
        required=True,
        help_text="Whether to add or remove the role"
    )
    role = serializers.ChoiceField(
        choices=Role.ROLE_CHOICES,
        required=True,
        help_text="The role to add or remove"
    )
    
    def validate(self, attrs):
        action = attrs.get('action')
        role_name = attrs.get('role')
        
        # Only admins can manipulate the admin role
        if role_name == Role.ADMIN:
            request = self.context.get('request')
            if not request or not request.user.has_role(Role.ADMIN):
                raise serializers.ValidationError({
                    "role": "Admin role can only be modified by existing administrators."
                })
        
        return attrs