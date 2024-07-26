from datetime import date, timedelta, datetime
import pytz
import os
from django.utils import timezone
from accounts.api.dependencies.get_forecast_start_date import (
    get_forecast_start_date,
)
from accounts.api.dependencies.get_forecast_end_date import (
    get_forecast_end_date,
)


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
