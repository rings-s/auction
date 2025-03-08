from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    
    path('register/', views.register_user, name='register'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', views.verify_token, name='verify-token'),  # New route

    
    # Profile management
    path('profile/', views.user_profile, name='profile'),
    path('profile/<uuid:user_id>/', views.get_public_profile, name='public-profile'),


    # Password management
    path('password/', views.change_password, name='change-password'),
    path('password/reset/', views.request_password_reset, name='request-password-reset'),
    path('password/reset/verify/', views.verify_reset_code, name='verify-reset-token'),
    path('password/reset/confirm/', views.reset_password, name='reset-password'),
    
    # Role management - moved from base app
    path('roles/assign/<uuid:user_id>/', views.assign_role, name='assign-role'),
    path('dashboard/role/', views.role_dashboard, name='role-dashboard'),
]


"""
Authentication Endpoints:
-----------------------
POST /accounts/register/
    Register a new user
    Body: {
        "email": string,
        "password": string,
        "password_confirmation": string,
        "first_name": string,
        "last_name": string,
        "phone_number": string,
        "role": string
    }

POST /accounts/verify-email/
    Verify user's email address
    Body: {
        "email": string,
        "verification_token": string
    }

POST /accounts/login/
    Login user
    Body: {
        "email": string,
        "password": string
    }

POST /accounts/logout/
    Logout user (requires authentication)
    Body: {
        "refresh": string
    }

POST /accounts/token/refresh/
    Refresh access token
    Body: {
        "refresh": string
    }

Profile Management:
-----------------
GET /accounts/profile/
    Get current user's profile (requires authentication)

PUT/PATCH /accounts/profile/
    Update current user's profile (requires authentication)
    Body: {
        "first_name": string,
        "last_name": string,
        "phone_number": string,
        "company_name": string,
        "company_registration": string,
        "tax_id": string,
        "address": string
    }

GET /accounts/profile/<uuid:user_id>/
    Get public profile information for a user

Email Verification:
-----------------
POST /accounts/resend-verification/
    Resend verification email
    Body: {
        "email": string
    }

Password Management:
------------------
POST /accounts/password/
    Change password (requires authentication)
    Body: {
        "current_password": string,
        "new_password": string,
        "confirm_password": string
    }

POST /accounts/password/reset/
    Request password reset
    Body: {
        "email": string
    }

POST /accounts/password/reset/verify/
    Verify password reset token
    Body: {
        "email": string,
        "reset_token": string
    }

POST /accounts/password/reset/confirm/
    Reset password using token
    Body: {
        "email": string,
        "reset_token": string,
        "new_password": string,
        "confirm_password": string
    }
"""