import asyncio
from typing import Any

from loguru import logger
from sqlalchemy import and_, func, select, update

from app.config import settings
from app.database.database import session_maker
from app.database.models.data import Check
from app.database.models.dicts import Filials, Mos
from app.database.repositories.cache_config import cached, caches

CACHE_EXPIRE_LONG = settings.CACHE_LONG


class HelpRepo:
    def __init__(self):
        self.session_maker = session_maker
        self.cache = caches.get('default')

    @cached(ttl=CACHE_EXPIRE_LONG, namespace='helpers')
    async def get_mo_by_fil(self, fil_: str) -> str:
        query = select(Filials.mo_).where(
            and_(
                Filials.fil_ == fil_,
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
            return res

    async def _get_scalar(self, query) -> Any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, check_id: int, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = update(Check).where(Check.check_id == check_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    async def clear_cache(self, namespace: str = 'helpers'):
        pattern = f'{namespace}:*'
        keys = await self.cache.raw('keys', pattern)
        if keys:
            await asyncio.gather(*(self.cache.delete(key) for key in keys))
        logger.info(f'Cache cleared (namespace: {namespace}, keys: {keys})')
