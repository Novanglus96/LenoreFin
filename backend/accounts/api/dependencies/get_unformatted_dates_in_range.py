from datetime import timedelta
from accounts.api.dependencies.get_forecast_start_date import (
    get_forecast_start_date,
)
from accounts.api.dependencies.get_forecast_end_date import (
    get_forecast_end_date,
)


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
