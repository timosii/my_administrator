from aiocache.serializers import PickleSerializer
from sqlalchemy import select, update, delete, func, and_
from app.database.database import session_maker
from app.database.models.data import User, Check
from app.database.schemas.user_schema import UserCreate, UserUpdate, UserInDB
from app.database.schemas.check_schema import CheckInDB
from loguru import logger
from typing import Optional, List
from aiocache import cached, Cache


class UserRepo:
    def __init__(self):
        self.session_maker = session_maker
        self.cache = Cache(Cache.REDIS, namespace="user", serializer=PickleSerializer())

    async def add_user(self, user_create: UserCreate) -> UserInDB:
        async with self.session_maker() as session:
            new_user = User(**user_create.model_dump())
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            logger.info('add user')
            await self.clear_cache()
            return UserInDB.model_validate(new_user)

    @cached(ttl=3600, cache=Cache.REDIS, namespace='user', serializer=PickleSerializer())
    async def get_user_mo(self, user_id: int) -> str:
        query = select(User.mo_).filter_by(id=user_id)
        result = await self._get_scalar(query=query)
        logger.info('get user mo')
        return result

    async def user_exists(self, user_id: int) -> bool:
        query = select(User.id).filter_by(id=user_id)
        logger.info('is user exist')
        return await self._get_scalar(query=query)

    async def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()
            logger.info('get user by id')
            return UserInDB.model_validate(user) if user else None

    async def update_user(self, user_id: int, user_update: UserUpdate) -> None:
        logger.info('user updated')
        await self._update_field(user_id, **user_update.model_dump(exclude_unset=True))
        await self.clear_cache()

    async def delete_user(self, user_id: int) -> None:
        async with self.session_maker() as session:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(stmt)
            await session.commit()
            logger.info('user deleted')
            await self.clear_cache()

    async def get_all_users(self) -> List[UserInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            logger.info('get all users')
            return [UserInDB.model_validate(user) for user in users]

    @cached(ttl=300, cache=Cache.REDIS, namespace='user', serializer=PickleSerializer())
    async def get_user_active_checks(self, user_id: int) -> List[CheckInDB] | str:
        async with self.session_maker() as session:
            query = select(Check).where(
                and_(
                    Check.user_id == user_id,
                    Check.mfc_finish.is_(None)
                )
            )
            result = await session.execute(query)
            checks = result.scalars().all()
            logger.info('get user active checks')
            return [CheckInDB.model_validate(check) for check in checks] if checks else ''
    
    async def get_user_count(self) -> int:
        query = select(func.count()).select_from(User)
        logger.info('get user count')
        return await self._get_scalar(query=query) or 0

    @cached(ttl=300, cache=Cache.REDIS, namespace='user')
    async def is_admin(self, user_id: int) -> bool:
        query = select(User.is_admin).filter_by(id=user_id, is_archived=False)
        logger.info('is admin')
        return await self._get_scalar(query=query)

    @cached(ttl=300, cache=Cache.REDIS, namespace='user')
    async def is_mfc(self, user_id: int) -> bool:
        query = select(User.is_mfc).filter_by(id=user_id, is_archived=False)
        logger.info('is mfc')
        return await self._get_scalar(query=query)

    @cached(ttl=300, cache=Cache.REDIS, namespace='user')
    async def is_mfc_leader(self, user_id: int) -> bool:
        query = select(User.is_mfc_leader).filter_by(id=user_id, is_archived=False)
        logger.info('is mfc leader')
        return await self._get_scalar(query=query)
    
    @cached(ttl=300, cache=Cache.REDIS, namespace='user')
    async def is_mo_performer(self, user_id: int) -> bool:
        query = select(User.is_mo_performer).filter_by(id=user_id, is_archived=False)
        logger.info('is mo performer')
        return await self._get_scalar(query=query)
    
    @cached(ttl=300, cache=Cache.REDIS, namespace='user')
    async def is_mo_controler(self, user_id: int) -> bool:
        query = select(User.is_mo_controler).filter_by(id=user_id, is_archived=False)
        logger.info('is mo controler')
        return await self._get_scalar(query=query)

    async def _get_scalar(self, query) -> any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, user_id: int, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = update(User).where(User.id == user_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    async def clear_cache(self):
        pattern = "user:*"
        keys = await self.cache.raw("keys", pattern)
        for key in keys:
            await self.cache.delete(key)
        logger.info("Cache cleared")
