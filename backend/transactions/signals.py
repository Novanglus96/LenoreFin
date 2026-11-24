import threading

from django.db import transaction as db_transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Transaction, TransactionImage
from django_q.tasks import async_task
from core.cache.helpers import delete_pattern
from core.cache.keys import account_all
from core.broadcast import broadcast_invalidate


_TRANSACTION_BROADCAST_KEYS = [
    "transactions", "accounts", "account_forecast",
    "tag_graph", "tag_graph_items", "calculator",
    "expense_graph", "pay_graph", "budgets",
    "retirement_forecast", "retirement_transactions",
]


def _refresh_account(account_id):
    delete_pattern(account_all(account_id))
    async_task("transactions.tasks.update_cc_forecast_cache", account_id)
    async_task("transactions.tasks.update_interest_forecast_cache", account_id)


# Per-thread, because a request and a worker task each have their own database
# transaction and must not pool their pending work into one another's.
_state = threading.local()


def _pending():
    if not hasattr(_state, "accounts"):
        _state.accounts = set()
    return _state.accounts


def _queue_refresh(*account_ids):
    """Collect the accounts a write touched, to be handled once on commit.

    Firing per row is the problem this exists to solve. Every saved Transaction
    used to clear a cache, queue two django-q tasks and broadcast an
    invalidation of eleven query keys to every open browser — so an import or a
    reminder run touching a few hundred rows produced a few hundred broadcasts
    describing one change, and every connected client refetched eleven queries
    for each of them.

    Deferring to commit also closes a race the immediate version had: it told
    clients to refetch while the writing transaction was still open, so a fast
    client could read exactly the state the broadcast was announcing had
    changed.
    """
    touched = [a for a in account_ids if a is not None]
    if not touched:
        return
    _pending().update(touched)
    # Registered every time rather than guarded by a "already scheduled" flag.
    # A flag has to be cleared by the flush, and a rolled-back transaction
    # never flushes — it would have left the flag set and silently disabled
    # refreshes and broadcasts on that thread for the life of the process.
    # Django discards these callbacks on rollback, so the honest version is to
    # register one per row and let the first flush drain the set; the rest cost
    # a function call each and find nothing to do.
    # Both of a row's accounts go in one call deliberately. Outside an atomic
    # block `on_commit` runs immediately, so registering per account made a
    # single transfer broadcast twice — worse than the per-row version this
    # replaces. One registration per row means autocommit behaves exactly as
    # before, and a bulk write inside `atomic()` collapses to one.
    db_transaction.on_commit(_flush)


def reset_pending():
    """Drop anything queued but never committed.

    Django discards on_commit callbacks when a transaction rolls back, but the
    ids collected for them stay in the thread-local set and would ride along
    with the next successful write on that thread. In production that costs a
    redundant cache invalidation; in a test suite it makes one test's rollback
    visible to the next, which is how it was found.
    """
    _pending().clear()


def _flush():
    accounts = _pending()
    touched = set(accounts)
    accounts.clear()
    if not touched:
        return
    for account_id in touched:
        _refresh_account(account_id)
    # One broadcast for the whole write, however many rows it moved.
    broadcast_invalidate(_TRANSACTION_BROADCAST_KEYS)


@receiver(post_save, sender=Transaction)
def update_forecast_cache_on_save(sender, instance, **kwargs):
    _queue_refresh(instance.source_account_id, instance.destination_account_id)


@receiver(post_delete, sender=Transaction)
def update_forecast_cache_on_delete(sender, instance, **kwargs):
    _queue_refresh(instance.source_account_id, instance.destination_account_id)


@receiver(post_delete, sender=TransactionImage)
def delete_transaction_image_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
