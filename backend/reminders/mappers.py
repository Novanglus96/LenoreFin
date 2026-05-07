from reminders.dto import DomainRepeat, DomainReminder
from reminders.api.schemas.repeat import RepeatOut
from reminders.api.schemas.reminder import ReminderOut
from tags.mappers import domain_tag_to_schema
from accounts.mappers import domain_account_to_schema
from transactions.mappers import domain_transaction_type_to_schema


def domain_repeat_to_schema(
    repeat: DomainRepeat,
) -> RepeatOut:
    return RepeatOut(
        id=repeat.id,
        repeat_name=repeat.repeat_name,
        days=repeat.days,
        weeks=repeat.weeks,
        months=repeat.months,
        years=repeat.years,
    )


def domain_reminder_to_schema(reminder: DomainReminder) -> ReminderOut:
    return ReminderOut(
        id=reminder.id,
        tag=domain_tag_to_schema(reminder.tag),
        amount=reminder.amount,
        reminder_source_account=domain_account_to_schema(
            reminder.reminder_source_account
        ),
        description=reminder.description,
        transaction_type=domain_transaction_type_to_schema(
            reminder.transaction_type
        ),
        start_date=reminder.start_date,
        next_date=reminder.next_date,
        end_date=reminder.end_date,
        repeat=domain_repeat_to_schema(reminder.repeat),
        auto_add=reminder.auto_add,
        memo=reminder.memo,
    )
