from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    # Category URLs
    path('categories/', views.category_list, name='category-list'),
    path('categories/create/', views.category_create, name='category-create'),
    path('categories/<str:slug>/', views.category_detail, name='category-detail'),
    path('categories/<str:slug>/update/', views.category_update, name='category-update'),
    path('categories/<str:slug>/delete/', views.category_delete, name='category-delete'),

    # Subcategory URLs
    path('subcategories/', views.subcategory_list, name='subcategory-list'),
    path('subcategories/create/', views.subcategory_create, name='subcategory-create'),
    path('subcategories/<str:slug>/', views.subcategory_detail, name='subcategory-detail'),

    # Auction URLs
    path('auctions/', views.auction_list, name='auction-list'),
    path('auctions/create/', views.auction_create, name='auction-create'),
    path('auctions/<uuid:auction_id>/', views.auction_detail, name='auction-detail'),
    path('auctions/<uuid:auction_id>/update/', views.auction_update, name='auction-update'),
    path('auctions/<uuid:auction_id>/delete/', views.auction_delete, name='auction-delete'),
    
    # Bid URLs
    path('auctions/<uuid:auction_id>/bids/', views.list_bids, name='list-bids'),
    path('auctions/<uuid:auction_id>/bids/create/', views.create_bid, name='create-bid'),
    path('user/bids/', views.user_bids, name='user-bids'),
    path('auctions/my-bids/', views.user_bids, name='my-bids'),

    
    # Document URLs
    path('auctions/<uuid:auction_id>/documents/', views.document_list, name='document-list'),
    path('auctions/<uuid:auction_id>/documents/upload/', views.document_upload, name='document-upload'),
    
    # Transaction URLs
    path('auctions/<uuid:auction_id>/transactions/create/', views.create_transaction, name='create-transaction'),
    path('transactions/', views.transaction_list, name='transaction-list'),
    
    # Search URLs
    path('search/', views.search, name='search'),
    
    # Dashboard URLs
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    
    # Message URLs
    path('messages/<str:room_id>/', views.message_history, name='message-history'),
    
    # Contract URLs
    path('contracts/create/', views.create_contract, name='create-contract'),
    path('contracts/', views.list_contracts, name='list-contracts'),
    
    # Payment Method URLs
    path('payment-methods/', views.list_payment_methods, name='list-payment-methods'),
    path('payment-methods/add/', views.add_payment_method, name='add-payment-method'),
    
    # Notification URLs
    path('notifications/', views.notification_list, name='notification-list'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    
    # Inspector URLs
    path('inspections/create/<uuid:auction_id>/', views.create_inspection_report, name='create-inspection'),
    path('documents/<uuid:document_id>/verify/', views.verify_document, name='verify-document'),

    # Legal URLs
    path('contracts/<uuid:contract_id>/review/', views.review_contract, name='review-contract'),
    path('transactions/<uuid:transaction_id>/dispute/', views.handle_dispute, name='handle-dispute'),
]