import asyncio
from typing import Any, Optional
from uuid import UUID

from loguru import logger
from sqlalchemy import and_, delete, func, select, update

from app.config import settings
from app.database.database import session_maker
from app.database.models.data import Check, ViolationFound
from app.database.repositories.cache_config import cached, caches
from app.database.schemas.check_schema import (
    CheckCreate,
    CheckInDB,
    CheckTestCreate,
    CheckUpdate,
)

CACHE_EXPIRE_SHORT = settings.CACHE_SHORT
CACHE_EXPIRE_LONG = settings.CACHE_LONG


class CheckRepo:
    def __init__(self):
        self.session_maker = session_maker
        self.cache = caches.get('default')

    async def add_check(self, check_create: CheckCreate | CheckTestCreate) -> CheckInDB:
        async with self.session_maker() as session:
            new_check = Check(**check_create.model_dump())
            session.add(new_check)
            await session.commit()
            await session.refresh(new_check)
            logger.info('check adding to db')
            await self.clear_cache()
            return CheckInDB.model_validate(new_check)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def check_exists(self, check_id: UUID) -> bool:
        query = select(Check.check_id).filter_by(check_id=check_id)
        return await self._get_scalar(query=query)

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_check_by_id(self, check_id: UUID) -> CheckInDB:
        async with self.session_maker() as session:
            result = await session.execute(select(Check).filter_by(check_id=check_id))
            check = result.scalar_one()
            logger.info('get check by id')
            return CheckInDB.model_validate(check)

    async def update_check(self, check_id: UUID, check_update: CheckUpdate) -> None:
        await self._update_field(
            check_id, **check_update.model_dump(exclude_unset=True)
        )
        logger.info('check updated')
        await self.clear_cache()

    async def delete_check(self, check_id: UUID) -> None:
        async with self.session_maker() as session:
            stmt = delete(Check).where(Check.check_id == check_id)
            await session.execute(stmt)
            await session.commit()
            logger.info('check deleted')
            await self.clear_cache()

    async def delete_all_checks(self) -> None:
        async with self.session_maker() as session:
            stmt = delete(Check)
            await session.execute(stmt)
            await session.commit()
            logger.info('ALL checks deleted')
            await self.clear_cache()

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_all_checks(self) -> list[CheckInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(Check))
            checks = result.scalars().all()
            logger.info('get all checks')
            return [CheckInDB.model_validate(check) for check in checks]

    async def get_mfc_all_active_checks(self) -> list[CheckInDB] | None:
        async with self.session_maker() as session:
            query = select(Check).where(
                and_(
                    Check.mfc_finish.is_(None),
                    # Check.is_task.is_(False)
                )
            )
            result = await session.execute(query)
            checks = result.scalars().all()
            logger.info('get all active checks')
            return [CheckInDB.model_validate(check) for check in checks] if checks else None

    async def get_mfc_fil_active_checks(self, fil_: str) -> list[CheckInDB] | None:
        async with self.session_maker() as session:
            query = select(Check).where(
                and_(
                    Check.fil_ == fil_,
                    Check.mfc_finish.is_(None),
                    Check.is_task.is_(False)
                )
            )
            result = await session.execute(query)
            checks = result.scalars().all()
            logger.info('get fil active checks')
            return [CheckInDB.model_validate(check) for check in checks] if checks else None

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_violations_found_count_by_check(self, check_id: UUID) -> int:
        query = select(func.count()).select_from(ViolationFound).where(
            and_(
                ViolationFound.check_id == check_id,
                ViolationFound.violation_fixed.is_(None),
                ViolationFound.is_pending.is_(False)
            )
        )
        logger.info('get violations found count by check')
        return (
            await self._get_scalar(query=query) or 0
        )

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_all_violations_found_count_by_check(self, check_id: UUID) -> int:
        query = select(func.count()).select_from(ViolationFound).where(
            and_(
                ViolationFound.check_id == check_id,
            )
        )
        logger.info('get all violations found count by check')
        return (
            await self._get_scalar(query=query) or 0
        )

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_all_violations_found_dict_ids_for_check(self, check_id: UUID) -> Optional[list[int]]:
        async with self.session_maker() as session:
            query = select(ViolationFound.violation_dict_id).select_from(ViolationFound).where(
                and_(
                    ViolationFound.check_id == check_id,
                )
            )
            result = await session.execute(query)
            violation_dict_ids = result.scalars().all()
            logger.info('get violations found dict_ids for check')
            return violation_dict_ids

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_all_active_checks_by_fil(
        self, fil_: str
    ) -> Optional[list[CheckInDB]]:
        async with self.session_maker() as session:
            query = select(Check).where(
                and_(
                    Check.fil_ == fil_,
                    Check.mfc_finish.is_not(None),
                    Check.mo_finish.is_(None),
                    Check.is_task.is_(False)
                )
            )
            result = await session.execute(query)
            checks = result.scalars().all()
            logger.info('get all active checks by fil')
            return (
                [CheckInDB.model_validate(check) for check in checks]
                if checks
                else None
            )

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_all_active_checks(
            self) -> Optional[list[CheckInDB]]:
        async with self.session_maker() as session:
            query = select(Check).where(
                and_(
                    Check.mfc_finish.is_not(None),
                    Check.mo_finish.is_(None),
                    # Check.is_task.is_(False)
                )
            )
            result = await session.execute(query)
            checks = result.scalars().all()
            logger.info('get all active checks')
            return (
                [CheckInDB.model_validate(check) for check in checks]
                if checks
                else None
            )

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_checks_count(self) -> int:
        query = select(func.count()).select_from(Check)
        logger.info('get checks count')
        return await self._get_scalar(query=query) or 0

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='check')
    async def get_checks_by_mfc_user(self, user_id: int) -> list[CheckInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(Check).filter_by(mfc_user_id=user_id))
            checks = result.scalars().all()
            logger.info('get checks by user')
            return [CheckInDB.model_validate(check) for check in checks]

    async def _get_scalar(self, query) -> Any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, check_id: UUID, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = update(Check).where(Check.check_id == check_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    async def clear_cache(self, namespace: str = 'check'):
        pattern = f'{namespace}:*'
        keys = await self.cache.raw('keys', pattern)
        if keys:
            await asyncio.gather(*(self.cache.delete(key) for key in keys))
        logger.info(f'Cache cleared (namespace: {namespace}, keys: {keys})')
