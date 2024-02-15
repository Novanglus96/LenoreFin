"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django_q.tasks import async_task, result, schedule
import arrow
from api.models import Message
from django_q.models import Schedule
from datetime import date


def create_message(message_text):
    """
    The function `create_message` creates a Message object for
    displaying a message alert in the app inbox.

    Args:
        message_text (str): The text of the message
    """

    message_obj = Message.objects.create(
        message_date=date.today().strftime("%Y-%m-%d"),
        message=message_text,
        unread=True,
    )


# TODO: Task for converting reminders to transactions
# TODO: Task to look for negative dips
# TODO: Task to look for under threshold
# TODO: Task to update Credit Card specific information
