from django.urls import path
from . import views

# Arabic slug converter
class ArabicSlugConverter:
    regex = r'[-\w\u0600-\u06FF]+'
    
    def to_python(self, value):
        if not value:
            raise ValueError("Invalid slug value")
        return value
    
    def to_url(self, value):
        if not value:
            raise ValueError("Invalid slug value")
        return value

from django.urls import register_converter
register_converter(ArabicSlugConverter, 'arabicslug')

urlpatterns = [
    # Locations
    path('locations/', views.LocationListCreateView.as_view(), name='locations'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location'),
    
    # Media
    path('media/', views.MediaListCreateView.as_view(), name='media'),
    path('media/<int:pk>/', views.MediaDetailView.as_view(), name='media-detail'),
    
    # Properties
    path('properties/', views.PropertyListCreateView.as_view(), name='properties'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property'),
    path('properties/<arabicslug:slug>/', views.PropertySlugDetailView.as_view(), name='property-by-slug'),
    path('properties/<int:property_id>/contact/', views.PropertyOwnerContactView.as_view(), name='property-contact'),

    
    # Rooms
    path('rooms/', views.RoomListCreateView.as_view(), name='rooms'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room'),
    
    # Auctions
    path('auctions/', views.AuctionListCreateView.as_view(), name='auctions'),
    path('auctions/<int:pk>/', views.AuctionDetailView.as_view(), name='auction'),
    path('auctions/<int:auction_id>/status/', views.AuctionStatusView.as_view(), name='auction-status'),
    path('auctions/<arabicslug:slug>/', views.AuctionSlugDetailView.as_view(), name='auction-by-slug'),
    
    # Bids
    path('bids/', views.BidListCreateView.as_view(), name='bids'),
    path('bids/<int:pk>/', views.BidDetailView.as_view(), name='bid'),




    # Messages
    path('messages/', views.MessageListCreateView.as_view(), name='messages'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('messages/<int:pk>/reply/', views.MessageReplyView.as_view(), name='message-reply'),
    path('messages/thread/<uuid:thread_id>/', views.MessageReplyView.as_view(), name='message-thread'),
    path('messages/stats/', views.MessageStatsView.as_view(), name='message-stats'),


    # Dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('dashboard/system/', views.SystemDashboardView.as_view(), name='system-dashboard'),
    path('dashboard/activity/', views.RecentActivityView.as_view(), name='dashboard-activity'),
    path('dashboard/properties/', views.DashboardPropertiesView.as_view(), name='dashboard-properties'),
    path('dashboard/auctions/', views.DashboardAuctionsView.as_view(), name='dashboard-auctions'),
    path('dashboard/bids/', views.DashboardBidsView.as_view(), name='dashboard-bids'),
    
    # Property Management Dashboard
    path('dashboard/rental-properties/', views.DashboardRentalPropertiesView.as_view(), name='dashboard-rental-properties'),
    path('dashboard/tenants/', views.DashboardTenantsView.as_view(), name='dashboard-tenants'),
    path('dashboard/leases/', views.DashboardLeasesView.as_view(), name='dashboard-leases'),
    path('dashboard/maintenance/', views.DashboardMaintenanceView.as_view(), name='dashboard-maintenance'),
    path('dashboard/expenses/', views.DashboardExpensesView.as_view(), name='dashboard-expenses'),
    path('dashboard/property-management-analytics/', views.PropertyManagementAnalyticsView.as_view(), name='dashboard-property-analytics'),
    
    # Property Management - Rental Properties
    path('rental-properties/', views.RentalPropertyListCreateView.as_view(), name='rental-properties'),
    path('rental-properties/<int:pk>/', views.RentalPropertyDetailView.as_view(), name='rental-property'),
    
    # Property Management - Tenants
    path('tenants/', views.TenantListCreateView.as_view(), name='tenants'),
    path('tenants/<int:pk>/', views.TenantDetailView.as_view(), name='tenant'),
    
    # Property Management - Leases
    path('leases/', views.LeaseListCreateView.as_view(), name='leases'),
    path('leases/<int:pk>/', views.LeaseDetailView.as_view(), name='lease'),
    
    # Property Management - Maintenance
    path('maintenance/categories/', views.MaintenanceCategoryListCreateView.as_view(), name='maintenance-categories'),
    path('maintenance/categories/<int:pk>/', views.MaintenanceCategoryDetailView.as_view(), name='maintenance-category'),
    path('maintenance/requests/', views.MaintenanceRequestListCreateView.as_view(), name='maintenance-requests'),
    path('maintenance/requests/<int:pk>/', views.MaintenanceRequestDetailView.as_view(), name='maintenance-request'),
    
    # Property Management - Expenses
    path('expenses/categories/', views.ExpenseCategoryListCreateView.as_view(), name='expense-categories'),
    path('expenses/categories/<int:pk>/', views.ExpenseCategoryDetailView.as_view(), name='expense-category'),
    path('expenses/', views.ExpenseListCreateView.as_view(), name='expenses'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense'),
    
    # Property Management - Analytics & Reports
    path('analytics/', views.PropertyAnalyticsView.as_view(), name='property-analytics'),
    path('analytics/<int:property_id>/', views.PropertyAnalyticsView.as_view(), name='property-analytics-detail'),
    path('reports/', views.ReportListView.as_view(), name='reports'),
    path('reports/generate/', views.ReportGenerationView.as_view(), name='generate-report'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report'),
    
    # Enhanced Analytics Views with Heat Maps and Bar Charts
    path('analytics/advanced/', views.AdvancedPropertyAnalyticsView.as_view(), name='advanced-property-analytics'),
    path('analytics/workers/', views.WorkerAnalyticsView.as_view(), name='worker-analytics'),
    path('analytics/payments/', views.PaymentAnalyticsView.as_view(), name='payment-analytics'),
    
    # Worker Management
    path('workers/categories/', views.WorkerCategoryListCreateView.as_view(), name='worker-categories'),
    path('workers/categories/<int:pk>/', views.WorkerCategoryDetailView.as_view(), name='worker-category'),
    path('workers/', views.WorkerListCreateView.as_view(), name='workers'),
    path('workers/<int:pk>/', views.WorkerDetailView.as_view(), name='worker'),
    
]