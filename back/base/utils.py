"""
Utility functions for views
"""
import logging
from rest_framework import status
from rest_framework.response import Response
from .models import Property
from django.utils import timezone
        
logger = logging.getLogger(__name__)


def create_response(data=None, message=None, error=None, error_code=None, status_code=status.HTTP_200_OK):
    """
    Create a standardized response format for API views
    
    Args:
        data (dict, optional): Data to return in response
        message (str, optional): Success message
        error (str or dict, optional): Error message or validation errors
        error_code (str, optional): Error code for client identification
        status_code (int, optional): HTTP status code
    
    Returns:
        Response: DRF Response with formatted data
    """
    response = {"success": error is None}
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    if error:
        response["error"] = error
        
    if error_code:
        response["error_code"] = error_code
    
    return Response(response, status=status_code)


def send_bid_confirmation_email(email, auction_title, property_title, bid_amount, currency, auction_id):
    """
    Send bid confirmation email
    
    Args:
        email (str): Recipient email
        auction_title (str): Auction title
        property_title (str): Property title
        bid_amount (decimal): Bid amount
        currency (str): Currency code
        auction_id (str): Auction ID
    """
    try:
        # Implementation of email sending logic
        logger.info(f"Sending bid confirmation email to {email} for auction {auction_id}")
        # Actual email sending would be implemented here
        pass
    except Exception as e:
        logger.error(f"Failed to send bid confirmation email: {str(e)}")


def send_outbid_notification_email(email, auction_title, auction_id, property_title, 
                                  previous_bid, current_bid, currency, end_time):
    """
    Send outbid notification email
    
    Args:
        email (str): Recipient email
        auction_title (str): Auction title
        auction_id (str): Auction ID
        property_title (str): Property title
        previous_bid (decimal): User's previous bid
        current_bid (decimal): New highest bid
        currency (str): Currency code
        end_time (datetime): Auction end time
    """
    try:
        # Implementation of outbid notification logic
        logger.info(f"Sending outbid notification email to {email} for auction {auction_id}")
        # Actual email sending would be implemented here
        pass
    except Exception as e:
        logger.error(f"Failed to send outbid notification email: {str(e)}")


def update_property_status(property_id, new_status, user):
    """
    Utility function to update property status
    
    Args:
        property_id: ID of the property
        new_status: New status to set
        user: User performing the status update
    
    Returns:
        Tuple of (success, message)
    """
    try:
     
        property_obj = Property.objects.get(id=property_id)
        
        # Check permissions
        if not user.is_admin and property_obj.owner != user:
            return False, "You do not have permission to update this property status"
        
        # Validate status transition
        valid_status_transitions = {
            'draft': ['pending_approval', 'inactive'],
            'pending_approval': ['active', 'rejected'],
            'active': ['under_contract', 'inactive'],
            'under_contract': ['sold', 'active'],
            'inactive': ['active', 'draft']
        }
        
        if new_status not in valid_status_transitions.get(property_obj.status, []):
            return False, f"Invalid status transition from {property_obj.status} to {new_status}"
        
        # Update status
        property_obj.status = new_status
        
        # Set verification info if applicable
        if new_status == 'active':
            property_obj.is_verified = True
            property_obj.verified_by = user
            property_obj.verification_date = timezone.now()
        
        property_obj.save()
        
        return True, "Property status updated successfully"
    
    except Property.DoesNotExist:
        return False, "Property not found"
    except Exception as e:
        logger.error(f"Error updating property status: {str(e)}")
        return False, "An error occurred while updating property status"