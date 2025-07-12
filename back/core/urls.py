# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Financial Management
    path('transactions/', views.FinancialTransactionListCreateView.as_view(), name='transactions'),
    path('transactions/<uuid:transaction_id>/', views.FinancialTransactionDetailView.as_view(), name='transaction-detail'),
    path('expenses/', views.PropertyExpenseListCreateView.as_view(), name='expenses'),
    path('expenses/<int:pk>/', views.PropertyExpenseDetailView.as_view(), name='expense-detail'),
    
    # Rental Property Management
    path('rental-properties/', views.RentalPropertyListCreateView.as_view(), name='rental-properties'),
    path('rental-properties/<int:pk>/', views.RentalPropertyDetailView.as_view(), name='rental-property-detail'),
    path('leases/', views.LeaseListCreateView.as_view(), name='leases'),
    path('leases/<int:pk>/', views.LeaseDetailView.as_view(), name='lease-detail'),
    
    # Maintenance Management
    path('maintenance-requests/', views.MaintenanceRequestListCreateView.as_view(), name='maintenance-requests'),
    path('maintenance-requests/<int:pk>/', views.MaintenanceRequestDetailView.as_view(), name='maintenance-request-detail'),
    path('vendors/', views.VendorListCreateView.as_view(), name='vendors'),
    path('vendors/<int:pk>/', views.VendorDetailView.as_view(), name='vendor-detail'),
    
    # Contract Management
    path('contract-templates/', views.ContractTemplateListCreateView.as_view(), name='contract-templates'),
    path('contract-templates/<int:pk>/', views.ContractTemplateDetailView.as_view(), name='contract-template-detail'),
    path('contracts/', views.ContractListCreateView.as_view(), name='contracts'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract-detail'),
    
    # Analytics & Dashboard
    path('analytics/', views.PropertyAnalyticsView.as_view(), name='analytics'),
    path('analytics/<int:property_id>/', views.PropertyAnalyticsView.as_view(), name='property-analytics'),
    path('dashboard/', views.PropertyManagementDashboardView.as_view(), name='dashboard'),
]