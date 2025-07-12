# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import logging

# Import from base app
from base.serializers import PropertySerializer, LocationSerializer
from accounts.serializers import UserProfileSerializer, UserBriefSerializer

# Import core models
from .models import (
    FinancialTransaction, PropertyExpense, 
    RentalProperty, Lease, MaintenanceRequest, Vendor, 
    ContractTemplate, Contract, PropertyAnalytics
)

logger = logging.getLogger(__name__)
User = get_user_model()

# Utility functions for serializers
def get_media_url(file_field, request=None):
    """
    Utility function to safely get media URL with proper error handling
    """
    if not file_field:
        return None
    
    try:
        if hasattr(file_field, 'url'):
            if request:
                return request.build_absolute_uri(file_field.url)
            return file_field.url
    except (ValueError, AttributeError) as e:
        logger.warning(f"Error getting media URL: {e}")
    
    return None

def get_file_size_safe(file_field):
    """
    Utility function to safely get file size
    """
    if not file_field:
        return 0
    
    try:
        if hasattr(file_field, 'size'):
            return file_field.size
        elif hasattr(file_field, 'path'):
            import os
            if os.path.exists(file_field.path):
                return os.path.getsize(file_field.path)
    except (ValueError, AttributeError, OSError) as e:
        logger.warning(f"Error getting file size: {e}")
    
    return 0


# -------------------------------------------------------------------------
# Financial Management Serializers
# -------------------------------------------------------------------------

class FinancialTransactionSerializer(serializers.ModelSerializer):
    """Financial transaction with nested user and property info"""
    payer_info = UserBriefSerializer(source='payer', read_only=True)
    payee_info = UserBriefSerializer(source='payee', read_only=True)
    property_info = serializers.SerializerMethodField()
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    # Write-only fields for creating transactions
    payer_id = serializers.IntegerField(write_only=True, required=False)
    payee_id = serializers.IntegerField(write_only=True, required=False)
    property_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = FinancialTransaction
        fields = '__all__'
        read_only_fields = ['transaction_id', 'paid_date', 'created_at', 'updated_at', 'deleted_at']

    def get_property_info(self, obj):
        """Get property information if exists"""
        if obj.related_property:
            try:
                return {
                    'id': obj.related_property.id,
                    'title': obj.related_property.title,
                    'slug': obj.related_property.slug,
                    'property_number': obj.related_property.property_number,
                }
            except AttributeError as e:
                logger.warning(f"Error accessing property info for transaction {obj.id}: {e}")
                return None
        return None

    def validate(self, data):
        """Validate transaction data"""
        # Ensure payer and payee are different
        payer_id = data.get('payer_id') or (data.get('payer').id if data.get('payer') else None)
        payee_id = data.get('payee_id') or (data.get('payee').id if data.get('payee') else None)
        
        if payer_id == payee_id:
            raise serializers.ValidationError(_("Payer and payee cannot be the same person"))
        
        # Validate due date is not in the past for new transactions
        if data.get('due_date') and data.get('due_date') < timezone.now().date():
            if not self.instance:  # Only for new transactions
                raise serializers.ValidationError({"due_date": _("Due date cannot be in the past")})
        
        return data

    def create(self, validated_data):
        """Create transaction with proper user assignment"""
        payer_id = validated_data.pop('payer_id', None)
        payee_id = validated_data.pop('payee_id', None)
        property_id = validated_data.pop('property_id', None)
        
        if payer_id:
            validated_data['payer'] = User.objects.get(id=payer_id)
        if payee_id:
            validated_data['payee'] = User.objects.get(id=payee_id)
        if property_id:
            from base.models import Property
            validated_data['related_property'] = Property.objects.get(id=property_id)
        
        return super().create(validated_data)

class PropertyExpenseSerializer(serializers.ModelSerializer):
    """Property expense with nested property and creator info"""
    property_info = serializers.SerializerMethodField()
    created_by_info = UserBriefSerializer(source='created_by', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    # Write-only fields
    property_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = PropertyExpense
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'deleted_at']

    def get_property_info(self, obj):
        """Get property information"""
        return {
            'id': obj.related_property.id,
            'title': obj.related_property.title,
            'slug': obj.related_property.slug,
            'property_number': obj.related_property.property_number,
        }

    def create(self, validated_data):
        """Create expense with property and user assignment"""
        property_id = validated_data.pop('property_id')
        from base.models import Property
        validated_data['related_property'] = Property.objects.get(id=property_id)
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

# -------------------------------------------------------------------------
# Rental Property Management Serializers
# -------------------------------------------------------------------------

