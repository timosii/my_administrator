from aiocache.serializers import PickleSerializer
# import redis.asyncio as redis
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func, not_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.data import Check, ViolationFound
from app.database.models.dicts import Mos, Filials
from loguru import logger
from app.database.schemas.check_schema import CheckCreate, CheckUpdate, CheckInDB
from aiocache import cached, Cache
from app.config import settings

CACHE_EXPIRE_LONG=settings.CACHE_LONG


class HelpRepo:
    def __init__(self):
        self.session_maker = session_maker
        self.cache = Cache(Cache.REDIS, namespace='helpers', serializer=PickleSerializer(),endpoint=settings.REDIS_HOST)
    
    @cached(ttl=CACHE_EXPIRE_LONG, cache=Cache.REDIS, namespace='helpers', serializer=PickleSerializer(),endpoint=settings.REDIS_HOST)
    async def get_mo_by_fil(self, fil_: str):
        query = select(Filials.mo_).where(
            and_(
                Filials.fil_==fil_,
                )
            )
        logger.info('get mo by fil')
        return (
            await self._get_scalar(query=query)
        )
    
    async def mo_define_by_num(self, num: str):
        async with self.session_maker() as session:
            result = await session.execute(
                select(Mos.mo_).where(
                    and_(
                        func.split_part(Mos.mo_, ' ', 2) == num
                        )
                    )
                )
            logger.info('mo_define_by_num')
            res = result.scalars().all()
            logger.info(res)
            return res

    async def _get_scalar(self, query) -> any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, check_id: int, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = update(Check).where(Check.check_id == check_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()
            

    async def clear_cache(self):
        pattern = "check:*"
        keys = await self.cache.raw("keys", pattern)
        for key in keys:
            await self.cache.delete(key)
        logger.info("Cache cleared (keys: {})", keys)