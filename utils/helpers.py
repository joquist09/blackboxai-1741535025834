from datetime import datetime, timedelta
from typing import Dict, Optional, Union
import logging
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt (datetime): Datetime object to format
        format_str (str): Format string to use
        
    Returns:
        str: Formatted datetime string
    """
    try:
        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"Error formatting datetime: {str(e)}")
        return str(dt)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M") -> Optional[datetime]:
    """
    Parse a datetime string to datetime object.
    
    Args:
        date_str (str): Datetime string to parse
        format_str (str): Format string to use
        
    Returns:
        Optional[datetime]: Parsed datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, format_str)
    except Exception as e:
        logger.error(f"Error parsing datetime string: {str(e)}")
        return None

def calculate_booking_cost(duration_minutes: int, price_per_hour: float) -> float:
    """
    Calculate the cost of a court booking.
    
    Args:
        duration_minutes (int): Duration in minutes
        price_per_hour (float): Price per hour
        
    Returns:
        float: Total cost
    """
    try:
        hours = duration_minutes / 60
        return round(hours * price_per_hour, 2)
    except Exception as e:
        logger.error(f"Error calculating booking cost: {str(e)}")
        return 0.0

def is_valid_booking_time(booking_time: datetime, 
                         duration_minutes: int,
                         opening_time: str = "06:00",
                         closing_time: str = "22:00") -> bool:
    """
    Check if a booking time is valid.
    
    Args:
        booking_time (datetime): Proposed booking time
        duration_minutes (int): Duration of booking in minutes
        opening_time (str): Facility opening time (HH:MM)
        closing_time (str): Facility closing time (HH:MM)
        
    Returns:
        bool: True if booking time is valid
    """
    try:
        # Convert opening and closing times to datetime objects for today
        today = datetime.now().date()
        opening_dt = datetime.combine(today, 
                                    datetime.strptime(opening_time, "%H:%M").time())
        closing_dt = datetime.combine(today, 
                                    datetime.strptime(closing_time, "%H:%M").time())
        
        # Calculate booking end time
        booking_end = booking_time + timedelta(minutes=duration_minutes)
        
        # Check if booking is in the future
        if booking_time <= datetime.now():
            return False
        
        # Check if booking is within operating hours
        booking_time_of_day = booking_time.time()
        booking_end_time_of_day = booking_end.time()
        
        if (booking_time_of_day < datetime.strptime(opening_time, "%H:%M").time() or
            booking_end_time_of_day > datetime.strptime(closing_time, "%H:%M").time()):
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating booking time: {str(e)}")
        return False

def format_price(amount: Union[int, float]) -> str:
    """
    Format a price amount with currency symbol.
    
    Args:
        amount (Union[int, float]): Price amount
        
    Returns:
        str: Formatted price string
    """
    try:
        return f"${amount:.2f}"
    except Exception as e:
        logger.error(f"Error formatting price: {str(e)}")
        return f"${float(amount):.2f}"

def admin_required(f):
    """
    Decorator to require admin access for a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def handle_booking_conflict(booking_time: datetime, 
                          court_id: int, 
                          duration_minutes: int) -> bool:
    """
    Check for booking conflicts.
    
    Args:
        booking_time (datetime): Proposed booking time
        court_id (int): ID of the court
        duration_minutes (int): Duration of booking in minutes
        
    Returns:
        bool: True if there is a conflict
    """
    from models.models import Booking
    
    try:
        booking_end = booking_time + timedelta(minutes=duration_minutes)
        
        # Check for overlapping bookings
        conflicting_bookings = Booking.query.filter(
            Booking.tennis_court_id == court_id,
            Booking.status != 'cancelled',
            # Check if the new booking overlaps with existing bookings
            ((Booking.booking_time <= booking_time) & 
             (Booking.booking_time + timedelta(minutes=Booking.duration) > booking_time)) |
            ((Booking.booking_time < booking_end) & 
             (Booking.booking_time + timedelta(minutes=Booking.duration) >= booking_end))
        ).count()
        
        return conflicting_bookings > 0
        
    except Exception as e:
        logger.error(f"Error checking booking conflicts: {str(e)}")
        return True  # Err on the side of caution

def log_error(error: Exception, context: Dict = None):
    """
    Log an error with optional context.
    
    Args:
        error (Exception): The error to log
        context (Dict, optional): Additional context information
    """
    try:
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg += f" Context: {context}"
        logger.error(error_msg, exc_info=True)
    except Exception as e:
        logger.error(f"Error in error logging: {str(e)}")

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    import html
    try:
        return html.escape(text.strip())
    except Exception as e:
        logger.error(f"Error sanitizing input: {str(e)}")
        return ""
