"""
Caching utilities for ConstructOS.
Provides distributed caching for frequently accessed data.
"""
from functools import wraps
from typing import Any, Optional, Callable
import json
import hashlib

from django.core.cache import cache
from django.conf import settings


CACHE_TIMEOUTS = {
    'short': 60,
    'medium': 300,
    'long': 3600,
    'day': 86400,
    'user_roles': 600,
    'product_pricing': 300,
    'account_data': 300,
    'project_summary': 120,
}


def make_cache_key(*args, prefix: str = 'constructos') -> str:
    key_data = ':'.join(str(arg) for arg in args)
    if len(key_data) > 200:
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    return f"{prefix}:{key_data}"


def get_cached(key: str, default: Any = None) -> Any:
    try:
        return cache.get(key, default)
    except Exception:
        return default


def set_cached(key: str, value: Any, timeout: Optional[int] = None) -> bool:
    try:
        cache.set(key, value, timeout or CACHE_TIMEOUTS['medium'])
        return True
    except Exception:
        return False


def delete_cached(key: str) -> bool:
    try:
        cache.delete(key)
        return True
    except Exception:
        return False


def delete_pattern(pattern: str) -> int:
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        keys = redis_conn.keys(f'*{pattern}*')
        if keys:
            return redis_conn.delete(*keys)
        return 0
    except Exception:
        return 0


def cache_result(timeout: int = None, key_prefix: str = None):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prefix = key_prefix or func.__name__
            cache_key = make_cache_key(prefix, *args, *sorted(kwargs.items()))
            
            result = get_cached(cache_key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            set_cached(cache_key, result, timeout or CACHE_TIMEOUTS['medium'])
            return result
        return wrapper
    return decorator


def get_user_roles(user_id: str) -> list:
    cache_key = make_cache_key('user_roles', user_id)
    roles = get_cached(cache_key)
    if roles is None:
        from backend.apps.core.models import User
        try:
            user = User.objects.get(id=user_id)
            roles = user.roles
            set_cached(cache_key, roles, CACHE_TIMEOUTS['user_roles'])
        except User.DoesNotExist:
            roles = []
    return roles


def invalidate_user_cache(user_id: str) -> None:
    cache_key = make_cache_key('user_roles', user_id)
    delete_cached(cache_key)


def get_product_price(product_id: str) -> Optional[dict]:
    cache_key = make_cache_key('product_price', product_id)
    price_data = get_cached(cache_key)
    if price_data is None:
        from backend.apps.erp.models import Product
        try:
            product = Product.objects.get(id=product_id)
            price_data = {
                'id': str(product.id),
                'name': product.name,
                'unit_price': str(product.unit_price),
                'currency': 'ZAR',
            }
            set_cached(cache_key, price_data, CACHE_TIMEOUTS['product_pricing'])
        except Product.DoesNotExist:
            return None
    return price_data


def invalidate_product_cache(product_id: str) -> None:
    cache_key = make_cache_key('product_price', product_id)
    delete_cached(cache_key)


def get_account_summary(account_id: str) -> Optional[dict]:
    cache_key = make_cache_key('account_summary', account_id)
    summary = get_cached(cache_key)
    if summary is None:
        from backend.apps.crm.models import Account
        try:
            account = Account.objects.get(id=account_id)
            summary = {
                'id': str(account.id),
                'name': account.name,
                'type': account.type,
                'status': account.status,
                'payment_terms': account.payment_terms,
            }
            set_cached(cache_key, summary, CACHE_TIMEOUTS['account_data'])
        except Account.DoesNotExist:
            return None
    return summary


def invalidate_account_cache(account_id: str) -> None:
    cache_key = make_cache_key('account_summary', account_id)
    delete_cached(cache_key)


class CacheStats:
    @staticmethod
    def get_info() -> dict:
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection('default')
            info = redis_conn.info()
            return {
                'connected': True,
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_days': info.get('uptime_in_days', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
            }