class RentalPropertySerializer(serializers.ModelSerializer):
    """Rental property with nested base property info"""
    property_info = PropertySerializer(source='base_property', read_only=True)
    property_manager_info = UserBriefSerializer(source='property_manager', read_only=True)
    rental_type_display = serializers.CharField(source='get_rental_type_display', read_only=True)
    monthly_yield = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    # Current lease info
    current_lease = serializers.SerializerMethodField()
    
    # Write-only field for property assignment
    property_id = serializers.IntegerField(write_only=True, required=True)
    property_manager_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = RentalProperty
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'deleted_at']

    def get_current_lease(self, obj):
        """Get current active lease information"""
        try:
            current_lease = obj.leases.filter(status='active').first()
            if current_lease:
                return {
                    'id': current_lease.id,
                    'lease_number': current_lease.lease_number,
                    'tenant_name': f"{current_lease.tenant.first_name} {current_lease.tenant.last_name}",
                    'start_date': current_lease.start_date,
                    'end_date': current_lease.end_date,
                    'monthly_rent': current_lease.monthly_rent,
                    'days_remaining': current_lease.days_remaining,
                }
        except AttributeError as e:
            logger.warning(f"Error accessing current lease for rental property {obj.id}: {e}")
        return None

    def validate_property_id(self, value):
        """Validate property exists and not already a rental"""
        from base.models import Property
        try:
            property_obj = Property.objects.get(id=value)
            if hasattr(property_obj, 'rental_details') and not self.instance:
                raise serializers.ValidationError(_("This property is already configured as a rental property"))
            return value
        except Property.DoesNotExist:
            raise serializers.ValidationError(_("Property does not exist"))

    def create(self, validated_data):
        """Create rental property with proper relationships"""
        property_id = validated_data.pop('property_id')
        property_manager_id = validated_data.pop('property_manager_id', None)
        
        from base.models import Property
        validated_data['base_property'] = Property.objects.get(id=property_id)
        
        if property_manager_id:
            validated_data['property_manager'] = User.objects.get(id=property_manager_id)
        
        return super().create(validated_data)

