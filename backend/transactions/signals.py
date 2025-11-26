from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Transaction
from transactions.models import ForecastCacheTransaction
from django_q.tasks import async_task


@receiver(post_save, sender=Transaction)
def update_forecast_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    async_task(
        "transactions.tasks.update_forecast_cache",
        instance.source_account.id,
        instance.destination_account.id,
    )


@receiver(post_delete, sender=Transaction)
def update_forecast_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    ForecastCacheTransaction.objects.filter(
        source_account=instance.source_account
    ).delete()
    ForecastCacheTransaction.objects.filter(
        destination_account=instance.destination_account
    ).delete()
