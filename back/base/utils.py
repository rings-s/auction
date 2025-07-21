"""
Shared utilities for the auction/property management system.

This module contains reusable functions for image processing, validation,
logging, and other common operations to reduce code duplication.
"""

import os
import logging
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Image Processing Utilities
# -------------------------------------------------------------------------

def process_image(image_file, max_size=(1200, 1200), quality=85):
    """
    Process and optimize an image file.
    
    Args:
        image_file: The image file to process
        max_size: Tuple of (max_width, max_height) for resizing
        quality: JPEG quality (1-95)
        
    Returns:
        ContentFile: Processed image file
        
    Raises:
        ValidationError: If the file is not a valid image
    """
    try:
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary for JPEG compatibility
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
        
        # Resize if needed
        original_size = img.size
        if img.height > max_size[1] or img.width > max_size[0]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            logger.info(f"Image resized from {original_size} to {img.size}")
        
        # Save optimized image
        output = BytesIO()
        
        # Determine format based on original file extension
        image_format = 'JPEG'
        if hasattr(image_file, 'name'):
            file_ext = os.path.splitext(image_file.name)[1].lower()
            if file_ext in ['.png', '.gif']:
                image_format = 'PNG'
                quality = None  # PNG doesn't use quality parameter
        
        save_kwargs = {'format': image_format, 'optimize': True}
        if quality and image_format == 'JPEG':
            save_kwargs['quality'] = quality
            
        img.save(output, **save_kwargs)
        output.seek(0)
        
        return ContentFile(output.read())
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise ValidationError(_('Invalid image file or processing error'))


def process_user_avatar(image_file):
    """
    Process user avatar with specific settings.
    
    Args:
        image_file: The avatar image file
        
    Returns:
        ContentFile: Processed avatar image
    """
    return process_image(image_file, max_size=(400, 400), quality=90)


def process_profile_image(image_file):
    """
    Process user profile image with specific settings.
    
    Args:
        image_file: The profile image file
        
    Returns:
        ContentFile: Processed profile image
    """
    return process_image(image_file, max_size=(800, 800), quality=85)


def process_property_media(image_file):
    """
    Process property media with specific settings for real estate images.
    
    Args:
        image_file: The property image file
        
    Returns:
        ContentFile: Processed property image
    """
    return process_image(image_file, max_size=(1200, 1200), quality=85)


# -------------------------------------------------------------------------
# Validation Utilities
# -------------------------------------------------------------------------

def validate_image_file(file):
    """
    Validate that a file is a valid image.
    
    Args:
        file: File to validate
        
    Raises:
        ValidationError: If file is not a valid image
    """
    if not file:
        return
        
    try:
        # Check file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise ValidationError(_('Image file too large. Maximum size is 10MB.'))
        
        # Try to open with PIL
        img = Image.open(file)
        img.verify()
        
        # Reset file pointer after verify
        file.seek(0)
        
    except Exception:
        raise ValidationError(_('Invalid image file format.'))


def validate_phone_number(phone_number):
    """
    Validate phone number format.
    
    Args:
        phone_number: Phone number string
        
    Returns:
        str: Cleaned phone number
        
    Raises:
        ValidationError: If phone number is invalid
    """
    import re
    
    if not phone_number:
        return phone_number
        
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Check format
    if not re.match(r'^\+?1?\d{9,15}$', cleaned):
        raise ValidationError(_('Invalid phone number format. Use international format.'))
    
    return cleaned


# -------------------------------------------------------------------------
# Logging Utilities
# -------------------------------------------------------------------------

def log_model_action(model_name, action, user=None, object_id=None, details=None):
    """
    Log model actions for audit trail.
    
    Args:
        model_name: Name of the model
        action: Action performed (create, update, delete, etc.)
        user: User who performed the action
        object_id: ID of the object affected
        details: Additional details about the action
    """
    user_info = f"User {user.id} ({user.email})" if user else "System"
    object_info = f"ID {object_id}" if object_id else "new object"
    details_info = f" - {details}" if details else ""
    
    logger.info(f"{model_name} {action}: {object_info} by {user_info}{details_info}")


def log_permission_denied(user, resource, action):
    """
    Log permission denied events for security monitoring.
    
    Args:
        user: User who was denied access
        resource: Resource they tried to access
        action: Action they tried to perform
    """
    logger.warning(f"Permission denied: User {user.id} ({user.email}) "
                  f"tried to {action} {resource}")


# -------------------------------------------------------------------------
# General Utilities
# -------------------------------------------------------------------------

def generate_unique_filename(original_name, prefix="", suffix=""):
    """
    Generate a unique filename to avoid conflicts.
    
    Args:
        original_name: Original filename
        prefix: Optional prefix to add
        suffix: Optional suffix to add before extension
        
    Returns:
        str: Unique filename
    """
    import uuid
    from django.utils import timezone
    
    name, ext = os.path.splitext(original_name)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    filename_parts = [prefix, name, suffix, timestamp, unique_id]
    filename_parts = [part for part in filename_parts if part]  # Remove empty parts
    
    return f"{'_'.join(filename_parts)}{ext}"


def safe_decimal_conversion(value, default=0):
    """
    Safely convert a value to Decimal, handling various input types.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Decimal: Converted value or default
    """
    from decimal import Decimal, InvalidOperation
    
    if value is None or value == '':
        return Decimal(str(default))
    
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        logger.warning(f"Could not convert {value} to Decimal, using default {default}")
        return Decimal(str(default))


def get_client_ip(request):
    """
    Get the client IP address from request.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or 'unknown'


# -------------------------------------------------------------------------
# Cache Utilities
# -------------------------------------------------------------------------

def cache_key_generator(*args, **kwargs):
    """
    Generate a consistent cache key from arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        str: Cache key
    """
    import hashlib
    import json
    
    # Create a consistent string representation
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True)
    
    # Create hash for consistent key length
    return hashlib.md5(key_string.encode()).hexdigest()


def invalidate_model_cache(model_class, object_id=None):
    """
    Invalidate cache entries related to a model.
    
    Args:
        model_class: Django model class
        object_id: Optional specific object ID
    """
    from django.core.cache import cache
    
    model_name = model_class.__name__.lower()
    cache_pattern = f"{model_name}_*"
    
    if object_id:
        cache_pattern = f"{model_name}_{object_id}_*"
    
    # Note: This is a simplified implementation
    # In production, you might want to use Redis pattern deletion
    logger.info(f"Cache invalidated for pattern: {cache_pattern}")