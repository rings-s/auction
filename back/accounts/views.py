from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.conf import settings
from datetime import timedelta
import random
import logging

from .models import UserProfile, Role
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRoleUpdateSerializer
)
from .utils import (
    send_verification_email, 
    send_password_reset_email, 
    send_role_assignment_email,
    EmailRateLimitExceeded
)
from base.decorators import role_required, debug_request
from base.models import Transaction, Auction, Document, Contract, Bid

User = get_user_model()
logger = logging.getLogger(__name__)

def create_response(data=None, message=None, error=None, error_code=None, status_code=status.HTTP_200_OK):
    """
    Standardized response creator for API endpoints
    """
    response_data = {"status": "error" if error else "success"}
    
    if data:
        response_data.update(data)
    if message:
        response_data["message"] = message
    if error:
        response_data["error"] = error
    if error_code:
        response_data["code"] = error_code
        
    return Response(response_data, status=status_code)

@api_view(['POST'])
@permission_classes([AllowAny])
@debug_request
def register_user(request):
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return create_response(
                error=serializer.errors,
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user = serializer.save()
            
            # Generate 6-digit verification code
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user.verification_code = verification_code
            user.verification_code_created = timezone.now()
            user.save()
            
            # For development - always log verification code
            if getattr(settings, 'DEBUG', False):
                logger.info(f"DEVELOPMENT MODE - Verification code for {user.email}: {verification_code}")
            
            try:
                context = {
                    'user_name': f"{user.first_name} {user.last_name}",
                    'verification_code': verification_code,
                    'expiry_hours': 24
                }
                send_verification_email(user.email, verification_code, context)
                
            except EmailRateLimitExceeded as e:
                logger.warning(f"Rate limit exceeded for verification email to {user.email}")
                return create_response(
                    error=str(e),
                    error_code="rate_limit_exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )
            except Exception as email_error:
                logger.error(f"Email sending failed: {str(email_error)}")
                if not getattr(settings, 'DEBUG', False):
                    raise ValidationError("Failed to send verification email. Please try again later.")

        return create_response(
            message="Registration successful. Please check your email for verification.",
            status_code=status.HTTP_201_CREATED
        )
        
    except ValidationError as ve:
        return create_response(
            error=str(ve),
            error_code="email_sending_failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return create_response(
            error="Registration failed. Please try again later.",
            error_code="registration_failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    
    
  
@api_view(['POST'])
@permission_classes([AllowAny])
@debug_request
def verify_email(request):
    """
    Verify user email with provided verification code
    """
    try:
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        
        if not all([email, verification_code]):
            return create_response(
                error="Email and verification code are required",
                error_code="missing_fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(
                email=email,
                verification_code=verification_code,
                verification_code_created__gt=timezone.now() - timedelta(hours=24)
            )
            
            if timezone.now() > user.verification_code_created + timedelta(hours=24):
                return create_response(
                    error="Verification code has expired",
                    error_code="verification_code_expired",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            user.is_verified = True
            user.verification_code = ""
            user.verification_code_created = None
            user.save()
            
            # Generate tokens for automatic login
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['user_id'] = str(user.id)
            
            return create_response({
                'message': "Email verified successfully",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserProfileSerializer(user).data
            })
            
        except User.DoesNotExist:
            return create_response(
                error="Invalid or expired verification code",
                error_code="invalid_code",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        return create_response(
            error="An unexpected error occurred",
            error_code="server_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )






@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify the validity of the access token.
    This endpoint checks if the token is valid and belongs to the authenticated user.
    """
    try:
        # If the user is authenticated, the token is valid
        return Response(
            {
                "status": "success",
                "message": "Token is valid",
                "user": {
                    "email": request.user.email,
                    "user_id": str(request.user.id),
                },
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return Response(
            {
                "status": "error",
                "error": "An unexpected error occurred during token verification",
                "error_code": "token_verification_error",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@debug_request
def user_profile(request):
    """
    Handle user profile operations (get, update)
    """
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return create_response({"user": serializer.data})

    try:
        # Check for immutable fields
        immutable_fields = {'email', 'is_verified', 'role'}
        if any(field in request.data for field in immutable_fields):
            return create_response(
                error="Cannot update protected fields",
                error_code="immutable_field_update",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )

        if not serializer.is_valid():
            return create_response(
                error=serializer.errors,
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return create_response({
            "user": UserProfileSerializer(request.user).data,
            "message": "Profile updated successfully"
        })

    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return create_response(
            error="Profile update failed",
            error_code="profile_update_failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
@debug_request
def get_public_profile(request, user_id):
    """
    Get public profile information for a user
    """
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Only return public information
        serializer = UserProfileSerializer(user, context={'request': request})
        
        # Filter out sensitive information
        data = serializer.data
        sensitive_fields = ['email', 'is_verified', 'reset_code', 'verification_code']
        for field in sensitive_fields:
            if field in data:
                del data[field]
        
        return create_response({"user": data})
        
    except Exception as e:
        logger.error(f"Error fetching public profile: {str(e)}")
        return create_response(
            error="An error occurred while fetching the profile",
            error_code="profile_fetch_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
@debug_request
def verify_reset_code(request):
    """
    Verify the reset code validity before allowing password reset
    """
    try:
        email = request.data.get('email')
        reset_code = request.data.get('reset_code')
        
        if not all([email, reset_code]):
            return create_response(
                error="Email and reset code are required",
                error_code="missing_fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(
                email=email,
                reset_code=reset_code,
                reset_code_created__gt=timezone.now() - timedelta(hours=1)
            )
            
            if timezone.now() > user.reset_code_created + timedelta(hours=1):
                return create_response(
                    error="Reset code has expired",
                    error_code="reset_code_expired",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            return create_response(message="Reset code is valid")
            
        except User.DoesNotExist:
            return create_response(
                error="Invalid or expired reset code",
                error_code="invalid_code",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Reset code verification error: {str(e)}")
        return create_response(
            error="An unexpected error occurred",
            error_code="server_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
@debug_request
def request_password_reset(request):
    """
    Handle password reset request and send reset code via email
    """
    try:
        email = request.data.get('email', '').lower().strip()
        if not email:
            return create_response(
                error="Email is required",
                error_code="email_required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            
            # Check for recent reset requests
            if user.reset_code_created and timezone.now() - user.reset_code_created < timedelta(minutes=5):
                return create_response(
                    error="Please wait 5 minutes before requesting another reset",
                    error_code="rate_limit",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Generate reset code (6-digit)
            reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user.reset_code = reset_code
            user.reset_code_created = timezone.now()
            user.save()
            
            # For development - always log reset code
            if getattr(settings, 'DEBUG', False):
                logger.info(f"DEVELOPMENT MODE - Reset code for {user.email}: {reset_code}")
            
            try:
                context = {
                    'user_name': f"{user.first_name} {user.last_name}",
                    'reset_code': reset_code,
                    'expiry_hours': 1
                }
                send_password_reset_email(user.email, reset_code, context)
                
                return create_response(
                    message="Password reset instructions have been sent to your email"
                )
                
            except EmailRateLimitExceeded as e:
                logger.warning(f"Rate limit exceeded for password reset email to {user.email}")
                return create_response(
                    error=str(e),
                    error_code="rate_limit_exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )
            except Exception as email_error:
                logger.error(f"Failed to send password reset email: {str(email_error)}")
                if getattr(settings, 'DEBUG', False):
                    return create_response(
                        message="Password reset code has been generated. Check server logs."
                    )
                return create_response(
                    error="Failed to send reset email",
                    error_code="email_sending_failed",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except User.DoesNotExist:
            # Return success message even if email doesn't exist (security)
            return create_response(
                message="If an account exists with this email, password reset instructions have been sent"
            )
            
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return create_response(
            error="An unexpected error occurred",
            error_code="server_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
@debug_request
def reset_password(request):
    """
    Reset user password using reset code
    """
    try:
        email = request.data.get('email')
        reset_code = request.data.get('reset_code')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([email, reset_code, new_password, confirm_password]):
            return create_response(
                error="All fields are required",
                error_code="missing_fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return create_response(
                error="Passwords do not match",
                error_code="password_mismatch",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            user = User.objects.get(
                email=email,
                reset_code=reset_code,
                reset_code_created__gt=timezone.now() - timedelta(hours=1)
            )
            
            if timezone.now() > user.reset_code_created + timedelta(hours=1):
                return create_response(
                    error="Reset code has expired",
                    error_code="reset_code_expired",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate new password
            try:
                validate_password(new_password, user)
            except ValidationError as e:
                return create_response(
                    error=str(e),
                    error_code="invalid_password",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # Update password and clear reset code
            user.set_password(new_password)
            user.reset_code = ""
            user.reset_code_created = None
            user.save()
            
            # Generate new tokens for automatic login
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['user_id'] = str(user.id)
            
            return create_response({
                'message': "Password reset successfully",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserProfileSerializer(user).data
            })
            
        except User.DoesNotExist:
            return create_response(
                error="Invalid or expired reset code",
                error_code="invalid_code",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return create_response(
            error="An unexpected error occurred",
            error_code="server_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def change_password(request):
    """
    Change password for authenticated user
    """
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            return create_response(
                error="All fields are required",
                error_code="missing_fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return create_response(
                error="New passwords do not match",
                error_code="password_mismatch",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if not user.check_password(current_password):
            return create_response(
                error="Current password is incorrect",
                error_code="invalid_password",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return create_response(
                error=str(e),
                error_code="invalid_new_password",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        user.set_password(new_password)
        user.save()

        # Generate new tokens
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['user_id'] = str(user.id)

        return create_response({
            'message': "Password changed successfully",
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })

    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return create_response(
            error="An unexpected error occurred",
            error_code="server_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@role_required([Role.ADMIN])
@debug_request
def assign_role(request, user_id):
    """
    Assign roles to a user (admin only).
    """
    try:
        user = get_object_or_404(User, id=user_id)
        role_names = request.data.get('roles', [])
        
        # Validate role names
        valid_roles = set([choice[0] for choice in Role.ROLE_CHOICES])
        for role_name in role_names:
            if role_name not in valid_roles:
                return Response(
                    {'error': f'Invalid role: {role_name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get current roles for notification
        current_roles = list(user.roles.values_list('name', flat=True))
        
        # Get or create the roles
        roles = []
        for role_name in role_names:
            role, created = Role.objects.get_or_create(name=role_name)
            roles.append(role)
        
        # Replace user's current roles
        user.roles.set(roles)
        
        # Prepare role display names for notification
        role_display_names = [role.get_name_display() for role in roles]
        
        # Determine added and removed roles
        added_roles = [role for role in role_names if role not in current_roles]
        removed_roles = [role for role in current_roles if role not in role_names]
        
        # Send notification email if roles changed
        if added_roles or removed_roles:
            try:
                send_role_assignment_email(
                    user.email, 
                    role_display_names,
                    [Role.objects.get(name=role).get_name_display() for role in added_roles], 
                    [Role.objects.get(name=role).get_name_display() for role in removed_roles]
                )
            except Exception as email_error:
                logger.warning(f"Failed to send role assignment email: {str(email_error)}")
        
        return Response({
            'user_id': user.id,
            'roles': role_names
        })
    except Exception as e:
        logger.error(f"Error in assign_role view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@login_required
@debug_request
def role_dashboard(request):
    """
    Get dashboard data based on user's role.
    """
    try:
        user = request.user
        user_roles = user.roles.values_list('name', flat=True)
        
        dashboard_data = {}
        
        # Admin dashboard
        if Role.ADMIN in user_roles:
            dashboard_data['admin'] = {
                'active_auctions': Auction.objects.filter(status='ACTIVE').count(),
                'total_users': User.objects.count(),
                'recent_transactions': Transaction.objects.order_by('-created_at')[:5].values(
                    'id', 'amount', 'status', 'created_at', 'auction__title'
                ),
                # Add more admin stats...
            }
            
        # Seller dashboard
        if Role.SELLER in user_roles:
            dashboard_data['seller'] = {
                'active_auctions': Auction.objects.filter(seller=user, status='ACTIVE').count(),
                'sold_items': Transaction.objects.filter(auction__seller=user, status='COMPLETED').count(),
                'pending_contracts': Contract.objects.filter(seller=user, status='PENDING_SELLER').count(),
                # Add more seller stats...
            }
            
        # Buyer dashboard
        if Role.BUYER in user_roles:
            dashboard_data['buyer'] = {
                'active_bids': Bid.objects.filter(bidder=user, auction__status='ACTIVE').count(),
                'won_auctions': Transaction.objects.filter(winner=user).count(),
                'pending_contracts': Contract.objects.filter(buyer=user, status='PENDING_BUYER').count(),
                # Add more buyer stats...
            }
            
        # Inspector dashboard
        if Role.INSPECTOR in user_roles:
            pending_inspections = Auction.objects.filter(
                status='ACTIVE',
                documents__document_type='INSPECTION',
                documents__verification_status=False
            ).distinct().count()
            
            dashboard_data['inspector'] = {
                'pending_inspections': pending_inspections,
                'completed_inspections': Document.objects.filter(
                    document_type='INSPECTION',
                    verified_by=user
                ).count(),
                # Add more inspector stats...
            }
            
        # Legal representative dashboard
        if Role.LEGAL in user_roles:
            dashboard_data['legal'] = {
                'pending_reviews': Contract.objects.filter(
                    Q(seller_legal_rep=user, status='PENDING_SELLER') | 
                    Q(buyer_legal_rep=user, status='PENDING_BUYER')
                ).count(),
                'active_disputes': Transaction.objects.filter(status='DISPUTED').count(),
                # Add more legal stats...
            }
        
        return Response(dashboard_data)
    except Exception as e:
        logger.error(f"Error in role_dashboard view: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
@debug_request
def login_user(request):
    """
    Handle user login and return JWT tokens
    """
    email = request.data.get('email', '').lower().strip()
    password = request.data.get('password', '')
    
    if not email or not password:
        return create_response(
            error="Email and password are required",
            error_code="missing_credentials",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        if not user.check_password(password):
            return create_response(
                error="Invalid credentials",
                error_code="invalid_credentials",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        if not user.is_active:
            return create_response(
                error="Account is disabled",
                error_code="account_disabled",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        if not user.is_verified:
            # Optionally send a new verification code here
            return create_response(
                error="Email not verified",
                error_code="email_not_verified",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['user_id'] = str(user.id)
        
        return create_response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        })
        
    except User.DoesNotExist:
        return create_response(
            error="Invalid credentials",
            error_code="invalid_credentials",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return create_response(
            error="Login failed",
            error_code="login_failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@debug_request
def logout_user(request):
    """
    Blacklist the refresh token to logout
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return create_response(
                error="Refresh token is required",
                error_code="missing_token",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return create_response(message="Logged out successfully")
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return create_response(
            error="Logout failed",
            error_code="logout_failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )