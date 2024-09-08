import asyncio
from typing import Any

from loguru import logger
from sqlalchemy import and_, delete, func, select, update

from app.config import settings
from app.database.database import session_maker
from app.database.models.data import User
from app.database.repositories.cache_config import cached, caches
from app.database.schemas.user_schema import UserCreate, UserInDB, UserUpdate

CACHE_EXPIRE_SHORT = settings.CACHE_SHORT
CACHE_EXPIRE_LONG = settings.CACHE_LONG


class UserRepo:
    def __init__(self):
        self.session_maker = session_maker
        self.cache = caches.get('default')

    async def add_user(self, user_create: UserCreate) -> UserInDB:
        async with self.session_maker() as session:
            new_user = User(**user_create.model_dump())
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            logger.info('add user')
            await self.clear_cache()
            return UserInDB.model_validate(new_user)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def get_user_mo(self, user_id: int) -> str:
        query = select(User.mo_).filter_by(user_id=user_id)
        result = await self._get_scalar(query=query)
        logger.info('get user mo')
        return result

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def get_user_fil(self, user_id: int) -> str:
        query = select(User.fil_).filter_by(user_id=user_id)
        result = await self._get_scalar(query=query)
        logger.info('get user fil')
        return result

    async def user_exists(self, user_id: int) -> bool:
        query = select(User.user_id).filter_by(user_id=user_id)
        logger.info('is user exist')
        return await self._get_scalar(query=query)

    async def get_user_by_id(self, user_id: int) -> UserInDB | None:
        async with self.session_maker() as session:
            result = await session.execute(select(User).filter_by(user_id=user_id))
            user = result.scalar_one_or_none()
            logger.info('get user by id')
            return UserInDB.model_validate(user) if user else None

    async def update_user(self, user_id: int, user_update: UserUpdate) -> None:
        logger.info('user updated')
        await self._update_field(user_id, **user_update.model_dump(exclude_unset=True))
        await self.clear_cache()

    async def delete_user(self, user_id: int) -> None:
        async with self.session_maker() as session:
            stmt = delete(User).where(User.user_id == user_id)
            await session.execute(stmt)
            await session.commit()
            logger.info('user deleted')
            await self.clear_cache()

    async def delete_all_users(self) -> None:
        async with self.session_maker() as session:
            stmt = delete(User)
            await session.execute(stmt)
            await session.commit()
            logger.info('ALL users deleted')
            await self.clear_cache()

    async def get_all_users(self) -> list[UserInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            logger.info('get all users')
            return [UserInDB.model_validate(user) for user in users]

    async def get_user_count(self) -> int:
        query = select(func.count()).select_from(User)
        logger.info('get user count')
        return await self._get_scalar(query=query) or 0

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def get_user_performer_by_fil(self, fil_: str) -> list[UserInDB] | None:
        async with self.session_maker() as session:
            query = select(User).where(
                and_(
                    User.fil_ == fil_,
                    User.is_mo_performer.is_(True),
                    User.is_archived.is_not(True)
                )
            )
            result = await session.execute(query)
            users = result.scalars().all()
            return [UserInDB.model_validate(user) for user in users] if users else None

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def get_avail_performer_by_fil(self, fil_: str) -> list[UserInDB] | None:
        async with self.session_maker() as session:
            query = select(User).where(
                and_(
                    User.fil_ == fil_,
                    User.is_mo_performer.is_(True),
                    User.is_archived.is_not(True),
                    User.is_avail.is_(True)
                )
            )
            result = await session.execute(query)
            users = result.scalars().all()
            return [UserInDB.model_validate(user) for user in users] if users else None

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def is_admin(self, user_id: int) -> bool:
        query = select(User.is_admin).filter_by(user_id=user_id, is_archived=False)
        logger.info('is admin')
        return await self._get_scalar(query=query)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def is_mfc(self, user_id: int) -> bool:
        query = select(User.is_mfc).filter_by(user_id=user_id, is_archived=False)
        logger.info('is mfc')
        return await self._get_scalar(query=query)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def is_mfc_leader(self, user_id: int) -> bool:
        query = select(User.is_mfc_leader).filter_by(user_id=user_id, is_archived=False)
        logger.info('is mfc leader')
        return await self._get_scalar(query=query)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def is_mfc_avail(self, user_id: int) -> bool:
        query = select(User.is_avail).filter_by(
            user_id=user_id,
            is_mfc=True,
            is_archived=False)
        logger.info('is mfc avail')
        return await self._get_scalar(query=query)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def is_mo_avail(self, user_id: int) -> bool:
        query = select(User.is_avail).filter_by(
            user_id=user_id,
            is_mfc=False,
            is_archived=False)
        logger.info('is mo avail')
        return await self._get_scalar(query=query)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def is_mo_performer(self, user_id: int) -> bool:
        query = select(User.is_mo_performer).filter_by(user_id=user_id, is_archived=False)
        logger.info('is mo performer')
        return await self._get_scalar(query=query)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='user')
    async def is_mo_controler(self, user_id: int) -> bool:
        query = select(User.is_mo_controler).filter_by(user_id=user_id, is_archived=False)
        logger.info('is mo controler')
        return await self._get_scalar(query=query)

    async def _get_scalar(self, query) -> Any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, user_id: int, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = update(User).where(User.user_id == user_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    async def clear_cache(self, namespace: str = 'user'):
        pattern = f'{namespace}:*'
        keys = await self.cache.raw('keys', pattern)
        if keys:
            await asyncio.gather(*(self.cache.delete(key) for key in keys))
        logger.info(f'Cache cleared (namespace: {namespace}, keys: {keys})')
