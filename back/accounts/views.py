from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from datetime import timedelta
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import UserProfile
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer,
    EmailVerificationSerializer, UserBriefSerializer, UserRoleUpdateSerializer
)
from .utils import send_verification_email, send_password_reset_email, EmailRateLimitExceeded, create_response, debug_request
from .middleware import track_successful_login
from .permissions import IsOwnerOrAdmin, IsAdminUser

logger = logging.getLogger(__name__)
User = get_user_model()


class AuthThrottle(AnonRateThrottle):
    """Custom throttle for authentication endpoints."""
    scope = 'auth'
    rate = '10/min'


class PasswordResetThrottle(AnonRateThrottle):
    """Stricter throttle for password reset endpoints."""
    scope = 'password_reset'
    rate = '5/hour'


def get_tokens_for_user(user):
    """Generate JWT tokens for user with enhanced metadata."""
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['role'] = user.role
    refresh['is_verified'] = user.is_verified
    refresh['user_id'] = str(user.uuid)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'expires_in': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    }


class BaseAuthView(APIView):
    """Enhanced base view for authentication endpoints."""
    
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    throttle_classes = [AuthThrottle]
    
    def handle_exception(self, exc):
        """Enhanced exception handling with detailed logging."""
        logger.error(
            f"Exception in {self.__class__.__name__}: {str(exc)}",
            extra={
                'user': getattr(self.request, 'user', None),
                'ip': self.get_client_ip(),
                'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
                'path': self.request.path,
                'method': self.request.method,
            },
            exc_info=True
        )
        
        # Return appropriate error response based on exception type
        if isinstance(exc, ValidationError):
            return create_response(
                error=exc.detail if hasattr(exc, 'detail') else str(exc),
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, PermissionDenied):
            return create_response(
                error="Permission denied",
                error_code="permission_denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        else:
            return create_response(
                error="An unexpected error occurred. Please try again later.",
                error_code="server_error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self):
        """Get client IP address from request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR', '')
        return ip
    
    def log_security_event(self, event_type, user_email=None, details=None):
        """Log security-related events."""
        logger.warning(
            f"Security event: {event_type}",
            extra={
                'event_type': event_type,
                'user_email': user_email,
                'ip': self.get_client_ip(),
                'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
                'details': details or {},
                'timestamp': timezone.now().isoformat(),
            }
        )

class RegisterView(BaseAuthView):
    """Enhanced user registration endpoint with comprehensive validation and security."""
    
    @debug_request
    @transaction.atomic
    def post(self, request):
        """Register a new user with email verification."""
        
        # Check for registration rate limiting per IP
        client_ip = self.get_client_ip()
        registration_key = f"registration_attempts_{client_ip}"
        registration_attempts = cache.get(registration_key, 0)
        
        if registration_attempts >= 5:  # Max 5 registrations per hour per IP
            self.log_security_event(
                'registration_rate_limit_exceeded',
                details={'ip': client_ip, 'attempts': registration_attempts}
            )
            return create_response(
                error="Too many registration attempts. Please try again later.",
                error_code="rate_limit_exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Validate and process registration
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            # Increment registration attempts on validation failure
            cache.set(registration_key, registration_attempts + 1, 3600)  # 1 hour
            
            return create_response(
                error=serializer.errors,
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create user
            user = serializer.save()
            verification_code = user.generate_verification_code()
            
            # Increment successful registration counter
            cache.set(registration_key, registration_attempts + 1, 3600)
            
            # Send verification email
            try:
                context = {
                    'user_name': f"{user.first_name} {user.last_name}",
                    'verification_code': verification_code,
                    'expiry_hours': getattr(settings, 'VERIFICATION_TOKEN_EXPIRATION_HOURS', 24),
                    'site_name': getattr(settings, 'SITE_NAME', 'Auction Platform'),
                    'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:7500')
                }
                send_verification_email(user.email, verification_code, context)
                
                logger.info(
                    f"User registration successful: {user.email} (ID: {user.id})",
                    extra={
                        'user_id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'ip': client_ip
                    }
                )
                
                return create_response(
                    message="Registration successful. Please check your email for verification instructions.",
                    data={
                        "email": user.email,
                        "verification_required": True,
                        "resend_available": True
                    },
                    status_code=status.HTTP_201_CREATED
                )
                
            except EmailRateLimitExceeded as e:
                logger.warning(f"Email rate limit exceeded during registration: {user.email}")
                return create_response(
                    message="Registration successful but verification email was rate limited. Please use resend option.",
                    data={
                        "email": user.email,
                        "verification_required": True,
                        "resend_available": True,
                        "rate_limited": True
                    },
                    error_code="email_rate_limit",
                    status_code=status.HTTP_201_CREATED
                )
                
            except Exception as email_error:
                logger.error(
                    f"Failed to send verification email for {user.email}: {str(email_error)}",
                    exc_info=True
                )
                return create_response(
                    message="Registration successful but failed to send verification email. Please use resend option.",
                    data={
                        "email": user.email,
                        "verification_required": True,
                        "resend_available": True,
                        "email_failed": True
                    },
                    status_code=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}", exc_info=True)
            return create_response(
                error="Registration failed due to an unexpected error. Please try again.",
                error_code="registration_failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyEmailView(BaseAuthView):
    """Enhanced email verification endpoint with security measures."""
    
    @debug_request
    def post(self, request):
        """Verify user email with verification code."""
        
        # Use the enhanced serializer for validation
        serializer = EmailVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return create_response(
                error=serializer.errors,
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        verification_code = serializer.validated_data['verification_code']
        client_ip = self.get_client_ip()
        
        # Rate limiting for verification attempts per IP
        verification_key = f"verification_attempts_{client_ip}"
        verification_attempts = cache.get(verification_key, 0)
        
        if verification_attempts >= 10:  # Max 10 attempts per hour
            self.log_security_event(
                'verification_rate_limit_exceeded',
                user_email=email,
                details={'ip': client_ip, 'attempts': verification_attempts}
            )
            return create_response(
                error="Too many verification attempts. Please try again later.",
                error_code="rate_limit_exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            user = User.objects.get(email=email)
            
            # Check if already verified
            if user.is_verified:
                tokens = get_tokens_for_user(user)
                track_successful_login(user, request)
                
                logger.info(f"Login via already verified email: {user.email} (ID: {user.id})")
                
                return create_response(
                    message="Email already verified. Welcome back!",
                    data={
                        'tokens': tokens, 
                        'user': UserProfileSerializer(user, context={'request': request}).data,
                        'already_verified': True
                    }
                )

            # Attempt verification
            if user.verify_account(verification_code):
                tokens = get_tokens_for_user(user)
                track_successful_login(user, request)
                
                # Clear verification attempts on success
                cache.delete(verification_key)
                
                logger.info(
                    f"Email verification successful: {user.email} (ID: {user.id})",
                    extra={
                        'user_id': user.id,
                        'email': user.email,
                        'ip': client_ip
                    }
                )
                
                return create_response(
                    message="Email verified successfully. Welcome to the platform!",
                    data={
                        'tokens': tokens, 
                        'user': UserProfileSerializer(user, context={'request': request}).data,
                        'newly_verified': True
                    }
                )
            else:
                # Increment failed verification attempts
                cache.set(verification_key, verification_attempts + 1, 3600)
                
                self.log_security_event(
                    'invalid_verification_attempt',
                    user_email=email,
                    details={'ip': client_ip, 'code_provided': verification_code}
                )
                
                return create_response(
                    error="Invalid or expired verification code. Please check your email or request a new code.",
                    error_code="invalid_verification",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist:
            # Increment attempts even for non-existent users to prevent enumeration
            cache.set(verification_key, verification_attempts + 1, 3600)
            
            self.log_security_event(
                'verification_attempt_nonexistent_user',
                user_email=email,
                details={'ip': client_ip}
            )
            
            return create_response(
                error="Invalid verification details. Please check your email and verification code.",
                error_code="invalid_verification",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class LoginView(BaseAuthView):
    """Enhanced login endpoint with comprehensive security measures."""
    
    @debug_request
    def post(self, request):
        """Authenticate user with email and password."""
        
        # Extract and normalize credentials
        email = request.data.get('email', request.data.get('username', '')).lower().strip()
        password = request.data.get('password', '')
        client_ip = self.get_client_ip()
        
        # Basic validation
        if not email or not password:
            return create_response(
                error="Email and password are required",
                error_code="missing_credentials",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Rate limiting for login attempts per IP
        login_attempts_key = f"login_attempts_{client_ip}"
        login_attempts = cache.get(login_attempts_key, 0)
        
        if login_attempts >= 10:  # Max 10 failed attempts per hour
            self.log_security_event(
                'login_rate_limit_exceeded',
                user_email=email,
                details={'ip': client_ip, 'attempts': login_attempts}
            )
            return create_response(
                error="Too many login attempts. Please try again later.",
                error_code="rate_limit_exceeded", 
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Rate limiting per email
        email_attempts_key = f"login_attempts_email_{email}"
        email_attempts = cache.get(email_attempts_key, 0)
        
        if email_attempts >= 5:  # Max 5 failed attempts per email per hour
            self.log_security_event(
                'login_email_rate_limit_exceeded',
                user_email=email,
                details={'ip': client_ip, 'attempts': email_attempts}
            )
            return create_response(
                error="Too many login attempts for this email. Please try again later or reset your password.",
                error_code="email_rate_limit_exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            # Get user - use select_related for efficiency
            user = User.objects.select_related('profile').get(email=email)
            
            # Check password
            if not user.check_password(password):
                # Increment failed attempts
                cache.set(login_attempts_key, login_attempts + 1, 3600)  # 1 hour
                cache.set(email_attempts_key, email_attempts + 1, 3600)  # 1 hour
                
                self.log_security_event(
                    'invalid_password_attempt',
                    user_email=email,
                    details={'ip': client_ip, 'user_id': user.id if user else None}
                )
                
                return create_response(
                    error="Invalid email or password",
                    error_code="invalid_credentials",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            # Check if account is active
            if not user.is_active:
                self.log_security_event(
                    'login_attempt_disabled_account',
                    user_email=email,
                    details={'ip': client_ip, 'user_id': user.id}
                )
                
                return create_response(
                    error="Your account has been disabled. Please contact support.",
                    error_code="account_disabled",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            # Check if email is verified
            if not user.is_verified:
                logger.info(f"Login attempt with unverified email: {email}")
                return create_response(
                    error="Please verify your email address before logging in.",
                    error_code="email_not_verified",
                    data={
                        "email": user.email,
                        "verification_required": True,
                        "resend_available": True
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            # Successful login - clear failed attempts
            cache.delete(login_attempts_key)
            cache.delete(email_attempts_key)
            
            # Track login and generate tokens
            track_successful_login(user, request)
            tokens = get_tokens_for_user(user)
            
            # Log successful login
            logger.info(
                f"Successful login: {user.email} (ID: {user.id})",
                extra={
                    'user_id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'ip': client_ip,
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
            
            return create_response(
                message="Login successful",
                data={
                    'tokens': tokens, 
                    'user': UserProfileSerializer(user, context={'request': request}).data
                }
            )

        except User.DoesNotExist:
            # Increment failed attempts even for non-existent users
            cache.set(login_attempts_key, login_attempts + 1, 3600)
            cache.set(email_attempts_key, email_attempts + 1, 3600)
            
            self.log_security_event(
                'login_attempt_nonexistent_user',
                user_email=email,
                details={'ip': client_ip}
            )
            
            return create_response(
                error="Invalid email or password",
                error_code="invalid_credentials",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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

            logger.info(f"User {request.user.email} logged out successfully")
            return create_response(message="Logged out successfully")
        except TokenError:
            return create_response(
                error="Invalid token",
                error_code="invalid_token",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class TokenRefreshView(BaseAuthView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return create_response(
                    error="Refresh token is required",
                    error_code="missing_token",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken(refresh_token)
            return create_response(data={'access': str(refresh.access_token)})
        except TokenError:
            return create_response(
                error="Invalid or expired refresh token",
                error_code="invalid_token",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = {
            "email": user.email, "user_id": str(user.uuid), "first_name": user.first_name,
            "last_name": user.last_name, "is_verified": user.is_verified, "is_active": user.is_active,
            "is_staff": user.is_staff, "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        return create_response(data={"valid": True, "user": user_data})

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return create_response(data={"user": serializer.data})

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True, context={'request': request}
        )

        if not serializer.is_valid():
            return create_response(
                error=serializer.errors,
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        updated_user = serializer.save()
        logger.info(f"Profile updated for user {request.user.email}")

        return create_response(
            data={"user": UserProfileSerializer(updated_user, context={'request': request}).data},
            message="Profile updated successfully"
        )

class PublicProfileView(BaseAuthView):
    def get(self, request, user_id):
        user = get_object_or_404(User, uuid=user_id)
        serializer = UserProfileSerializer(user, context={'request': request})
        data = serializer.data

        # Filter out sensitive information
        sensitive_fields = [
            'email', 'is_verified', 'phone_number', 'date_of_birth',
            'address', 'tax_id', 'credit_limit', 'company_registration'
        ]
        for field in sensitive_fields:
            data.pop(field, None)

        return create_response(data={"user": data})

class PasswordResetRequestView(BaseAuthView):
    @debug_request
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        if not email:
            return create_response(
                error="Email is required",
                error_code="email_required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)

            if user.reset_code_created:
                time_since_last_request = timezone.now() - user.reset_code_created
                if time_since_last_request < timedelta(minutes=5):
                    wait_minutes = 5 - (time_since_last_request.seconds // 60)
                    return create_response(
                        error=f"Please wait {wait_minutes} minutes before requesting another reset",
                        error_code="rate_limit",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS
                    )

            reset_code = user.generate_reset_code()

            try:
                context = {
                    'user_name': f"{user.first_name} {user.last_name}",
                    'reset_code': reset_code,
                    'expiry_hours': 1
                }
                send_password_reset_email(user.email, reset_code, context)
                logger.info(f"Password reset email sent to {user.email}")
            except EmailRateLimitExceeded as e:
                return create_response(error=str(e), error_code="rate_limit_exceeded", status_code=status.HTTP_429_TOO_MANY_REQUESTS)

        except User.DoesNotExist:
            logger.info(f"Password reset requested for non-existent email: {email}")

        return create_response(
            message="If an account exists with this email, password reset instructions have been sent"
        )

class VerifyResetCodeView(BaseAuthView):
    def post(self, request):
        email = request.data.get('email')
        reset_code = request.data.get('reset_code')

        if not all([email, reset_code]):
            return create_response(
                error="Email and reset code are required",
                error_code="missing_fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)

            if not user.reset_code_created or user.reset_code != reset_code:
                return create_response(
                    error="Invalid reset code",
                    error_code="invalid_code",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            expiry_time = user.reset_code_created + timedelta(hours=1)
            if timezone.now() > expiry_time:
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

class ResetPasswordView(BaseAuthView):
    @transaction.atomic
    def post(self, request):
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
            user = User.objects.get(email=email)

            if user.reset_password(reset_code, new_password):
                tokens = get_tokens_for_user(user)
                logger.info(f"Password reset successful for user {user.email}")
                return create_response(
                    message="Password reset successfully",
                    data={'tokens': tokens, 'user': UserProfileSerializer(user, context={'request': request}).data}
                )
            else:
                return create_response(
                    error="Invalid or expired reset code",
                    error_code="reset_failed",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist:
            return create_response(
                error="Invalid or expired reset code",
                error_code="invalid_code",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
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

        user.set_password(new_password)
        user.save()
        tokens = get_tokens_for_user(user)

        logger.info(f"Password changed successfully for user {user.email}")
        return create_response(message="Password changed successfully", data={'tokens': tokens})

class ResendVerificationView(BaseAuthView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return create_response(
                error="Email is required",
                error_code="missing_fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                return create_response(message="Email is already verified")

            if user.verification_code_created:
                time_since_last_request = timezone.now() - user.verification_code_created
                if time_since_last_request < timedelta(minutes=5):
                    wait_minutes = 5 - (time_since_last_request.seconds // 60)
                    return create_response(
                        error=f"Please wait {wait_minutes} minutes before requesting another verification email",
                        error_code="rate_limit",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS
                    )

            verification_code = user.generate_verification_code()

            try:
                context = {
                    'user_name': f"{user.first_name} {user.last_name}",
                    'verification_code': verification_code,
                    'expiry_hours': 24
                }
                send_verification_email(user.email, verification_code, context)
                logger.info(f"Verification email resent to {user.email}")
            except EmailRateLimitExceeded as e:
                return create_response(error=str(e), error_code="rate_limit_exceeded", status_code=status.HTTP_429_TOO_MANY_REQUESTS)

        except User.DoesNotExist:
            logger.info(f"Verification resend requested for non-existent email: {email}")

        return create_response(
            message="If an account exists with this email, a verification email has been sent"
        )

class UpdateAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if 'avatar' not in request.FILES:
            return create_response(
                error="No avatar file provided",
                error_code="missing_file",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        avatar_file = request.FILES['avatar']

        if avatar_file.size > 2 * 1024 * 1024:  # 2MB
            return create_response(
                error="Avatar file too large. Maximum size is 2MB",
                error_code="file_too_large",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return create_response(
                error="Invalid file type. Allowed types: JPEG, PNG, GIF",
                error_code="invalid_file_type",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        if user.avatar:
            try:
                storage, path = user.avatar.storage, user.avatar.path
                storage.delete(path)
            except Exception as e:
                logger.warning(f"Failed to delete old avatar: {str(e)}")

        user.avatar = avatar_file
        user.save()

        logger.info(f"Avatar updated for user {user.email}")
        return create_response(
            data={"user": UserProfileSerializer(user, context={'request': request}).data},
            message="Avatar updated successfully"
        )

class UserBriefView(APIView):
    """Brief user information endpoint for lightweight displays."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get brief user information."""
        serializer = UserBriefSerializer(request.user, context={'request': request})
        return create_response(data={"user": serializer.data})


# Admin Management Views
# -------------------------------------------------------------------------

class UserListView(APIView):
    """List all users for admin purposes."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Get list of all users."""
        users = User.objects.all().order_by('-date_joined')
        serializer = UserProfileSerializer(users, many=True, context={'request': request})
        return create_response(data={"users": serializer.data, "count": users.count()})


class UserDetailView(APIView):
    """Get detailed user information for admin purposes."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, user_id):
        """Get detailed user information."""
        user = get_object_or_404(User, uuid=user_id)
        serializer = UserProfileSerializer(user, context={'request': request})
        return create_response(data={"user": serializer.data})


class UserRoleUpdateView(APIView):
    """Update user role for admin purposes."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        """Update user role."""
        user = get_object_or_404(User, uuid=user_id)
        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return create_response(
                error=serializer.errors,
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        updated_user = serializer.save()
        logger.info(f"User role updated: {user.email} -> {updated_user.role} by {request.user.email}")
        
        return create_response(
            data={"user": UserProfileSerializer(updated_user, context={'request': request}).data},
            message="User role updated successfully"
        )


class UserStatusUpdateView(APIView):
    """Update user status (active/inactive) for admin purposes."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        """Update user status."""
        user = get_object_or_404(User, uuid=user_id)
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return create_response(
                error="is_active field is required",
                error_code="missing_field",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(is_active, bool):
            return create_response(
                error="is_active must be a boolean value",
                error_code="invalid_type",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = is_active
        user.save()
        
        logger.info(f"User status updated: {user.email} -> {'active' if is_active else 'inactive'} by {request.user.email}")
        
        return create_response(
            data={"user": UserProfileSerializer(user, context={'request': request}).data},
            message=f"User {'activated' if is_active else 'deactivated'} successfully"
        )


class UserAnalyticsView(APIView):
    """Get user analytics data for admin purposes."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Get user analytics."""
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Get basic user counts
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_verified=True).count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Get users by role
        role_distribution = User.objects.values('role').annotate(count=Count('id'))
        
        # Get recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()
        
        # Get monthly registration trend (last 6 months)
        monthly_registrations = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            count = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lte=month_end
            ).count()
            
            monthly_registrations.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        analytics_data = {
            'total_users': total_users,
            'verified_users': verified_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'verification_rate': round((verified_users / total_users * 100) if total_users > 0 else 0, 2),
            'role_distribution': list(role_distribution),
            'recent_registrations': recent_registrations,
            'monthly_registrations': list(reversed(monthly_registrations))
        }
        
        return create_response(data={"analytics": analytics_data})


# Utility Views
# -------------------------------------------------------------------------

class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Perform health check."""
        try:
            # Check database connectivity
            User.objects.first()
            
            # Check cache connectivity if using cache
            from django.core.cache import cache
            cache.get('health_check')
            
            return create_response(
                data={
                    "status": "healthy",
                    "timestamp": timezone.now().isoformat(),
                    "version": "1.0.0",
                    "database": "connected",
                    "cache": "connected"
                },
                message="Service is healthy"
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return create_response(
                error="Service is unhealthy",
                error_code="health_check_failed",
                data={
                    "status": "unhealthy",
                    "timestamp": timezone.now().isoformat(),
                    "error": str(e)
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )


# -------------------------------------------------------------------------
