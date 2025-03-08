
from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

import logging
import json
from functools import wraps
from django.conf import settings


logger = logging.getLogger(__name__)


def debug_request(view_func):
    """Decorator to log request details for debugging"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if settings.DEBUG:
            logger.debug(f"DEBUG: {request.method} {request.path}")
            logger.debug(f"DEBUG: Query Params: {request.GET}")
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if request.content_type == 'application/json':
                        body = json.loads(request.body) if request.body else {}
                        # Mask sensitive information
                        if 'password' in body:
                            body['password'] = '******'
                        logger.debug(f"DEBUG: Body: {body}")
                except Exception as e:
                    logger.debug(f"DEBUG: Could not parse request body: {e}")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


def role_required(allowed_roles):
    """
    Decorator to check if user has one of the allowed roles
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('Content-Type') == 'application/json':
                    return Response(
                        {'error': 'Authentication required'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                return redirect('login')

            # Check if user has any of the required roles
            user_roles = request.user.roles.values_list('name', flat=True)
            if any(role in user_roles for role in allowed_roles):
                return view_func(request, *args, **kwargs)
            
            # User doesn't have required role
            if request.headers.get('Content-Type') == 'application/json':
                return Response(
                    {'error': 'You do not have permission to perform this action'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return redirect('home')
        return _wrapped_view
    return decorator