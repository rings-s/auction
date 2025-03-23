# consumers/middleware.py
import logging
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.conf import settings
import jwt

User = get_user_model()
logger = logging.getLogger(__name__)

# @database_sync_to_async
# def get_user(user_id):
#     """Get user by ID"""
#     try:
#         return User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return AnonymousUser()



@database_sync_to_async
def get_user_from_token(token_key):
    """
    Get user from JWT token

    Args:
        token_key: JWT token string

    Returns:
        User object if valid token, AnonymousUser otherwise
    """
    try:
        # Close old database connections
        close_old_connections()

        # Use the SimpleJWT AccessToken class if available
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

        try:
            # Parse the token
            token = AccessToken(token_key)

            # Get user from token payload
            user_id = token.payload.get('user_id')
            if not user_id:
                logger.warning("JWT token missing user_id claim")
                return AnonymousUser()

            # Get user from database
            user = User.objects.get(id=user_id)

            # Ensure user is active
            if not user.is_active:
                logger.warning(f"Inactive user {user_id} attempted WebSocket connection")
                return AnonymousUser()

            return user

        except (InvalidToken, TokenError) as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return AnonymousUser()

    except Exception as e:
        logger.error(f"JWT authentication error: {str(e)}")
        return AnonymousUser()

class JwtAuthMiddleware(BaseMiddleware):
    """
    Custom JWT authentication middleware for Channels
    """

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent connection pooling issues
        close_old_connections()

        # Get the user
        user = await self.get_user_from_scope(scope)
        scope['user'] = user

        # Call the next middleware or the consumer
        return await super().__call__(scope, receive, send)

    async def get_user_from_scope(self, scope):
        """Get the user from the JWT token in the WebSocket scope"""
        # Check if scope already has a user (e.g., from session)
        if 'user' in scope and scope['user'] is not None and scope['user'].is_authenticated:
            return scope['user']

        # Get the token from the query string
        token = None
        query_string = scope.get('query_string', b'').decode()
        if query_string:
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]

        # Check headers for token if not found in query string
        if not token and 'headers' in scope:
            headers = dict(scope['headers'])
            auth_header = headers.get(b'authorization', b'').decode().split()
            if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
                token = auth_header[1]

        # If no token, use an anonymous user
        if not token:
            return AnonymousUser()

        # Verify and decode the token
        try:
            # Get the algorithm and secret key from settings
            algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
            secret_key = getattr(settings, 'SECRET_KEY', '')

            # Decode the token
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])

            # Get the user ID from the payload
            user_id = payload.get('user_id')
            if not user_id:
                return AnonymousUser()

            # Get the user from the database
            return await get_user(user_id)
        except jwt.PyJWTError as e:
            logger.warning(f"JWT authentication error: {str(e)}")
            return AnonymousUser()
        except Exception as e:
            logger.error(f"Error during WebSocket authentication: {str(e)}")
            return AnonymousUser()

class QueryAuthMiddleware(BaseMiddleware):
    """
    Authentication middleware that uses query string parameters
    Use this when JWT authentication is not available
    """

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent connection pooling issues
        close_old_connections()

        # Get the token and session key from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)

        user_id = query_params.get('user_id', [None])[0]

        # Get the user
        if user_id:
            user = await get_user(user_id)
        else:
            user = AnonymousUser()

        scope['user'] = user

        # Call the next middleware or the consumer
        return await super().__call__(scope, receive, send)
