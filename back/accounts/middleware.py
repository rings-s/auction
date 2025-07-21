import json
import logging
import time
import re
from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseForbidden

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


class SuperuserOnlyAdminMiddleware(MiddlewareMixin):
    """
    ✅ NEW: Middleware to ensure only superusers can access Django admin panel
    Provides enhanced security by restricting admin access to superusers only
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
    def process_request(self, request):
        """Process request to check admin access permissions"""
        # Check if request is for admin panel
        if request.path.startswith('/admin/'):
            try:
                # Allow admin login page and admin root page for all authenticated users
                if request.path in ['/admin/login/', '/admin/', '/admin/logout/']:
                    return None
                    
                # Allow static admin files
                if '/admin/static/' in request.path or '/admin/jsi18n/' in request.path:
                    return None
                
                # Check if user is authenticated
                if request.user.is_authenticated:
                    # Check if user is superuser
                    if not request.user.is_superuser:
                        logger.warning(
                            f"Non-superuser {request.user.email} attempted to access admin: {request.path}"
                        )
                        
                        # Create a more user-friendly error response
                        error_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Access Denied - Admin Panel</title>
                            <style>
                                body {{ 
                                    font-family: Arial, sans-serif; 
                                    text-align: center; 
                                    padding: 50px; 
                                    background-color: #f8f9fa;
                                }}
                                .error-container {{ 
                                    max-width: 500px; 
                                    margin: 0 auto; 
                                    background: white; 
                                    padding: 30px; 
                                    border-radius: 8px; 
                                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                                }}
                                .error-title {{ 
                                    color: #dc3545; 
                                    font-size: 24px; 
                                    margin-bottom: 20px;
                                }}
                                .error-message {{ 
                                    color: #6c757d; 
                                    font-size: 16px; 
                                    margin-bottom: 20px;
                                }}
                                .back-link {{ 
                                    color: #007bff; 
                                    text-decoration: none; 
                                    font-size: 14px;
                                }}
                                .back-link:hover {{ 
                                    text-decoration: underline; 
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="error-container">
                                <h1 class="error-title">🚫 Access Denied</h1>
                                <p class="error-message">
                                    Only superusers can access the admin panel.<br>
                                    Your account ({request.user.email}) does not have sufficient privileges.
                                </p>
                                <p class="error-message">
                                    Please contact your administrator if you believe this is an error.
                                </p>
                                <a href="/" class="back-link">← Return to Homepage</a>
                            </div>
                        </body>
                        </html>
                        """
                        
                        return HttpResponseForbidden(error_html)
                        
                # Redirect unauthenticated users to admin login
                else:
                    logger.info(f"Unauthenticated user redirected to admin login from: {request.path}")
                    return redirect('admin:login')
                    
            except Exception as e:
                logger.error(f"Error in SuperuserOnlyAdminMiddleware: {str(e)}")
                # In case of error, allow the request to proceed (fail open for safety)
                return None
        
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