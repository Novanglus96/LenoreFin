from datetime import date, timedelta, datetime
from django.utils import timezone
import pytz
import os


def get_todays_date_timezone_adjusted(get_time: bool = False) -> date:
    """
    The function `get_todays_date_timezone_adjusted` returns today's date
    adjusted for the local timezone of the app. If `get_time` is set to True,
    it returns the current time instead.

    Args:
        get_time (bool): If True, returns the current time instead of the date. Defaults to False.

    Returns:
        date or datetime: Today's date or current time adjusted for the local timezone.
    """
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE", "UTC"))
    today_tz = today.astimezone(tz_timezone)

    if get_time:
        return today_tz
    else:
        return today_tz.date()
