from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from accounts.models import Account
from django.db.models import Q
from transactions.models import ForecastCacheTransaction
from core.cache.helpers import delete_pattern
from core.cache.keys import (
    account_cleared_balance,
    account_financials,
    account_forecast_transactions,
    account_pending_balance,
    account_combined_transactions,
    account_all,
)


@receiver(post_save, sender=Account)
def update_cache_on_save(sender, instance, **kwargs):
    """
    Update the reminder scratch/cache table when a Reminder is created or updated.
    """
    if getattr(instance, "_should_update_cache", False):
        if instance.account_type.account_type == "Credit Card":
            from transactions.tasks import update_cc_forecast_cache
            update_cc_forecast_cache(instance.id)
            delete_pattern(account_forecast_transactions(instance.id))
        elif instance.account_type.slug in {"savings", "investment"}:
            from transactions.tasks import update_interest_forecast_cache
            update_interest_forecast_cache(instance.id)
            delete_pattern(account_forecast_transactions(instance.id))
    delete_pattern(account_combined_transactions(instance.id))
    delete_pattern(account_cleared_balance(instance.id))
    delete_pattern(account_financials(instance.id))
    delete_pattern(account_pending_balance(instance.id))
    # Also invalidate the parent's financials cache if this is a child account
    if instance.parent_account_id:
        delete_pattern(account_financials(instance.parent_account_id))
        delete_pattern(account_combined_transactions(instance.parent_account_id))


@receiver(post_delete, sender=Account)
def update_cache_on_delete(sender, instance, **kwargs):
    """
    Remove entries from the reminder scratch table when a Reminder is deleted.
    """
    ForecastCacheTransaction.objects.filter(
        Q(source_account_id=instance.id) | Q(destination_account_id=instance.id)
    ).delete()
    delete_pattern(account_all(instance.id))


@receiver(pre_save, sender=Account)
def detect_relevant_changes(sender, instance, **kwargs):
    instance._should_update_cache = False

    if not instance.pk:
        instance._should_update_cache = True
        return

    relevant = {
        "annual_rate",
        "opening_balance",
        "statement_cycle_length",
        "statement_cycle_period",
        "archive_balance",
        "funding_account_id",
        "calculate_payments",
        "calculate_interest",
        "payment_strategy",
        "payment_amount",
        "minimum_payment_amount",
        "statement_day",
        "due_day",
        "pay_day",
        "interest_deposit_day",
        "parent_account_id",
        "interest_child_account_id",
    }

    if relevant & set(instance.tracker.changed()):
        instance._should_update_cache = True
