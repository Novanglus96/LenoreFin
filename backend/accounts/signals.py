from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from accounts.models import Account
from django_q.tasks import async_task


@receiver(post_save, sender=Account)
def update_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    pass


@receiver(post_delete, sender=Account)
def update_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    pass
