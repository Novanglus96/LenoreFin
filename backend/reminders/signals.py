from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reminders.models import Reminder
from transactions.models import (
    ReminderCacheTransaction,
)
from django_q.tasks import async_task


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
