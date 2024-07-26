from datetime import date, timedelta, datetime
import pytz
import os
from django.utils import timezone


def get_forecast_end_date(interval):
    """
    The function `get_forecast_end_date` calculates the end date of a forecast based on the given
    interval.

    Args:
        interval (int): The interval parameter represents the number of days from today's date for which
            you want to get the forecast end date.

    Returns:
        return: the end date of the forecast, which is calculated by adding the specified interval (in
            days) to the current date.
    """

    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    enddate = today_tz + timedelta(days=interval)
    return enddate
