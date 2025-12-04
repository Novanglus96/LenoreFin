from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reminders.models import Reminder
from transactions.models import (
    ReminderCacheTransaction,
)
from django_q.tasks import async_task
from backend.utils.cache import delete_pattern


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


@receiver(post_save, sender=Reminder)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    pattern = f"*account_transactions_{instance.reminder_source_account.id}*"
    delete_pattern(pattern)
    if instance.reminder_destination_account is not None:
        pattern = (
            f"*account_transactions_{instance.reminder_destination_account.id}*"
        )
        delete_pattern(pattern)


@receiver(post_delete, sender=Reminder)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    pattern = f"*account_transactions_{instance.reminder_source_account.id}*"
    delete_pattern(pattern)
    if instance.reminder_destination_account is not None:
        pattern = (
            f"*account_transactions_{instance.reminder_destination_account.id}*"
        )
        delete_pattern(pattern)
