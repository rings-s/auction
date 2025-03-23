"""
URL configuration for Real Estate Auction System API
All endpoints are defined in a single file to match the consolidated views
"""
from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    # Auction endpoints
    path('auctions/', views.list_auctions, name='auction-list'),
    path('auctions/analytics/', views.auction_analytics, name='auction-analytics'),
    path('auctions/<uuid:auction_id>/', views.auction_detail, name='auction-detail'),
    path('auctions/create/', views.create_auction, name='auction-create'),
    path('auctions/<uuid:auction_id>/update/', views.update_auction, name='auction-update'),
    path('auctions/<uuid:auction_id>/delete/', views.delete_auction, name='auction-delete'),

    # Property endpoints
    path('properties/', views.list_properties, name='property-list'),
    path('properties/analytics/', views.property_analytics, name='property-analytics'),
    path('properties/create/', views.create_property, name='property-create'),
    path('properties/<uuid:property_id>/', views.property_detail, name='property-detail'),
    path('properties/<uuid:property_id>/update/', views.update_property, name='property-update'),
    path('properties/<uuid:property_id>/delete/', views.delete_property, name='property-delete'),
    path('properties/<uuid:property_id>/documents/', views.property_documents, name='property-documents'),
    path('properties/<uuid:property_id>/status/', views.change_property_status, name='property-status-change'),

    # Bid endpoints
    path('bids/', views.list_bids, name='bid-list'),
    path('bids/place/', views.place_bid, name='place-bid'),
    path('bids/analytics/', views.bid_analytics, name='bid-analytics'),

    # Contract endpoints
    path('contracts/', views.list_contracts, name='contract-list'),
    path('contracts/create/', views.create_contract, name='contract-create'),
    path('contracts/analytics/', views.contract_analytics, name='contract-analytics'),
    path('contracts/<uuid:contract_id>/', views.contract_detail, name='contract-detail'),
    path('contracts/<uuid:contract_id>/update/', views.update_contract, name='contract-update'),
    path('contracts/<uuid:contract_id>/sign/', views.sign_contract, name='contract-sign'),
    path('contracts/<uuid:contract_id>/payments/', views.create_contract_payment, name='contract-payment-create'),

    # Transaction endpoints
    path('transactions/', views.list_transactions, name='transaction-list'),
    path('transactions/create/', views.create_transaction, name='transaction-create'),
    path('transactions/analytics/', views.transaction_analytics, name='transaction-analytics'),
    path('transactions/<uuid:transaction_id>/', views.transaction_detail, name='transaction-detail'),
    path('transactions/<uuid:transaction_id>/update/', views.update_transaction, name='transaction-update'),
    path('transactions/<uuid:transaction_id>/process/', views.process_transaction, name='transaction-process'),


    path('dashboard/overview/', views.dashboard_overview, name='dashboard-overview'),
    path('dashboard/section/<str:section>/', views.dashboard_section, name='dashboard-section'),
    path('dashboard/chart/<str:chart_type>/', views.dashboard_chart, name='dashboard-chart'),

    # Quick statistics endpoints
    path('dashboard/quick-stats/', views.dashboard_quick_stats, name='dashboard-quick-stats'),
    path('dashboard/recent-activity/', views.dashboard_recent_activity, name='dashboard-recent-activity'),
]
