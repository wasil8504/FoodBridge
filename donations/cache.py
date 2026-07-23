from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from functools import wraps
import hashlib
import json


def cache_result(timeout=300, key_prefix=''):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'prefix': key_prefix
            }
            key_string = json.dumps(key_data, sort_keys=True, default=str)
            cache_key = f"{key_prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # If not in cache, execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def cache_queryset(timeout=300, key_prefix=''):
    """
    Decorator to cache queryset results.

    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'prefix': key_prefix
            }
            key_string = json.dumps(key_data, sort_keys=True, default=str)
            cache_key = f"{key_prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                # For querysets, we need to evaluate them to cache the actual results
                if hasattr(result, '_prefetch_related_lookups'):
                    return result  # Already evaluated
                return result

            # If not in cache, execute function
            result = func(*args, **kwargs)

            # For querysets, evaluate and cache the results
            if hasattr(result, 'all'):
                # It's a queryset, evaluate it
                result = list(result)

            # Store in cache
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate cache keys matching a pattern.
    Note: This requires a cache backend that supports deletion patterns
    (like redis with django-redis).
    """
    try:
        # For redis cache backend
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            # Fallback: clear entire cache (not ideal but safe)
            cache.clear()
    except Exception:
        # If pattern deletion fails, clear cache as fallback
        cache.clear()


def generate_cache_key(*args, **kwargs):
    """
    Generate a consistent cache key from arguments.
    """
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'short': 60,        # 1 minute
    'medium': 300,      # 5 minutes
    'long': 3600,       # 1 hour
    'very_long': 86400, # 24 hours
}


def cache_queryset_timeout(queryset_func, timeout_key='medium', key_prefix=''):
    """
    Cache a queryset with a specific timeout.

    Args:
        queryset_func: Function that returns a queryset
        timeout_key: Key from CACHE_TIMEOUTS dict
        key_prefix: Prefix for cache key
    """
    timeout = CACHE_TIMEOUTS.get(timeout_key, 300)

    @wraps(queryset_func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        key_data = {
            'func': queryset_func.__name__,
            'args': args,
            'kwargs': kwargs,
            'prefix': key_prefix
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        cache_key = f"{key_prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

        # Try to get from cache
        result = cache.get(cache_key)
        if result is not None:
            return result

        # If not in cache, execute function
        result = queryset_func(*args, **kwargs)

        # Evaluate queryset and cache results
        if hasattr(result, 'all'):
            result = list(result)

        # Store in cache
        cache.set(cache_key, result, timeout)
        return result

    return wrapper