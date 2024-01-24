from django_q.tasks import async_task, result, schedule
import arrow
from api.models import Message
from django_q.models import Schedule
from datetime import date


# Task for sending messages
def create_message(message_text):
    message_obj = Message.objects.create(
        message_date=date.today().strftime("%Y-%m-%d"),
        message=message_text,
        unread=True
    )
# TODO: Task for converting reminders to transactions
# TODO: Task to look for negative dips
# TODO: Task to look for under threshold
# TODO: Task to update Credit Card specific information