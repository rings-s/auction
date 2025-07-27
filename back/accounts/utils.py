from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
import logging
from functools import wraps
from decimal import Decimal

logger = logging.getLogger(__name__)

RATE_LIMITS = {
    'verification': {'max_attempts': 3, 'lockout_seconds': 1800},
    'reset': {'max_attempts': 3, 'lockout_seconds': 1800},
    'default': {'max_attempts': 5, 'lockout_seconds': 900}
}

class EmailRateLimitExceeded(Exception):
    def __init__(self, wait_minutes=None):
        self.wait_minutes = wait_minutes
        message = f"Too many attempts. Please wait {wait_minutes} minutes before trying again." if wait_minutes else "Too many attempts. Please try again later."
        super().__init__(message)

def _convert_decimals_to_floats(data):
    """Recursively convert Decimal and datetime objects for JSON serialization"""
    from datetime import datetime, date
    if isinstance(data, dict):
        return {key: _convert_decimals_to_floats(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_decimals_to_floats(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, date):
        return data.isoformat()
    else:
        return data

def create_response(data=None, message=None, error=None, error_code=None, status_code=status.HTTP_200_OK):
    response_data = {"status": "error" if error else "success"}

    if data is not None:
        response_data["data"] = _convert_decimals_to_floats(data)
    if message:
        response_data["message"] = message
    if error:
        if isinstance(error, dict) and any(isinstance(v, list) for v in error.values()):
            response_data["error"] = _convert_decimals_to_floats(error)
        else:
            response_data["error"] = {"message": error}
            if error_code:
                response_data["error"]["code"] = error_code

    return Response(response_data, status=status_code)

def check_rate_limit(identifier, action_type):
    if not identifier:
        logger.warning(f"Empty identifier for rate limit check: {action_type}")
        return

    limits = RATE_LIMITS.get(action_type, RATE_LIMITS['default'])
    max_attempts = limits['max_attempts']
    lockout_time = limits['lockout_seconds']

    cache_key = f"rate_limit_{action_type}_{identifier.lower().replace('@', '_at_').replace('.', '_dot_')}"

    attempts = cache.get(cache_key, 0)
    if attempts >= max_attempts:
        wait_minutes = lockout_time // 60
        logger.warning(f"Rate limit exceeded: {action_type} by {identifier}. Attempts: {attempts}/{max_attempts}")
        raise EmailRateLimitExceeded(wait_minutes=wait_minutes)

    cache.set(cache_key, attempts + 1, timeout=lockout_time)

def send_email(to_email, subject, template_name, context, action_type='default', check_limits=True, fail_silently=False):
    if not to_email:
        logger.error(f"Attempted to send email with empty recipient: {subject}")
        return False

    if check_limits:
        try:
            check_rate_limit(to_email, action_type)
        except EmailRateLimitExceeded as e:
            logger.warning(f"Rate limit hit: {action_type} to {to_email}")
            raise e

    company_name = getattr(settings, 'COMPANY_NAME', 'Real Estate Platform')
    default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    frontend_url = getattr(settings, 'FRONTEND_URL', '').rstrip('/')

    context.update({
        'company_name': company_name,
        'frontend_url': frontend_url,
        'current_year': timezone.now().year,
    })

    full_subject = f"[{company_name}] {subject}"

    try:
        html_template = f'emails/{template_name}.html'
        html_message = render_to_string(html_template, context)

        try:
            txt_template = f'emails/{template_name}.txt'
            plain_message = render_to_string(txt_template, context)
        except:
            plain_message = strip_tags(html_message)

        if settings.DEBUG and 'console' in getattr(settings, 'EMAIL_BACKEND', ''):
            logger.info(f"\n{'='*40}\nEMAIL TO: {to_email}\nSUBJECT: {full_subject}\nTEMPLATE: {template_name}\n{'='*40}")
            if settings.DEBUG and action_type in ['verification', 'reset']:
                code = context.get('verification_code') or context.get('reset_code')
                if code:
                    logger.info(f"DEBUG - {action_type.upper()} CODE: {code}")
            return True

        send_mail(
            subject=full_subject,
            message=plain_message,
            html_message=html_message,
            from_email=default_from_email,
            recipient_list=[to_email],
            fail_silently=fail_silently
        )
        logger.info(f"Email sent: {subject} to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send {action_type} email to {to_email}: {str(e)}", exc_info=True)
        if not fail_silently:
            raise
        return False

def send_verification_email(email, verification_code, context=None):
    ctx = context or {}
    ctx['verification_code'] = verification_code
    ctx['expiry_hours'] = RATE_LIMITS['verification']['lockout_seconds'] // 3600

    if settings.FRONTEND_URL:
        verify_path = getattr(settings, 'EMAIL_VERIFY_PATH', '/verify-email')
        ctx['verification_url'] = f"{settings.FRONTEND_URL.rstrip('/')}{verify_path}/{verification_code}"

    check_limits = not settings.DEBUG

    send_email(
        to_email=email,
        subject="Verify Your Email Address",
        template_name='verification_email',
        context=ctx,
        action_type='verification',
        check_limits=check_limits
    )

def send_password_reset_email(email, reset_code, context=None):
    ctx = context or {}
    ctx['reset_code'] = reset_code
    ctx['expiry_hours'] = RATE_LIMITS['reset']['lockout_seconds'] // 3600

    if settings.FRONTEND_URL:
        reset_path = getattr(settings, 'PASSWORD_RESET_PATH', '/reset-password')
        ctx['reset_url'] = f"{settings.FRONTEND_URL.rstrip('/')}{reset_path}/{reset_code}"

    send_email(
        to_email=email,
        subject="Reset Your Password",
        template_name='password_reset',
        context=ctx,
        action_type='reset'
    )

def debug_request(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)

        if settings.DEBUG:
            try:
                logger.debug(f"DEBUG: {request.method} {request.path}")
                if request.method not in ['GET', 'HEAD'] and hasattr(request, 'body') and request.body:
                    content_type = request.META.get('CONTENT_TYPE', '').lower()
                    if 'application/json' in content_type:
                        try:
                            import json
                            body = json.loads(request.body)
                            if isinstance(body, dict):
                                for k in body:
                                    if any(s in k.lower() for s in ['password', 'token', 'key', 'secret']):
                                        body[k] = '[REDACTED]'
                            logger.debug(f"BODY: {json.dumps(body)[:500]}")
                        except:
                            pass
            except:
                pass

        return response
    return wrapper