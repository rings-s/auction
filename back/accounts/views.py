from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import UserProfile, BankAccount, Payment
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    BankAccountSerializer, BankAccountCreateSerializer, BankAccountUpdateSerializer,
    PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer
)
from .utils import send_verification_email, send_password_reset_email, EmailRateLimitExceeded, create_response, debug_request
from .middleware import track_successful_login
from .permissions import IsOwnerOrAdmin, IsAdminUser

logger = logging.getLogger(__name__)
User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}

class BaseAuthView(APIView):
    permission_classes = [AllowAny]
    
    def handle_exception(self, exc):
        logger.error(f"Exception in {self.__class__.__name__}: {str(exc)}", exc_info=True)
        return create_response(
            error="An unexpected error occurred",
            error_code="server_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class RegisterView(BaseAuthView):
    @debug_request
    @transaction.atomic
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return create_response(
                error=serializer.errors,
                error_code="validation_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        verification_code = user.generate_verification_code()

        try:
            context = {
                'user_name': f"{user.first_name} {user.last_name}",
                'verification_code': verification_code,
                'expiry_hours': 24
            }
            send_verification_email(user.email, verification_code, context)
            logger.info(f"Verification email sent to {user.email}")
        except EmailRateLimitExceeded as e:
            return create_response(error=str(e), error_code="rate_limit_exceeded", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as email_error:
            logger.error(f"Failed to send verification email: {email_error}", exc_info=True)
            return create_response(
                message="Registration successful but failed to send verification email. Please use resend option.",
                data={"email": user.email},
                status_code=status.HTTP_201_CREATED
            )

        return create_response(
            message="Registration successful. Please check your email for verification.",
            data={"email": user.email},
            status_code=status.HTTP_201_CREATED
        )

class VerifyEmailView(BaseAuthView):
    @debug_request
    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')

        if not all([email, verification_code]):
            return create_response(
                error="Email and verification code are required",
                error_code="missing_fields",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                tokens = get_tokens_for_user(user)
                return create_response(
                    message="Email already verified",
                    data={'tokens': tokens, 'user': UserProfileSerializer(user, context={'request': request}).data}
                )

            if user.verify_account(verification_code):
                tokens = get_tokens_for_user(user)
                logger.info(f"Email verification successful for user {user.id}")
                return create_response(
                    message="Email verified successfully",
                    data={'tokens': tokens, 'user': UserProfileSerializer(user, context={'request': request}).data}
                )
            else:
                return create_response(
                    error="Invalid or expired verification code",
                    error_code="invalid_verification",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist:
            return create_response(
                error="User not found",
                error_code="user_not_found",
                status_code=status.HTTP_404_NOT_FOUND
            )

class LoginView(BaseAuthView):
    @debug_request
    def post(self, request):
        email = request.data.get('email', request.data.get('username', '')).lower().strip()
        password = request.data.get('password', '')

        if not email or not password:
            return create_response(
                error="Email and password are required",
                error_code="missing_credentials",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return create_response(
                error="Invalid credentials",
                error_code="invalid_credentials",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

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
            return create_response(
                error="Email not verified",
                error_code="email_not_verified",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        track_successful_login(user, request)
        tokens = get_tokens_for_user(user)

        logger.info(f"Successful login for user: {email}")
        return create_response(
            data={'tokens': tokens, 'user': UserProfileSerializer(user, context={'request': request}).data}
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


# -------------------------------------------------------------------------
# Bank Account Management Views
# -------------------------------------------------------------------------

class BankAccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        bank_accounts = BankAccount.objects.filter(user=request.user)
        serializer = BankAccountSerializer(bank_accounts, many=True)
        return create_response(data={'bank_accounts': serializer.data})
    
    def post(self, request):
        serializer = BankAccountCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            bank_account = serializer.save()
            return create_response(
                data={'bank_account': BankAccountSerializer(bank_account).data},
                message="Bank account created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

class BankAccountDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_object(self, pk, user):
        try:
            bank_account = BankAccount.objects.get(pk=pk, user=user)
            return bank_account
        except BankAccount.DoesNotExist:
            return None
    
    def get(self, request, pk):
        bank_account = self.get_object(pk, request.user)
        if not bank_account:
            return create_response(
                error="Bank account not found",
                error_code="not_found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = BankAccountSerializer(bank_account)
        return create_response(data={'bank_account': serializer.data})
    
    def put(self, request, pk):
        bank_account = self.get_object(pk, request.user)
        if not bank_account:
            return create_response(
                error="Bank account not found",
                error_code="not_found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BankAccountUpdateSerializer(bank_account, data=request.data, partial=True)
        if serializer.is_valid():
            bank_account = serializer.save()
            return create_response(
                data={'bank_account': BankAccountSerializer(bank_account).data},
                message="Bank account updated successfully"
            )
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        bank_account = self.get_object(pk, request.user)
        if not bank_account:
            return create_response(
                error="Bank account not found",
                error_code="not_found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        bank_account.delete()
        return create_response(message="Bank account deleted successfully")


# -------------------------------------------------------------------------
# Payment Management Views
# -------------------------------------------------------------------------

class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
        serializer = PaymentSerializer(payments, many=True)
        return create_response(data={'payments': serializer.data})
    
    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            payment = serializer.save()
            return create_response(
                data={'payment': PaymentSerializer(payment).data},
                message="Payment created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_object(self, pk, user):
        try:
            payment = Payment.objects.get(pk=pk, user=user)
            return payment
        except Payment.DoesNotExist:
            return None
    
    def get(self, request, pk):
        payment = self.get_object(pk, request.user)
        if not payment:
            return create_response(
                error="Payment not found",
                error_code="not_found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = PaymentSerializer(payment)
        return create_response(data={'payment': serializer.data})
    
    def put(self, request, pk):
        payment = self.get_object(pk, request.user)
        if not payment:
            return create_response(
                error="Payment not found",
                error_code="not_found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PaymentUpdateSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            payment = serializer.save()
            return create_response(
                data={'payment': PaymentSerializer(payment).data},
                message="Payment updated successfully"
            )
        return create_response(
            error=serializer.errors,
            error_code="validation_error",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        payment = self.get_object(pk, request.user)
        if not payment:
            return create_response(
                error="Payment not found",
                error_code="not_found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        payment.delete()
        return create_response(message="Payment deleted successfully")