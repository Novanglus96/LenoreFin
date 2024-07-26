from datetime import date, timedelta, datetime
import pytz
import os
from django.utils import timezone


def get_forecast_start_date(interval):
    """
    The function `get_forecast_start_date` returns the start date for a forecast based on the given
    interval.

    Args:
        interval (int): The interval parameter represents the number of days in the past from today's date.

    Returns:
        return: the start date for a forecast based on the given interval.
    """

    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    startdate = today_tz - timedelta(days=interval)
    return startdate
