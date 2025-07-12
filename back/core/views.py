# core/views.py
import logging
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework import permissions as drf_permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction, models
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
import django_filters.rest_framework as drf_django_filters
from datetime import timedelta
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.contrib.auth import get_user_model

# Import from base app
from base.views import BaseListCreateView, BaseDetailView
from base.permissions import IsVerifiedUser, IsAdminUser
from base.models import Property

# Import core models and serializers
from .models import (
    FinancialTransaction, PropertyExpense,
    RentalProperty, Lease, MaintenanceRequest, Vendor,
    ContractTemplate, Contract, PropertyAnalytics
)
from .serializers import (
    FinancialTransactionSerializer, PropertyExpenseSerializer,
    RentalPropertySerializer, LeaseSerializer, MaintenanceRequestSerializer, VendorSerializer,
    ContractTemplateSerializer, ContractSerializer, PropertyAnalyticsSerializer,
    PropertyManagementDashboardSerializer
)
from .permissions import (
    IsPropertyManagerOrOwner, IsLandlordOrPropertyManager, IsTenantOrLandlord,
    IsMaintenanceStaffOrManager, IsVendorOrManager
)
from .filters import (
    FinancialTransactionFilterSet, PropertyExpenseFilterSet, RentalPropertyFilterSet,
    LeaseFilterSet, MaintenanceRequestFilterSet, VendorFilterSet, ContractFilterSet
)

logger = logging.getLogger(__name__)
User = get_user_model()


# -------------------------------------------------------------------------
# Financial Management Views
# -------------------------------------------------------------------------

class FinancialTransactionListCreateView(BaseListCreateView):
    """Financial transaction list and create view"""
    serializer_class = FinancialTransactionSerializer
    filterset_class = FinancialTransactionFilterSet
    search_fields = ['description', 'reference_number', 'related_property__title']
    ordering_fields = ['created_at', 'due_date', 'amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get transactions based on user role"""
        user = self.request.user
        queryset = FinancialTransaction.objects.select_related(
            'payer', 'payee', 'related_property'
        ).order_by('-created_at')

        # Filter based on user role
        if user.role in ['landlord', 'property_manager']:
            # Landlords and property managers can see transactions for their properties
            return queryset.filter(
                Q(related_property__owner=user) | 
                Q(related_property__rental_details__property_manager=user) |
                Q(payer=user) | Q(payee=user)
            )
        elif user.role == 'tenant':
            # Tenants can only see their own transactions
            return queryset.filter(Q(payer=user) | Q(payee=user))
        elif user.is_superuser or user.role in ['appraiser', 'data_entry']:
            # Admin users can see all transactions
            return queryset
        else:
            # Regular users can only see their own transactions
            return queryset.filter(Q(payer=user) | Q(payee=user))

    def get_permissions(self):
        """Set permissions based on method"""
        return [drf_permissions.IsAuthenticated()]

class FinancialTransactionDetailView(BaseDetailView):
    """Financial transaction detail view"""
    serializer_class = FinancialTransactionSerializer
    lookup_field = 'transaction_id'

    def get_queryset(self):
        """Get transactions based on user permissions"""
        user = self.request.user
        queryset = FinancialTransaction.objects.select_related('payer', 'payee', 'related_property')

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(payer=user) | Q(payee=user) |
                Q(related_property__owner=user) |
                Q(related_property__rental_details__property_manager=user)
            )

    def get_permissions(self):
        """Set permissions for different operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsPropertyManagerOrOwner()]

class PropertyExpenseListCreateView(BaseListCreateView):
    """Property expense list and create view"""
    serializer_class = PropertyExpenseSerializer
    filterset_class = PropertyExpenseFilterSet
    search_fields = ['description', 'vendor_name', 'invoice_number', 'related_property__title']
    ordering_fields = ['expense_date', 'amount', 'category']
    ordering = ['-expense_date']

    def get_queryset(self):
        """Get expenses based on user permissions"""
        user = self.request.user
        queryset = PropertyExpense.objects.select_related('related_property', 'created_by')

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(related_property__owner=user) |
                Q(related_property__rental_details__property_manager=user) |
                Q(created_by=user)
            )

    def get_permissions(self):
        """Set permissions for expense management"""
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsPropertyManagerOrOwner()]
        return [drf_permissions.IsAuthenticated()]

class PropertyExpenseDetailView(BaseDetailView):
    """Property expense detail view"""
    serializer_class = PropertyExpenseSerializer

    def get_queryset(self):
        """Get expenses based on user permissions"""
        user = self.request.user
        queryset = PropertyExpense.objects.select_related('related_property', 'created_by')

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(related_property__owner=user) |
                Q(related_property__rental_details__property_manager=user) |
                Q(created_by=user)
            )

    def get_permissions(self):
        """Set permissions for expense operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsPropertyManagerOrOwner()]

