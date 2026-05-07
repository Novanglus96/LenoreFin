from datetime import datetime

from dateutil.relativedelta import relativedelta

from reminders.models import Repeat
from utils.dates import get_todays_date_timezone_adjusted


def calculate_repeat_window(start_date: datetime, repeat: Repeat) -> tuple:
    """
    Calculate the current repeat window (start and end date) based on the Repeat object.

    Args:
        start_date (datetime or date): The date when the repetition started.
        repeat (Repeat): The Repeat object containing the interval (days, weeks, months, years).

    Returns:
        tuple: A tuple of (window_start, window_end) for the current repeat window.
    """
    # Combine repeat fields into a single period using relativedelta
    total_period = relativedelta(
        days=repeat.days,
        weeks=repeat.weeks,
        months=repeat.months,
        years=repeat.years,
    )

    # Get the current date (timezone-adjusted)
    today = get_todays_date_timezone_adjusted()

    # Calculate how many total periods have passed since the start date
    current_period_start = start_date

    while current_period_start + total_period <= today:
        current_period_start += total_period

    window_start = current_period_start
    window_end = window_start + total_period + relativedelta(days=-1)

    return window_start, window_end
