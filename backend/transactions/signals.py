from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Transaction
from django_q.tasks import async_task
from core.cache.helpers import delete_pattern
from core.cache.keys import (
    account_financials,
    account_real_transactions,
    account_all_balances,
    account_combined_transactions,
)


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
    delete_pattern(account_combined_transactions(instance.source_account.id))
    delete_pattern(account_all_balances(instance.source_account.id))
    delete_pattern(account_financials(instance.source_account.id))
    delete_pattern(account_real_transactions(instance.source_account.id))
    if instance.destination_account is not None:
        delete_pattern(
            account_combined_transactions(instance.destination_account.id)
        )
        delete_pattern(account_all_balances(instance.destination_account.id))
        delete_pattern(account_financials(instance.destination_account.id))
        delete_pattern(
            account_real_transactions(instance.destination_account.id)
        )


@receiver(post_delete, sender=Transaction)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    delete_pattern(account_combined_transactions(instance.source_account.id))
    delete_pattern(account_all_balances(instance.source_account.id))
    delete_pattern(account_financials(instance.source_account.id))
    delete_pattern(account_real_transactions(instance.source_account.id))
    pattern = f"*account_{instance.source_account.id}_transactions*"
    delete_pattern(pattern)
    if instance.destination_account is not None:
        delete_pattern(account_combined_transactions(instance.destination_account.id))
        delete_pattern(account_all_balances(instance.destination_account.id))
        delete_pattern(account_financials(instance.destination_account.id))
        delete_pattern(
            account_real_transactions(instance.destination_account.id)
        )
