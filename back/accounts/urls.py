from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),

    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<uuid:user_id>/', views.PublicProfileView.as_view(), name='public-profile'),
    path('profile/avatar/', views.UpdateAvatarView.as_view(), name='update-avatar'),

    # Password management
    path('password/change/', views.ChangePasswordView.as_view(), name='change-password'),
    path('password/reset/request/', views.PasswordResetRequestView.as_view(), name='request-password-reset'),
    path('password/reset/verify/', views.VerifyResetCodeView.as_view(), name='verify-reset-token'),
    path('password/reset/confirm/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
]