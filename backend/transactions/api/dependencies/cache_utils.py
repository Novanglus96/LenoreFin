from django.core.cache import cache
import json
from administration.api.dependencies.log_to_db import logToDB


# ===============================
# 🔑 Key Naming Helpers
# ===============================


def key_transactions_by_account(account_id):
    return f"transactions:{account_id}"


def key_reminder_transactions_by_account(account_id):
    return f"reminders:{account_id}"


def key_cc_transactions_by_account(account_id, funding):
    return f"cc:{account_id}:{funding}"


# ===============================
# ⚙️ Cache Setters & Getters
# ===============================


def get_cache(key):
    """Wrapper for cache.get with error handling."""
    try:
        return cache.get(key)
    except Exception as e:
        logToDB(
            f"Cache get failed for {key}: {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        return None


def set_cache(key, value, timeout=None):
    """
    Store a value indefinitely (timeout=None) unless you pass a TTL.
    Serializes complex objects as JSON automatically.
    """
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, default=str)
        cache.set(key, value, timeout=timeout)
        logToDB(
            f"Cached key: {key}",
            None,
            None,
            None,
            3001001,
            1,
        )
    except Exception as e:
        logToDB(
            f"Cache set failed for {key}: {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )


def delete_cache(key):
    """Safely delete a cache key."""
    try:
        cache.delete(key)
        logToDB(
            f"Cache invalidated: {key}",
            None,
            None,
            None,
            3001003,
            1,
        )
    except Exception as e:
        logToDB(
            f"Cache delete failed for {key}: {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
