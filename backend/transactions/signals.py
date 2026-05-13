from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Transaction
from django_q.tasks import async_task
from core.cache.helpers import delete_pattern
from core.cache.keys import account_all


def _refresh_account(account_id):
    delete_pattern(account_all(account_id))
    async_task("transactions.tasks.update_cc_forecast_cache", account_id)
    async_task("transactions.tasks.update_interest_forecast_cache", account_id)


@receiver(post_save, sender=Transaction)
def update_forecast_cache_on_save(sender, instance, **kwargs):
    _refresh_account(instance.source_account_id)
    if instance.destination_account_id is not None:
        _refresh_account(instance.destination_account_id)


@receiver(post_delete, sender=Transaction)
def update_forecast_cache_on_delete(sender, instance, **kwargs):
    _refresh_account(instance.source_account_id)
    if instance.destination_account_id is not None:
        _refresh_account(instance.destination_account_id)