# -------------------------------------------------------------------------
# Rental Property Management Views
# -------------------------------------------------------------------------

class RentalPropertyListCreateView(BaseListCreateView):
    """Rental property list and create view"""
    serializer_class = RentalPropertySerializer
    filterset_class = RentalPropertyFilterSet
    search_fields = ['base_property__title', 'base_property__address', 'base_property__location__city']
    ordering_fields = ['monthly_rent', 'created_at', 'available_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get rental properties based on user permissions"""
        user = self.request.user
        queryset = RentalProperty.objects.select_related('base_property', 'property_manager').prefetch_related('leases')

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        elif user.role in ['landlord', 'property_manager']:
            return queryset.filter(
                Q(base_property__owner=user) | Q(property_manager=user)
            )
        elif user.role == 'tenant':
            # Tenants can see available properties and their current rentals
            return queryset.filter(
                Q(is_currently_rented=False) | Q(leases__tenant=user, leases__status='active')
            ).distinct()
        else:
            # Public can see available rentals only
            return queryset.filter(base_property__is_published=True, is_currently_rented=False)

    def get_permissions(self):
        """Set permissions for rental property management"""
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsLandlordOrPropertyManager()]
        return [drf_permissions.AllowAny()]

class RentalPropertyDetailView(BaseDetailView):
    """Rental property detail view"""
    serializer_class = RentalPropertySerializer

    def get_queryset(self):
        """Get rental properties based on user permissions"""
        user = self.request.user
        queryset = RentalProperty.objects.select_related('base_property', 'property_manager')

        if not user.is_authenticated:
            return queryset.filter(base_property__is_published=True)
        elif user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(base_property__is_published=True) |
                Q(base_property__owner=user) |
                Q(property_manager=user) |
                Q(leases__tenant=user)
            ).distinct()

    def get_permissions(self):
        """Set permissions for rental property operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.AllowAny()]
        return [drf_permissions.IsAuthenticated(), IsLandlordOrPropertyManager()]

class LeaseListCreateView(BaseListCreateView):
    """Lease list and create view"""
    serializer_class = LeaseSerializer
    filterset_class = LeaseFilterSet
    search_fields = ['lease_number', 'tenant__first_name', 'tenant__last_name', 'rental_property__base_property__title']
    ordering_fields = ['start_date', 'end_date', 'monthly_rent', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get leases based on user permissions"""
        user = self.request.user
        queryset = Lease.objects.select_related(
            'rental_property__base_property', 'tenant', 'landlord'
        )

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        elif user.role in ['landlord', 'property_manager']:
            return queryset.filter(
                Q(landlord=user) |
                Q(rental_property__base_property__owner=user) |
                Q(rental_property__property_manager=user)
            )
        elif user.role == 'tenant':
            return queryset.filter(tenant=user)
        else:
            return queryset.none()

    def get_permissions(self):
        """Set permissions for lease management"""
        return [drf_permissions.IsAuthenticated(), IsTenantOrLandlord()]

class LeaseDetailView(BaseDetailView):
    """Lease detail view"""
    serializer_class = LeaseSerializer

    def get_queryset(self):
        """Get leases based on user permissions"""
        user = self.request.user
        queryset = Lease.objects.select_related('rental_property__property', 'tenant', 'landlord')

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(tenant=user) | Q(landlord=user) |
                Q(rental_property__base_property__owner=user) |
                Q(rental_property__property_manager=user)
            )

    def get_permissions(self):
        """Set permissions for lease operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsTenantOrLandlord()]

# -------------------------------------------------------------------------
# Maintenance Management Views
# -------------------------------------------------------------------------

class MaintenanceRequestListCreateView(BaseListCreateView):
    """Maintenance request list and create view"""
    serializer_class = MaintenanceRequestSerializer
    filterset_class = MaintenanceRequestFilterSet
    search_fields = ['title', 'description', 'request_number', 'related_property__title']
    ordering_fields = ['created_at', 'priority', 'status', 'scheduled_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get maintenance requests based on user permissions"""
        user = self.request.user
        queryset = MaintenanceRequest.objects.select_related(
            'related_property', 'requested_by', 'assigned_to'
        )

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        elif user.role in ['landlord', 'property_manager']:
            return queryset.filter(
                Q(related_property__owner=user) |
                Q(related_property__rental_details__property_manager=user)
            )
        elif user.role in ['maintenance_staff', 'vendor']:
            return queryset.filter(assigned_to=user)
        elif user.role == 'tenant':
            return queryset.filter(requested_by=user)
        else:
            return queryset.filter(requested_by=user)

    def get_permissions(self):
        """Set permissions for maintenance requests"""
        return [drf_permissions.IsAuthenticated()]

