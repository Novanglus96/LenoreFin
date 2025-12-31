from django.core.cache import cache
from django_redis import get_redis_connection


def cached(key_fn, ttl=300):
    """
    key_fn: either a string (static) or a function that receives (*args, **kwargs) and returns a string
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            key = key_fn(*args, **kwargs) if callable(key_fn) else key_fn

            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            value = fn(*args, **kwargs)
            cache.set(key, value, ttl)
            return value

        return wrapper

    return decorator


def delete_pattern(pattern: str):
    """
    Safely delete all Redis keys matching a wildcard pattern.
    Uses SCAN to avoid blocking Redis.
    """
    conn = get_redis_connection("default")
    for key in conn.scan_iter(f"*{pattern}*"):
        conn.delete(key)
