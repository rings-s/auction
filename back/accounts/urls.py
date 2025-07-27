from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

app_name = 'accounts'

# Authentication patterns
auth_patterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
]

# Token management patterns
token_patterns = [
    path('refresh/', views.TokenRefreshView.as_view(), name='refresh'),
    path('verify/', views.VerifyTokenView.as_view(), name='verify'),
    path('blacklist/', views.LogoutView.as_view(), name='blacklist'),  # Alternative endpoint name
]

# Password management patterns  
password_patterns = [
    path('change/', views.ChangePasswordView.as_view(), name='change'),
    path('reset/request/', views.PasswordResetRequestView.as_view(), name='reset-request'),
    path('reset/verify/', views.VerifyResetCodeView.as_view(), name='reset-verify'),
    path('reset/confirm/', views.ResetPasswordView.as_view(), name='reset-confirm'),
]

# Profile management patterns
profile_patterns = [
    path('', views.UserProfileView.as_view(), name='detail'),
    path('update/', views.UserProfileView.as_view(), name='update'),
    path('avatar/', views.UpdateAvatarView.as_view(), name='avatar'),
    path('<uuid:user_id>/', views.PublicProfileView.as_view(), name='public'),
    path('brief/', views.UserBriefView.as_view(), name='brief'),
]

# Admin management patterns (for superusers and administrators)
admin_patterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:user_id>/role/', views.UserRoleUpdateView.as_view(), name='user-role-update'),
    path('users/<uuid:user_id>/status/', views.UserStatusUpdateView.as_view(), name='user-status-update'),
    path('analytics/', views.UserAnalyticsView.as_view(), name='analytics'),
]

# Main URL patterns with organized structure
urlpatterns = [
    # Authentication endpoints
    path('auth/', include(auth_patterns)),
    
    # Token management endpoints
    path('token/', include(token_patterns)),
    
    # Password management endpoints
    path('password/', include(password_patterns)),
    
    # Profile management endpoints
    path('profile/', include(profile_patterns)),
    
    # Admin endpoints (requires appropriate permissions)
    path('admin/', include(admin_patterns)),
    
    # Legacy endpoints for backward compatibility
    path('register/', views.RegisterView.as_view(), name='register-legacy'),
    path('login/', views.LoginView.as_view(), name='login-legacy'),
    path('logout/', views.LogoutView.as_view(), name='logout-legacy'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email-legacy'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token-refresh-legacy'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify-legacy'),
    
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]