class MaintenanceRequestDetailView(BaseDetailView):
    """Maintenance request detail view"""
    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        """Get maintenance requests based on user permissions"""
        user = self.request.user
        queryset = MaintenanceRequest.objects.select_related('related_property', 'requested_by', 'assigned_to')

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(requested_by=user) | Q(assigned_to=user) |
                Q(related_property__owner=user) |
                Q(related_property__rental_details__property_manager=user)
            )

    def get_permissions(self):
        """Set permissions for maintenance request operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsMaintenanceStaffOrManager()]

class VendorListCreateView(BaseListCreateView):
    """Vendor list and create view"""
    serializer_class = VendorSerializer
    filterset_class = VendorFilterSet
    search_fields = ['company_name', 'contact_person', 'vendor_type']
    ordering_fields = ['company_name', 'rating', 'created_at']
    ordering = ['company_name']

    def get_queryset(self):
        """Get vendors based on user permissions"""
        user = self.request.user
        queryset = Vendor.objects.all()

        if user.is_superuser or user.role in ['appraiser', 'data_entry', 'landlord', 'property_manager']:
            return queryset.filter(is_active=True)
        else:
            return queryset.filter(is_active=True, is_preferred=True)

    def get_permissions(self):
        """Set permissions for vendor management"""
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsVendorOrManager()]
        return [drf_permissions.IsAuthenticated()]

class VendorDetailView(BaseDetailView):
    """Vendor detail view"""
    serializer_class = VendorSerializer

    def get_queryset(self):
        """Get vendors based on user permissions"""
        return Vendor.objects.all()

    def get_permissions(self):
        """Set permissions for vendor operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsVendorOrManager()]

# -------------------------------------------------------------------------
# Contract Management Views
# -------------------------------------------------------------------------

class ContractTemplateListCreateView(BaseListCreateView):
    """Contract template list and create view"""
    serializer_class = ContractTemplateSerializer
    search_fields = ['name', 'contract_type']
    ordering_fields = ['name', 'contract_type', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Get contract templates"""
        return ContractTemplate.objects.filter(is_active=True).select_related('created_by')

    def get_permissions(self):
        """Set permissions for contract template management"""
        if self.request.method == 'POST':
            return [drf_permissions.IsAuthenticated(), IsLandlordOrPropertyManager()]
        return [drf_permissions.IsAuthenticated()]

class ContractTemplateDetailView(BaseDetailView):
    """Contract template detail view"""
    serializer_class = ContractTemplateSerializer

    def get_queryset(self):
        """Get contract templates"""
        return ContractTemplate.objects.select_related('created_by')

    def get_permissions(self):
        """Set permissions for contract template operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsLandlordOrPropertyManager()]

class ContractListCreateView(BaseListCreateView):
    """Contract list and create view"""
    serializer_class = ContractSerializer
    filterset_class = ContractFilterSet
    search_fields = ['contract_number', 'title', 'primary_party__first_name', 'secondary_party__first_name']
    ordering_fields = ['effective_date', 'expiration_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get contracts based on user permissions"""
        user = self.request.user
        queryset = Contract.objects.select_related(
            'template', 'primary_party', 'secondary_party', 'related_property', 'lease'
        )

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(primary_party=user) | Q(secondary_party=user) |
                Q(related_property__owner=user) |
                Q(related_property__rental_details__property_manager=user)
            )

    def get_permissions(self):
        """Set permissions for contract management"""
        return [drf_permissions.IsAuthenticated()]

class ContractDetailView(BaseDetailView):
    """Contract detail view"""
    serializer_class = ContractSerializer

    def get_queryset(self):
        """Get contracts based on user permissions"""
        user = self.request.user
        queryset = Contract.objects.select_related('template', 'primary_party', 'secondary_party', 'related_property', 'lease')

        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            return queryset
        else:
            return queryset.filter(
                Q(primary_party=user) | Q(secondary_party=user) |
                Q(related_property__owner=user) |
                Q(related_property__rental_details__property_manager=user)
            )

    def get_permissions(self):
        """Set permissions for contract operations"""
        if self.request.method in SAFE_METHODS:
            return [drf_permissions.IsAuthenticated()]
        return [drf_permissions.IsAuthenticated(), IsPropertyManagerOrOwner()]

# -------------------------------------------------------------------------
# Analytics Views
# -------------------------------------------------------------------------

