from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reminders.models import Reminder
from transactions.models import (
    ReminderCacheTransaction,
)
from django_q.tasks import async_task
from core.cache.helpers import delete_pattern
from core.cache.keys import (
    account_all,
    account_combined_transactions,
    account_reminder_transactions,
)


@receiver(post_save, sender=Reminder)
def update_and_invalidate_cache_on_save(sender, instance, **kwargs):
    async_task("transactions.tasks.update_reminder_cache", instance.id)
    delete_pattern(
        account_reminder_transactions(instance.reminder_source_account.id)
    )
    delete_pattern(
        account_combined_transactions(instance.reminder_source_account.id)
    )
    if instance.reminder_destination_account is not None:
        delete_pattern(
            account_reminder_transactions(instance.reminder_destination_account.id)
        )
        delete_pattern(
            account_combined_transactions(instance.reminder_destination_account.id)
        )


@receiver(post_delete, sender=Reminder)
def update_and_invalidate_cache_on_delete(sender, instance, **kwargs):
    ReminderCacheTransaction.objects.filter(reminder=instance).delete()
    source = instance.reminder_source_account
    delete_pattern(account_reminder_transactions(source.id))
    delete_pattern(account_combined_transactions(source.id))
    # If source is a CC account, its funding account holds the payment forecast —
    # clear that cache too so it doesn't serve stale payment entries.
    if source.funding_account_id:
        delete_pattern(account_all(source.funding_account_id))
    async_task(
        "transactions.tasks.update_cc_forecast_cache",
        source.id,
    )
    async_task(
        "transactions.tasks.update_interest_forecast_cache",
        source.id,
    )
    if instance.reminder_destination_account is not None:
        dest = instance.reminder_destination_account
        delete_pattern(account_reminder_transactions(dest.id))
        delete_pattern(account_combined_transactions(dest.id))
        if dest.funding_account_id:
            delete_pattern(account_all(dest.funding_account_id))
        async_task(
            "transactions.tasks.update_cc_forecast_cache",
            dest.id,
        )
        async_task(
            "transactions.tasks.update_interest_forecast_cache",
            dest.id,
        )
