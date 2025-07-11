import json
import logging
import time
import re
from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLogMiddleware(MiddlewareMixin):
    """Middleware to log API requests and responses with timing - SYNC VERSION"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Configurable excluded paths
        self.excluded_paths = [re.compile(p) for p in getattr(settings, 'LOGGING_EXCLUDED_PATHS', [
            r'^/admin/', r'^/static/', r'^/media/', r'^/favicon\.ico$'
        ])]
        super().__init__(get_response)

    def is_excluded_path(self, path):
        return any(pattern.match(path) for pattern in self.excluded_paths)

    def _mask_sensitive_data(self, data):
        """Mask passwords, tokens, etc. in logs"""
        if isinstance(data, dict):
            masked_data = {}
            for k, v in data.items():
                if any(keyword in k.lower() for keyword in ['password', 'token', 'secret', 'authorization', 'cookie']):
                    masked_data[k] = '[REDACTED]'
                elif isinstance(v, dict):
                    masked_data[k] = self._mask_sensitive_data(v)
                else:
                    masked_data[k] = v
            return masked_data
        return data

    def process_request(self, request):
        """Process request - called before view"""
        if self.is_excluded_path(request.path_info):
            return None

        request.req_start_time = time.monotonic()

        if settings.DEBUG:
            # Log request details
            method, path, ip = request.method, request.path_info, request.META.get('REMOTE_ADDR', '-')
            logger.debug(f"REQUEST: {method} {path} from {ip}")

            # Log request body for non-GET methods
            if method not in ['GET', 'HEAD', 'OPTIONS'] and hasattr(request, 'body'):
                try:
                    body = request.body.decode('utf-8', errors='replace')
                    if body and 'application/json' in request.META.get('CONTENT_TYPE', '').lower():
                        try:
                            body_data = json.loads(body)
                            masked_data = self._mask_sensitive_data(body_data)
                            logger.debug(f"BODY: {json.dumps(masked_data)[:1000]}")
                        except json.JSONDecodeError:
                            logger.debug(f"BODY: {body[:500]} (Invalid JSON)")
                except Exception as e:
                    logger.warning(f"Could not log request body: {e}")
        
        return None

    def process_response(self, request, response):
        """Process response - called after view"""
        if self.is_excluded_path(request.path_info) or not hasattr(request, 'req_start_time'):
            return response

        duration = time.monotonic() - request.req_start_time
        duration_ms = round(duration * 1000)
        
        # Add duration header
        response['X-Request-Duration-Ms'] = str(duration_ms)
        status_code = getattr(response, 'status_code', 0)

        # Log level based on status code
        log_level = logging.INFO if status_code < 400 else logging.WARNING if status_code < 500 else logging.ERROR
        logger.log(log_level, f"RESPONSE: {request.method} {request.path_info} - Status {status_code} in {duration_ms}ms")

        # Log slow requests
        slow_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD_MS', 1000)
        if duration_ms > slow_threshold:
            logger.warning(f"SLOW REQUEST: {request.method} {request.path_info} took {duration:.3f}s")

        return response


class LoginTrackingMiddleware(MiddlewareMixin):
    """Middleware to extract client IP and User-Agent for login attempts - SYNC VERSION"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_path_pattern = re.compile(getattr(settings, 'LOGIN_PATH_REGEX', r'/api/accounts/login/?$'))
        super().__init__(get_response)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip if ip else '0.0.0.0'

    def process_request(self, request):
        """Process request to add tracking info"""
        if self.login_path_pattern.search(request.path_info) and request.method == 'POST':
            try:
                request.client_ip = self._get_client_ip(request)
                request.user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            except Exception as e:
                logger.error(f"Error setting login tracking attributes: {str(e)}")
        
        return None


# Helper function for login tracking
def track_successful_login(user, request):
    """Track login with IP and user agent data"""
    try:
        ip_address = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR', '0.0.0.0'))
        user_agent = getattr(request, 'user_agent', request.META.get('HTTP_USER_AGENT', 'Unknown'))
        
        logger.info(f"Login: {user.email} from IP: {ip_address}, UA: '{user_agent[:50]}...'")
        
        # Add security alerting logic here if needed
        if hasattr(settings, 'LOGIN_SECURITY_ALERTS') and settings.LOGIN_SECURITY_ALERTS:
            logger.warning(f"New device/location for {user.email} from {ip_address}")

    except Exception as e:
        logger.error(f"Error tracking login: {str(e)}")