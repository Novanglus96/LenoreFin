from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reminders.models import Reminder
from transactions.models import (
    ReminderCacheTransaction,
)
from django_q.tasks import async_task
from core.cache.helpers import delete_pattern
from core.cache.keys import (
    account_combined_transactions,
    account_reminder_transactions,
)


@receiver(post_save, sender=Reminder)
def update_reminder_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    async_task("transactions.tasks.update_reminder_cache", instance.id)


@receiver(post_delete, sender=Reminder)
def update_reminder_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    ReminderCacheTransaction.objects.filter(reminder=instance).delete()
    async_task(
        "transactions.tasks.update_cc_forecast_cache",
        instance.reminder_source_account.id,
    )
    async_task(
        "transactions.tasks.update_interest_forecast_cache",
        instance.reminder_source_account.id,
    )
    if instance.reminder_destination_account is not None:
        async_task(
            "transactions.tasks.update_cc_forecast_cache",
            instance.reminder_destination_account.id,
        )
        async_task(
            "transactions.tasks.update_interest_forecast_cache",
            instance.reminder_destination_account.id,
        )


@receiver(post_save, sender=Reminder)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    delete_pattern(
        account_reminder_transactions(instance.reminder_source_account.id)
    )
    delete_pattern(
        account_combined_transactions(instance.reminder_source_account.id)
    )
    if instance.reminder_destination_account is not None:
        delete_pattern(
            account_reminder_transactions(
                instance.reminder_destination_account.id
            )
        )
        delete_pattern(
            account_combined_transactions(
                instance.reminder_destination_account.id
            )
        )


@receiver(post_delete, sender=Reminder)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    delete_pattern(
        account_reminder_transactions(instance.reminder_source_account.id)
    )
    delete_pattern(
        account_combined_transactions(instance.reminder_source_account.id)
    )
    if instance.reminder_destination_account is not None:
        delete_pattern(
            account_reminder_transactions(
                instance.reminder_destination_account.id
            )
        )
        delete_pattern(
            account_combined_transactions(
                instance.reminder_destination_account.id
            )
        )
