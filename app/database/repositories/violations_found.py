from aiocache.serializers import PickleSerializer
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func, and_, text
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.data import ViolationFound, Check
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundUpdate,
    ViolationFoundInDB
)
from loguru import logger
from aiocache import cached, Cache
from app.config import settings


class ViolationFoundRepo:
    def __init__(self):
        self.session_maker = session_maker
        self.cache = Cache(Cache.REDIS, namespace='violation_found', serializer=PickleSerializer(), endpoint=settings.REDIS_HOST)

    async def add_violation_found(
        self, violation_create: ViolationFoundCreate
    ) -> ViolationFoundInDB:
        async with self.session_maker() as session:
            new_violation = ViolationFound(**violation_create.model_dump())
            session.add(new_violation)
            await session.commit()
            await session.refresh(new_violation)
            logger.info('add violation found')
            await self.clear_cache()
            return ViolationFoundInDB.model_validate(new_violation)

    @cached(ttl=300, cache=Cache.REDIS, namespace='violation_found', endpoint=settings.REDIS_HOST)
    async def violation_found_exists(self, violation_id: int) -> bool:
        query = select(ViolationFound.id).filter_by(violation_found_id=violation_id)
        logger.info('is violation found exist')
        return await self._get_scalar(query=query)

    @cached(ttl=300, cache=Cache.REDIS, namespace='violation_found', serializer=PickleSerializer(), endpoint=settings.REDIS_HOST)
    async def get_violation_found_by_id(
        self, violation_found_id: int
    ) -> Optional[ViolationFoundInDB]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(ViolationFound).filter_by(violation_found_id=violation_found_id)
            )
            violation = result.scalar_one_or_none()
            logger.info('get violation found by id')
            return ViolationFoundInDB.model_validate(violation) if violation else None    

    async def get_violation_found_fil_by_id(
            self,
            violation_id: int
    ) -> str:
        query = select(Check.fil_).select_from(Check).join(ViolationFound).where(
            and_(
                ViolationFound.violation_found_id == violation_id,
                ViolationFound.check_id == Check.check_id,
            )
        )
        logger.info('get_violation_found_fil_by_id')
        return (
            await self._get_scalar(query=query)
            or None
        )
        

    async def update_violation_found(
        self, violation_found_id: int, violation_update: ViolationFoundUpdate
    ) -> None:
        await self._update_field(
            violation_found_id=violation_found_id,
            **violation_update.model_dump(exclude_unset=True)
        )
        logger.info('updated violation found')
        await self.clear_cache()

    async def delete_violation_found(self, violation_id: int) -> None:
        async with self.session_maker() as session:
            stmt = delete(ViolationFound).where(ViolationFound.violation_found_id == violation_id)
            await session.execute(stmt)
            await session.commit()
            logger.info('deleted violation found')
            await self.clear_cache()

    async def delete_all_violations_found(self) -> None:
        async with self.session_maker() as session:
            stmt = delete(ViolationFound)
            await session.execute(stmt)
            await session.commit()
            await session.execute(text("ALTER SEQUENCE data.violation_found_violation_found_id_seq RESTART WITH 1"))
            await session.commit()
            logger.info('ALL violations found deleted')
            await self.clear_cache()

    # @cached(ttl=10, cache=Cache.REDIS, namespace='violation_found', serializer=PickleSerializer(), endpoint=settings.REDIS_HOST)
    async def get_all_violations_found(self) -> List[ViolationFoundInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(ViolationFound))
            violations = result.scalars().all()
            logger.info('get all violations found')
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ]
    
    @cached(ttl=10, cache=Cache.REDIS, namespace='violation_found', serializer=PickleSerializer(), endpoint=settings.REDIS_HOST)
    async def get_violations_found_by_check(self, check_id: int) -> Optional[List[ViolationFoundInDB]]:
        async with self.session_maker() as session:
            query = select(ViolationFound).where(
                    and_(
                        ViolationFound.check_id == check_id,
                        ViolationFound.violation_fixed.is_(None),
                        ViolationFound.is_pending.is_(False)
                    )
                )
            result = await session.execute(query)
            violations = result.scalars().all()
            logger.info('get violations found by check')
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ] if violations else None

    @cached(ttl=10, cache=Cache.REDIS, namespace='violation_found', serializer=PickleSerializer(), endpoint=settings.REDIS_HOST)
    async def get_violations_found_by_fil(self, fil_: str) -> Optional[List[ViolationFoundInDB]]:
        async with self.session_maker() as session:
            checks = await session.execute(
                select(Check).filter_by(fil_=fil_)
            )
            check_ids = [check.id for check in checks.scalars().all()]
            if not check_ids:
                return None
            
            result = await session.execute(
                select(ViolationFound).filter(ViolationFound.check_id.in_(check_ids))
            )
            violations = result.scalars().all()
            logger.info('get violations found by fil')
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ]
        
    async def get_active_violations_by_fil(
            self, fil_: str
    ) -> Optional[List[ViolationFoundInDB]]:
        async with self.session_maker() as session:
            query = (
                select(ViolationFound)
                .join(ViolationFound.check)
                .filter(
                    Check.fil_ == fil_,
                    Check.mfc_finish.is_not(None),
                    Check.mo_finish.is_(None),
                    Check.is_task.is_(True),
                    ViolationFound.violation_fixed.is_(None),
                    ViolationFound.is_pending.is_(False)
                    )
                .options(joinedload(ViolationFound.check))
            )
            
            result = await session.execute(query)
            
            violations = result.scalars().all()
            logger.info('get_active_violations_by_fil')
            
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ] if violations else None

    async def get_pending_violations_by_fil(
            self, fil_: str
    ) -> Optional[List[ViolationFoundInDB]]:
        async with self.session_maker() as session:
            query = (
                select(ViolationFound)
                .join(ViolationFound.check)
                .filter(
                    Check.fil_ == fil_,
                    Check.mfc_finish.is_not(None),
                    # Check.mo_finish.is_(None),
                    # Check.is_task.is_(True),
                    ViolationFound.violation_fixed.is_(None),
                    ViolationFound.is_pending.is_(True)
                    )
                .options(joinedload(ViolationFound.check))
            )
            
            result = await session.execute(query)
            
            violations = result.scalars().all()
            logger.info('get_active_violations_by_fil')
            
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ] if violations else None        
    
    @cached(ttl=10, cache=Cache.REDIS, namespace='violation_found', endpoint=settings.REDIS_HOST)
    async def is_violation_already_in_check(self, violation_dict_id: int, check_id: int) -> bool:
        query = select(ViolationFound).where(
            and_(
                ViolationFound.violation_dict_id == violation_dict_id,
                ViolationFound.check_id == check_id
            )
        )
        result = await self._get_scalar(query=query)
        logger.info('is violation already in check')
        return bool(result)
    
    async def is_violation_already_fixed(self, violation_found_id: int) -> bool:
        query = select(ViolationFound.violation_fixed).where(
            and_(
                ViolationFound.violation_found_id == violation_found_id,
            )
        )
        result = await self._get_scalar(query=query)
        logger.info('is violation already fixed')
        return bool(result)
    
    async def _get_scalar(self, query) -> any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, violation_found_id: int, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = (
                update(ViolationFound)
                .where(ViolationFound.violation_found_id == violation_found_id)
                .values(**kwargs)
            )
            await session.execute(stmt)
            await session.commit()

    async def clear_cache(self):
        pattern = "violation_found:*"
        keys = await self.cache.raw("keys", pattern)
        for key in keys:
            await self.cache.delete(key)
        logger.info("Cache cleared (keys: {})", keys)