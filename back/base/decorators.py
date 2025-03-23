import functools
import logging
import time
from typing import Callable, Any, Union, List, Optional
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.conf import settings

logger = logging.getLogger(__name__)

def debug_request(view_func: Callable) -> Callable:
    """
    Debug decorator to log request details for troubleshooting.
    Useful for tracking request information during development.
    
    Args:
        view_func (Callable): View function to be decorated
    
    Returns:
        Callable: Wrapped view function with debug logging
    """
    @functools.wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        # Only log in debug mode
        if settings.DEBUG:
            log_data = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
                'query_params': dict(request.GET),
                'headers': {k: v for k, v in request.headers.items() if k.lower() not in ['cookie', 'authorization']}
            }
            
            try:
                log_data['body'] = request.body.decode('utf-8')
            except Exception:
                log_data['body'] = 'Unable to decode request body'
            
            logger.info(f"Debug Request: {log_data}")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(roles: Optional[List[str]] = None, 
                  permission: Optional[str] = None) -> Callable:
    """
    Decorator to restrict view access based on user roles or specific permissions.
    
    Args:
        roles (List[str], optional): List of allowed roles
        permission (str, optional): Specific permission to check
    
    Returns:
        Callable: Decorator function for role-based access control
    
    Raises:
        PermissionDenied: If user doesn't have required role or permission
    """
    def decorator(view_func: Callable) -> Callable:
        @functools.wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
            # Skip checks for superusers and staff
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                logger.warning(f"Unauthenticated access attempt to {view_func.__name__}")
                raise PermissionDenied("Authentication required.")
            
            # Check roles if specified
            if roles:
                user_roles = request.user.role_names
                if not any(role in user_roles for role in roles):
                    logger.warning(
                        f"Access denied for user {request.user.email}. "
                        f"Required roles: {roles}, User roles: {user_roles}"
                    )
                    raise PermissionDenied(f"Access restricted to roles: {', '.join(roles)}")
            
            # Check specific permission if specified
            if permission:
                if not request.user.has_auction_permission(permission):
                    logger.warning(
                        f"Access denied for user {request.user.email}. "
                        f"Required permission: {permission}"
                    )
                    raise PermissionDenied(f"Permission '{permission}' is required.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def timer(logger_obj: Optional[logging.Logger] = None) -> Callable:
    """
    Decorator to measure and log function execution time.
    
    Args:
        logger_obj (logging.Logger, optional): Custom logger for timing info.
                                               Uses default logger if not provided.
    
    Returns:
        Callable: Decorator function for timing function execution
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        log = logger_obj or logger
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                
                log.info(
                    f"Function '{func.__name__}' executed in {execution_time:.4f} seconds"
                )
                
                return result
            
            except Exception as e:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                
                log.error(
                    f"Function '{func.__name__}' failed after {execution_time:.4f} seconds: {e}"
                )
                
                raise
        return wrapper
    return decorator


def validate_params(**param_types: Any):
    """
    Decorator to validate function parameters based on type hints.
    
    Args:
        **param_types: Mapping of parameter names to their expected types
    
    Returns:
        Callable: Decorator function for parameter validation
    
    Raises:
        TypeError: If parameter types do not match expectations
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Validate positional arguments
            for i, (arg_name, expected_type) in enumerate(param_types.items()):
                if i < len(args):
                    if not isinstance(args[i], expected_type):
                        raise TypeError(
                            f"Argument '{arg_name}' must be of type {expected_type}, "
                            f"got {type(args[i])}"
                        )
            
            # Validate keyword arguments
            for arg_name, arg_value in kwargs.items():
                if arg_name in param_types:
                    expected_type = param_types[arg_name]
                    if not isinstance(arg_value, expected_type):
                        raise TypeError(
                            f"Argument '{arg_name}' must be of type {expected_type}, "
                            f"got {type(arg_value)}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry(max_attempts: int = 3, 
          exceptions: Union[Exception, tuple] = Exception, 
          delay: float = 1.0):
    """
    Decorator to retry a function in case of specified exceptions.
    
    Args:
        max_attempts (int): Maximum number of retry attempts
        exceptions (Exception or tuple): Exception types to catch and retry
        delay (float): Delay between retry attempts in seconds
    
    Returns:
        Callable: Decorator function for retry mechanism
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_attempts} attempts. "
                            f"Last error: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempts} failed for '{func.__name__}': {e}. Retrying..."
                    )
                    time.sleep(delay)
            
            raise RuntimeError("Retry mechanism failed unexpectedly")
        return wrapper
    return decorator


def audit_log(log_input: bool = True, log_output: bool = True):
    """
    Decorator to log function inputs and outputs for auditing purposes.
    
    Args:
        log_input (bool): Whether to log input parameters
        log_output (bool): Whether to log return value
    
    Returns:
        Callable: Decorator function for audit logging
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Log input if enabled
            if log_input:
                logger.info(
                    f"Audit Log - Input to {func.__name__}: "
                    f"args={args}, kwargs={kwargs}"
                )
            
            try:
                result = func(*args, **kwargs)
                
                # Log output if enabled
                if log_output:
                    logger.info(
                        f"Audit Log - Output from {func.__name__}: "
                        f"result={result}"
                    )
                
                return result
            
            except Exception as e:
                logger.error(
                    f"Audit Log - Exception in {func.__name__}: {e}"
                )
                raise
        return wrapper
    return decorator


# Example usage in views
"""
@role_required(['admin', 'agent'])
@timer()
@validate_params(user_id=str)
def example_view(request, user_id):
    # View implementation
    pass
"""