class LeaseSerializer(serializers.ModelSerializer):
    """Lease agreement with nested rental property and parties info"""
    rental_property_info = serializers.SerializerMethodField()
    tenant_info = UserBriefSerializer(source='tenant', read_only=True)
    landlord_info = UserBriefSerializer(source='landlord', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Properties
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_fully_signed = serializers.SerializerMethodField()
    
    # Write-only fields
    rental_property_id = serializers.IntegerField(write_only=True, required=True)
    tenant_id = serializers.IntegerField(write_only=True, required=True)
    landlord_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Lease
        fields = '__all__'
        read_only_fields = ['lease_number', 'signing_date', 'created_at', 'updated_at', 'deleted_at']

    def get_rental_property_info(self, obj):
        """Get rental property information"""
        return {
            'id': obj.rental_property.id,
            'property_title': obj.rental_property.base_property.title,
            'property_address': obj.rental_property.base_property.address,
            'bedrooms': obj.rental_property.bedrooms,
            'bathrooms': obj.rental_property.bathrooms,
        }

    def get_is_fully_signed(self, obj):
        """Check if lease is fully signed"""
        return obj.tenant_signed and obj.landlord_signed

    def validate(self, data):
        """Validate lease data"""
        # Validate date range
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError({"end_date": _("End date must be after start date")})
        
        # Validate tenant and landlord are different
        tenant_id = data.get('tenant_id') or (data.get('tenant').id if data.get('tenant') else None)
        landlord_id = data.get('landlord_id') or (data.get('landlord').id if data.get('landlord') else None)
        
        if tenant_id == landlord_id:
            raise serializers.ValidationError(_("Tenant and landlord cannot be the same person"))
        
        return data

    def create(self, validated_data):
        """Create lease with proper relationships"""
        rental_property_id = validated_data.pop('rental_property_id')
        tenant_id = validated_data.pop('tenant_id')
        landlord_id = validated_data.pop('landlord_id')
        
        validated_data['rental_property'] = RentalProperty.objects.get(id=rental_property_id)
        validated_data['tenant'] = User.objects.get(id=tenant_id)
        validated_data['landlord'] = User.objects.get(id=landlord_id)
        
        return super().create(validated_data)

# -------------------------------------------------------------------------
# Maintenance Management Serializers
# -------------------------------------------------------------------------

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Maintenance request with nested relationships"""
    property_info = serializers.SerializerMethodField()
    requested_by_info = UserBriefSerializer(source='requested_by', read_only=True)
    assigned_to_info = UserBriefSerializer(source='assigned_to', read_only=True)
    
    # Display fields
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    # Calculated fields
    days_since_request = serializers.SerializerMethodField()
    
    # Write-only fields
    property_id = serializers.IntegerField(write_only=True, required=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = MaintenanceRequest
        fields = '__all__'
        read_only_fields = ['request_number', 'requested_by', 'requested_date', 'completed_date', 'created_at', 'updated_at', 'deleted_at']

    def get_property_info(self, obj):
        """Get property information"""
        return {
            'id': obj.related_property.id,
            'title': obj.related_property.title,
            'address': obj.related_property.address,
            'property_number': obj.related_property.property_number,
        }

    def get_days_since_request(self, obj):
        """Calculate days since request was made"""
        return (timezone.now().date() - obj.requested_date).days

    def create(self, validated_data):
        """Create maintenance request with proper relationships"""
        property_id = validated_data.pop('property_id')
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        
        from base.models import Property
        validated_data['related_property'] = Property.objects.get(id=property_id)
        validated_data['requested_by'] = self.context['request'].user
        
        if assigned_to_id:
            validated_data['assigned_to'] = User.objects.get(id=assigned_to_id)
        
        return super().create(validated_data)

class VendorSerializer(serializers.ModelSerializer):
    """Vendor with location and performance info"""
    vendor_type_display = serializers.CharField(source='get_vendor_type_display', read_only=True)
    recent_jobs = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'deleted_at']

    def get_recent_jobs(self, obj):
        """Get recent maintenance requests assigned to this vendor"""
        # Find users who might be associated with this vendor by matching company names
        # This is a simplified approach - in a real app you'd have a proper vendor-user relationship
        from django.db.models import Q
        recent_requests = MaintenanceRequest.objects.filter(
            Q(assigned_to__isnull=False)
        ).select_related('related_property', 'assigned_to').order_by('-created_at')[:3]
        
        return [
            {
                'id': req.id,
                'title': req.title,
                'property': req.related_property.title,
                'status': req.status,
                'created_at': req.created_at,
            }
            for req in recent_requests
        ]

# -------------------------------------------------------------------------
# Contract Management Serializers
# -------------------------------------------------------------------------

class ContractTemplateSerializer(serializers.ModelSerializer):
    """Contract template serializer"""
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    created_by_info = UserBriefSerializer(source='created_by', read_only=True)
    usage_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContractTemplate
        fields = '__all__'
        read_only_fields = ['created_by', 'usage_count', 'created_at', 'updated_at', 'deleted_at']

    def create(self, validated_data):
        """Create template with creator assignment"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ContractSerializer(serializers.ModelSerializer):
    """Contract with nested relationships"""
    template_info = serializers.SerializerMethodField()
    primary_party_info = UserBriefSerializer(source='primary_party', read_only=True)
    secondary_party_info = UserBriefSerializer(source='secondary_party', read_only=True)
    property_info = serializers.SerializerMethodField()
    lease_info = serializers.SerializerMethodField()
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_fully_signed = serializers.BooleanField(read_only=True)
    
    # Calculated fields
    days_until_expiration = serializers.SerializerMethodField()
    
    # Write-only fields
    template_id = serializers.IntegerField(write_only=True, required=False)
    primary_party_id = serializers.IntegerField(write_only=True, required=True)
    secondary_party_id = serializers.IntegerField(write_only=True, required=True)
    property_id = serializers.IntegerField(write_only=True, required=False)
    lease_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ['contract_number', 'signed_date', 'created_at', 'updated_at', 'deleted_at']

    def get_template_info(self, obj):
        """Get template information if exists"""
        if obj.template:
            return {
                'id': obj.template.id,
                'name': obj.template.name,
                'contract_type': obj.template.contract_type,
                'contract_type_display': obj.template.get_contract_type_display(),
            }
        return None

    def get_property_info(self, obj):
        """Get property information if exists"""
        if obj.related_property:
            return {
                'id': obj.related_property.id,
                'title': obj.related_property.title,
                'address': obj.related_property.address,
            }
        return None

    def get_lease_info(self, obj):
        """Get lease information if exists"""
        if obj.lease:
            return {
                'id': obj.lease.id,
                'lease_number': obj.lease.lease_number,
                'monthly_rent': obj.lease.monthly_rent,
            }
        return None

    def get_days_until_expiration(self, obj):
        """Calculate days until contract expiration"""
        if obj.expiration_date:
            today = timezone.now().date()
            if today <= obj.expiration_date:
                return (obj.expiration_date - today).days
        return None

    def create(self, validated_data):
        """Create contract with proper relationships"""
        # Extract foreign key IDs
        template_id = validated_data.pop('template_id', None)
        primary_party_id = validated_data.pop('primary_party_id')
        secondary_party_id = validated_data.pop('secondary_party_id')
        property_id = validated_data.pop('property_id', None)
        lease_id = validated_data.pop('lease_id', None)
        
        # Set relationships
        if template_id:
            validated_data['template'] = ContractTemplate.objects.get(id=template_id)
        
        validated_data['primary_party'] = User.objects.get(id=primary_party_id)
        validated_data['secondary_party'] = User.objects.get(id=secondary_party_id)
        
        if property_id:
            from base.models import Property
            validated_data['related_property'] = Property.objects.get(id=property_id)
        
        if lease_id:
            validated_data['lease'] = Lease.objects.get(id=lease_id)
        
        return super().create(validated_data)

# -------------------------------------------------------------------------
# Analytics Serializers
# -------------------------------------------------------------------------

class PropertyAnalyticsSerializer(serializers.ModelSerializer):
    """Property analytics with performance metrics"""
    property_info = serializers.SerializerMethodField()
    financial_summary = serializers.SerializerMethodField()
    performance_grade = serializers.SerializerMethodField()

    class Meta:
        model = PropertyAnalytics
        fields = '__all__'
        read_only_fields = ['base_property', 'last_calculated', 'created_at', 'updated_at', 'deleted_at']

    def get_property_info(self, obj):
        """Get property information"""
        return {
            'id': obj.base_property.id,
            'title': obj.base_property.title,
            'market_value': obj.base_property.market_value,
            'property_type': obj.base_property.property_type,
        }

    def get_financial_summary(self, obj):
        """Get financial performance summary"""
        return {
            'total_income_ytd': obj.total_income_ytd,
            'total_expenses_ytd': obj.total_expenses_ytd,
            'net_income_ytd': obj.net_income_ytd,
            'roi_percentage': obj.roi_percentage,
        }

    def get_performance_grade(self, obj):
        """Get performance grade based on score"""
        score = obj.performance_score
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

# -------------------------------------------------------------------------
# Dashboard Summary Serializers
# -------------------------------------------------------------------------

class PropertyDashboardSummarySerializer(serializers.Serializer):
    """Summary serializer for property dashboard"""
    total_properties = serializers.IntegerField()
    total_rental_properties = serializers.IntegerField()
    active_leases = serializers.IntegerField()
    pending_maintenance = serializers.IntegerField()
    overdue_payments = serializers.IntegerField()
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_roi = serializers.DecimalField(max_digits=5, decimal_places=2)

class FinancialSummarySerializer(serializers.Serializer):
    """Financial summary for dashboard"""
    total_income_ytd = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses_ytd = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_income_ytd = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_payments = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_comparison = serializers.DictField()
    top_expense_categories = serializers.ListField()

class PropertyManagementDashboardSerializer(serializers.Serializer):
    """Comprehensive property management dashboard serializer"""
    
    # Property overview
    total_properties = serializers.IntegerField()
    total_rental_income_ytd = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses_ytd = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_profit_ytd = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Occupancy metrics
    occupied_properties = serializers.IntegerField()
    vacant_properties = serializers.IntegerField()
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Maintenance metrics
    pending_maintenance = serializers.IntegerField()
    completed_maintenance_month = serializers.IntegerField()
    maintenance_cost_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Contract metrics
    expiring_leases_30_days = serializers.IntegerField()
    pending_contracts = serializers.IntegerField()
    
    # Recent activity - these will be list of dictionaries
    recent_transactions = FinancialTransactionSerializer(many=True, read_only=True)
    recent_maintenance = MaintenanceRequestSerializer(many=True, read_only=True)
    recent_leases = LeaseSerializer(many=True, read_only=True)
    
    # Summary data
    property_summary = PropertyDashboardSummarySerializer(read_only=True)
    financial_summary = FinancialSummarySerializer(read_only=True)

class MaintenanceStatsSerializer(serializers.Serializer):
    """Maintenance statistics for dashboard"""
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    in_progress_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    average_completion_time = serializers.DecimalField(max_digits=5, decimal_places=1)
    total_cost_ytd = serializers.DecimalField(max_digits=12, decimal_places=2)
    cost_by_category = serializers.DictField()
    urgency_breakdown = serializers.DictField()

class LeaseStatsSerializer(serializers.Serializer):
    """Lease statistics for dashboard"""
    total_leases = serializers.IntegerField()
    active_leases = serializers.IntegerField()
    expired_leases = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    average_lease_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    renewal_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    lease_status_breakdown = serializers.DictField()

class VendorStatsSerializer(serializers.Serializer):
    """Vendor statistics for dashboard"""
    total_vendors = serializers.IntegerField()
    active_vendors = serializers.IntegerField()
    preferred_vendors = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_paid_to_vendors = serializers.DecimalField(max_digits=12, decimal_places=2)
    vendor_type_breakdown = serializers.DictField()
    top_vendors_by_usage = serializers.ListField()

class ContractStatsSerializer(serializers.Serializer):
    """Contract statistics for dashboard"""
    total_contracts = serializers.IntegerField()
    draft_contracts = serializers.IntegerField()
    pending_contracts = serializers.IntegerField()
    signed_contracts = serializers.IntegerField()
    expiring_contracts = serializers.IntegerField()
    contract_type_breakdown = serializers.DictField()
    signing_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)