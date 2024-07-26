from datetime import date, timedelta, datetime
from django.utils import timezone
import pytz
import os


def get_todays_date_timezone_adjusted() -> date:
    """
    The function `get_todays_date_timezone_adjusted` returns todays date
    adjusted for the local timezone of the app.

    Args:

    Returns:
        date: todays date
    """
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz
