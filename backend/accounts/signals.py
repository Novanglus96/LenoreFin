from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from accounts.models import Account
from django_q.tasks import async_task
from django.db.models import Q
from transactions.models import ForecastCacheTransaction


@receiver(post_save, sender=Account)
def update_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    if instance.account_type.id == 1:
        async_task(
            "transactions.tasks.update_cc_forecast_cache",
            instance.id,
        )


@receiver(post_delete, sender=Account)
def update_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    ForecastCacheTransaction.objects.filter(
        Q(source_account_id=instance.id) | Q(destination_account_id=instance.id)
    ).delete()
