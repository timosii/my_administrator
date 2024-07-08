from functools import wraps
from typing import Optional

from aiocache import caches

from app.config import settings

caches.set_config({
    'default': {
        'cache': 'aiocache.RedisCache',
        'endpoint': settings.REDIS_HOST,
        'port': 6379,
        'timeout': 1,
        'serializer': {
            'class': 'aiocache.serializers.PickleSerializer'
        },
        'plugins': [
            {'class': 'aiocache.plugins.HitMissRatioPlugin'},
            {'class': 'aiocache.plugins.TimingPlugin'}
        ]
    }
})

cache = caches.get('default')


def cached(ttl: str, namespace: Optional[str] = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f'{namespace}:{func.__name__}:{args}:{kwargs}' if namespace else f'{func.__name__}:{args}:{kwargs}'
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
