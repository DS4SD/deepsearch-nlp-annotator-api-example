import logging
from typing import Optional
from nlp_annotator_api.config.config import Config, RedisCacheConfig
import aioredis

_log = logging.getLogger(__name__)


class RedisCache:
    _redis: aioredis.Redis

    def __init__(self, config: RedisCacheConfig) -> None:
        self.config = config

    def _format_key(self, key: str) -> str:
        if not self.config.prefix:
            return key

        return f"{self.config.prefix}.{key}"

    async def set(self, key: str, value: str):
        await self._redis.set(self._format_key(key), value, ex=self.config.ttl)

    async def get(self, key: str) -> Optional[str]:
        value = await self._redis.get(self._format_key(key))

        return value

    async def __aenter__(self):
        self._redis = aioredis.from_url(self.config.url)
        _log.info("Set up Redis cache")

        return self

    async def __aexit__(self, *args, **kwargs):
        _log.info("Closed Redis cache")

        await self._redis.close()


def redis_cache_factory(config: Config):
    async def redis_cache(app_instance):
        if config.redis_cache is None:
            _log.info("Redis cache not set")
            
            app_instance["redis_cache"] = None
            yield
        else:
            _log.info("Adding Redis cache")

            async with RedisCache(config.redis_cache) as cache:
                app_instance["redis_cache"] = cache
                yield

    return redis_cache
