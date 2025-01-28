from aiocache import Cache
from aiocache.serializers import JsonSerializer

class CacheManager:
    def __init__(self, cache_type=Cache.MEMORY, **kwargs):
        self.cache = Cache.from_url(cache_type, serializer=JsonSerializer(), **kwargs)

    async def get(self, key):
        """
        Получить данные из кеша по ключу.
        """
        return await self.cache.get(key)

    async def add(self, key, value, ttl=None):
        """
        Добавить данные в кеш. Если ключ уже существует, не делать ничего.
        ttl - время жизни в секундах.
        """
        return await self.cache.add(key, value, ttl=ttl)

    async def set(self, key, value, ttl=None):
        """
        Обновить данные в кеше по ключу. Если ключа нет, он будет создан.
        ttl - время жизни в секундах.
        """
        return await self.cache.set(key, value, ttl=ttl)

    async def delete(self, key):
        """
        Удалить данные из кеша по ключу.
        """
        return await self.cache.delete(key)