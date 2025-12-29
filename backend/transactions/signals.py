from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Transaction
from django_q.tasks import async_task
from backend.utils.cache import delete_pattern


@receiver(post_save, sender=Transaction)
def update_forecast_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    async_task(
        "transactions.tasks.update_cc_forecast_cache",
        instance.source_account.id,
    )
    if instance.destination_account is not None:
        async_task(
            "transactions.tasks.update_cc_forecast_cache",
            instance.destination_account.id,
        )


@receiver(post_delete, sender=Transaction)
def update_forecast_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    async_task(
        "transactions.tasks.update_cc_forecast_cache",
        instance.source_account.id,
    )
    if instance.destination_account is not None:
        async_task(
            "transactions.tasks.update_cc_forecast_cache",
            instance.destination_account.id,
        )


@receiver(post_save, sender=Transaction)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    pattern = f"*account_{instance.source_account.id}_transaction_transactions*"
    delete_pattern(pattern)
    pattern = f"*account_{instance.source_account.id}_transactions*"
    delete_pattern(pattern)
    if instance.destination_account is not None:
        pattern = f"*account_{instance.destination_account.id}_transaction_transactions*"
        delete_pattern(pattern)
        pattern = f"*account_{instance.destination_account.id}_transactions*"
        delete_pattern(pattern)


@receiver(post_delete, sender=Transaction)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    pattern = f"*account_{instance.source_account.id}_transaction_transactions*"
    delete_pattern(pattern)
    pattern = f"*account_{instance.source_account.id}_transactions*"
    delete_pattern(pattern)
    if instance.destination_account is not None:
        pattern = f"*account_{instance.destination_account.id}_transaction_transactions*"
        delete_pattern(pattern)
        pattern = f"*account_{instance.destination_account.id}_transactions*"
        delete_pattern(pattern)
