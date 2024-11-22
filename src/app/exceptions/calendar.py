# app/exceptions/calendar.py
class CalendarException(Exception):
    """Base exception class for calendar-related errors."""
    pass

class CalendarException:
    FETCH_ERROR = "Failed to fetch calendar events."
    API_ERROR = "Error returned from the Microsoft Graph API."
    TOKEN_ERROR = "Error fetching or refreshing access token."
