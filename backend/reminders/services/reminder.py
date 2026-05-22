from dateutil.relativedelta import relativedelta
from reminders.models import Reminder, ReminderExclusion, Repeat
from transactions.models import Transaction
from tags.api.dependencies.custom_tag import CustomTag
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.api.dependencies.create_transactions import create_transactions
from utils.dates import get_todays_date_timezone_adjusted
from datetime import date


class ReminderNotFound(Exception):
    pass


def add_reminder_transaction(reminder_id: int, transaction_date: date) -> None:
    try:
        reminder = Reminder.objects.get(id=reminder_id)
    except Reminder.DoesNotExist:
        raise ReminderNotFound(f"Reminder {reminder_id} not found")

    existing_transaction = Transaction.objects.filter(
        transaction_date=transaction_date,
        total_amount=reminder.amount,
        memo=reminder.memo,
        description=reminder.description,
        transaction_type=reminder.transaction_type,
        destination_account=reminder.reminder_destination_account,
        source_account=reminder.reminder_source_account,
    ).last()

    if not existing_transaction:
        destination_account_id = None
        if reminder.reminder_destination_account:
            destination_account_id = reminder.reminder_destination_account.id

        tag_obj = CustomTag(
            tag_name=None,
            tag_amount=reminder.amount,
            tag_id=reminder.tag.id,
            tag_full_toggle=True,
        )
        transaction = FullTransaction(
            transaction_date=transaction_date,
            total_amount=reminder.amount,
            status_id=1,
            memo=reminder.memo,
            description=reminder.description,
            edit_date=get_todays_date_timezone_adjusted(),
            add_date=get_todays_date_timezone_adjusted(),
            transaction_type_id=reminder.transaction_type.id,
            paycheck_id=None,
            source_account_id=reminder.reminder_source_account.id,
            destination_account_id=destination_account_id,
            tags=[tag_obj],
            checkNumber=None,
        )
        create_transactions([transaction])

    existing_exclusion = ReminderExclusion.objects.filter(
        reminder=reminder, exclude_date=transaction_date
    ).last()
    if not existing_exclusion:
        ReminderExclusion.objects.create(
            reminder=reminder,
            exclude_date=transaction_date,
        )

    repeat = Repeat.objects.get(id=reminder.repeat.id)
    next_date = reminder.next_date
    while True:
        if not ReminderExclusion.objects.filter(
            reminder_id=reminder.id, exclude_date=next_date
        ).first():
            break
        next_date += relativedelta(days=repeat.days)
        next_date += relativedelta(weeks=repeat.weeks)
        next_date += relativedelta(months=repeat.months)
        next_date += relativedelta(years=repeat.years)
    reminder.next_date = next_date
    if next_date is not None:
        reminder.start_date = next_date
    reminder.save()
