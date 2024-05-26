from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.data import ViolationFound, Check
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundUpdate,
    ViolationFoundInDB,
)


class ViolationFoundRepo:
    def __init__(self):
        self.session_maker = session_maker

    async def add_violation_found(
        self, violation_create: ViolationFoundCreate
    ) -> ViolationFoundInDB:
        async with self.session_maker() as session:
            new_violation = ViolationFound(**violation_create.model_dump())
            session.add(new_violation)
            await session.commit()
            await session.refresh(new_violation)
            return ViolationFoundInDB.model_validate(new_violation)

    async def violation_found_exists(self, violation_id: int) -> bool:
        query = select(ViolationFound.id).filter_by(id=violation_id)
        return await self._get_scalar(query=query)

    async def get_violation_found_by_id(
        self, violation_id: int
    ) -> Optional[ViolationFoundInDB]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(ViolationFound).filter_by(id=violation_id)
            )
            violation = result.scalar_one_or_none()
            return ViolationFoundInDB.model_validate(violation) if violation else None    

    async def update_violation_found(
        self, violation_id: int, violation_update: ViolationFoundUpdate
    ) -> None:
        await self._update_field(
            violation_id, **violation_update.model_dump(exclude_unset=True)
        )

    async def delete_violation_found(self, violation_id: int) -> None:
        async with self.session_maker() as session:
            stmt = delete(ViolationFound).where(ViolationFound.id == violation_id)
            await session.execute(stmt)
            await session.commit()

    async def get_all_violations_found(self) -> List[ViolationFoundInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(ViolationFound))
            violations = result.scalars().all()
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ]

    async def get_violations_found_count(self) -> int:
        query = select(func.count()).select_from(ViolationFound)
        return (
            await self._get_scalar(query=query)
            or 0
        )

    async def get_violations_found_by_check(self, check_id: int) -> List[ViolationFoundInDB]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(ViolationFound).filter_by(check_id=check_id)
            )
            violations = result.scalars().all()
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ]
        
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
            return [
                ViolationFoundInDB.model_validate(violation) for violation in violations
            ]


    async def _get_scalar(self, query) -> any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, violation_id: int, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = (
                update(ViolationFound)
                .where(ViolationFound.id == violation_id)
                .values(**kwargs)
            )
            await session.execute(stmt)
            await session.commit()
