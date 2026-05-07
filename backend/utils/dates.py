from datetime import date, timedelta
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


def get_dates_in_range(start_interval, end_interval):
    """
    The function `get_dates_in_range` returns a list of dates in a specified range, formatted as month,
    day, and year.

    Args:
        start_interval (int): The start_interval parameter represents the starting point of the date range.
            It could be a specific date or a time interval.
        end_interval (int): The `end_interval` parameter represents the end of the date range for which you
            want to generate a list of dates.

    Returns:
        return: a list of dates in the format "Month Day, Year" that fall within the specified start and
            end intervals.
    """

    date_list = []
    current_date = get_forecast_start_date(start_interval)
    end_date = get_forecast_end_date(end_interval)

    while current_date <= end_date:
        date_list.append(current_date.strftime("%b %d, %y"))
        current_date += timedelta(days=1)

    return date_list


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


def get_unformatted_dates_in_range(start_interval, end_interval):
    """
    The function `get_unformatted_dates_in_range` returns a list of dates within a specified range with no
    formatting.

    Args:
        start_interval (int): The start date of the interval for which you want to get unformatted dates.
        end_interval (int): The `end_interval` parameter represents the end of the date range for which you
            want to get unformatted dates.

    Returns:
        return: a list of unformatted dates within the specified range.
    """

    date_list = []
    current_date = get_forecast_start_date(start_interval)
    end_date = get_forecast_end_date(end_interval)

    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    return date_list
