from django.db.models.signals import post_save, post_delete, pre_save
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
    if instance.account_type.account_type == "Credit Card" and getattr(
        instance, "_should_update_cache", False
    ):
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
    }

    if relevant & set(instance.tracker.changed()):
        instance._should_update_cache = True