class PropertyAnalyticsView(APIView):
    """Property analytics view"""
    permission_classes = [drf_permissions.IsAuthenticated]

    def get(self, request, property_id=None):
        """Get property analytics"""
        user = request.user
        
        if property_id:
            # Get analytics for specific property
            try:
                analytics = PropertyAnalytics.objects.select_related('base_property').get(
                    base_property_id=property_id
                )
                
                # Check permissions
                if not (user.is_superuser or 
                       analytics.base_property.owner == user or
                       getattr(analytics.base_property.rental_details, 'property_manager', None) == user):
                    raise PermissionDenied("You don't have permission to view this property's analytics")
                
                # Recalculate metrics
                analytics.calculate_metrics()
                
                serializer = PropertyAnalyticsSerializer(analytics, context={'request': request})
                return Response(serializer.data)
                
            except PropertyAnalytics.DoesNotExist:
                return Response(
                    {'error': 'Analytics not found for this property'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Get analytics for all user's properties
            if user.is_superuser or user.role in ['appraiser', 'data_entry']:
                analytics = PropertyAnalytics.objects.select_related('base_property').all()
            else:
                analytics = PropertyAnalytics.objects.select_related('base_property').filter(
                    Q(base_property__owner=user) |
                    Q(base_property__rental_details__property_manager=user)
                )
            
            serializer = PropertyAnalyticsSerializer(analytics, many=True, context={'request': request})
            return Response(serializer.data)

class PropertyManagementDashboardView(APIView):
    """Property management dashboard view"""
    permission_classes = [drf_permissions.IsAuthenticated]

    def get(self, request):
        """Get dashboard data for property management"""
        user = request.user
        
        # Get user's properties based on role
        if user.is_superuser or user.role in ['appraiser', 'data_entry']:
            properties = Property.objects.all()
        else:
            properties = Property.objects.filter(
                Q(owner=user) | Q(rental_details__property_manager=user)
            )
        
        # Calculate dashboard metrics
        dashboard_data = self._calculate_dashboard_metrics(user, properties)
        
        serializer = PropertyManagementDashboardSerializer(dashboard_data)
        return Response(serializer.data)

    def _calculate_dashboard_metrics(self, user, properties):
        """Calculate comprehensive dashboard metrics"""
        from datetime import datetime, timedelta
        
        current_year = timezone.now().year
        current_month = timezone.now().month
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Property metrics
        rental_properties = RentalProperty.objects.filter(base_property__in=properties)
        occupied_properties = rental_properties.filter(is_currently_rented=True).count()
        vacant_properties = rental_properties.filter(is_currently_rented=False).count()
        total_properties = rental_properties.count()
        occupancy_rate = (occupied_properties / total_properties * 100) if total_properties > 0 else 0
        
        # Financial metrics
        transactions = FinancialTransaction.objects.filter(
            related_property__in=properties,
            created_at__year=current_year
        )
        income_transactions = transactions.filter(
            transaction_type__in=['rent_payment', 'security_deposit']
        )
        expense_transactions = transactions.filter(
            transaction_type__in=['maintenance_cost', 'utility_bill', 'insurance', 'tax_payment']
        )
        
        total_income = income_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = expense_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        net_profit = total_income - total_expenses
        
        # Maintenance metrics
        maintenance_requests = MaintenanceRequest.objects.filter(related_property__in=properties)
        pending_maintenance = maintenance_requests.filter(status__in=['submitted', 'in_progress']).count()
        completed_this_month = maintenance_requests.filter(
            status='completed',
            completed_date__year=current_year,
            completed_date__month=current_month
        ).count()
        
        maintenance_cost_month = maintenance_requests.filter(
            completed_date__year=current_year,
            completed_date__month=current_month
        ).aggregate(Sum('actual_cost'))['actual_cost__sum'] or 0
        
        # Contract metrics
        leases = Lease.objects.filter(rental_property__base_property__in=properties)
        expiring_leases = leases.filter(
            end_date__lte=timezone.now().date() + timedelta(days=30),
            status='active'
        ).count()
        
        contracts = Contract.objects.filter(related_property__in=properties)
        pending_contracts = contracts.filter(status__in=['draft', 'pending']).count()
        
        # Recent activity
        recent_transactions = FinancialTransaction.objects.filter(
            related_property__in=properties,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:10]
        
        recent_maintenance = MaintenanceRequest.objects.filter(
            related_property__in=properties,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:10]
        
        recent_leases = Lease.objects.filter(
            rental_property__base_property__in=properties,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:5]
        
        return {
            'total_properties': total_properties,
            'total_rental_income_ytd': total_income,
            'total_expenses_ytd': total_expenses,
            'net_profit_ytd': net_profit,
            'occupied_properties': occupied_properties,
            'vacant_properties': vacant_properties,
            'occupancy_rate': round(occupancy_rate, 2),
            'pending_maintenance': pending_maintenance,
            'completed_maintenance_month': completed_this_month,
            'maintenance_cost_month': maintenance_cost_month,
            'expiring_leases_30_days': expiring_leases,
            'pending_contracts': pending_contracts,
            'recent_transactions': recent_transactions,
            'recent_maintenance': recent_maintenance,
            'recent_leases': recent_leases,
        }