from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func, not_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.data import Check
from app.database.schemas.check_schema import (
    CheckCreate,
    CheckUpdate,
    CheckInDB
)


class CheckRepo:
    def __init__(self):
        self.session_maker = session_maker

    async def add_check(self,
                        check_create: CheckCreate) -> CheckInDB:
        async with self.session_maker() as session:
            new_check = Check(**check_create.model_dump())
            session.add(new_check)
            await session.commit()
            await session.refresh(new_check)
            return CheckInDB.model_validate(new_check)

    async def check_exists(self, check_id: int) -> bool:
        query = select(Check.id).filter_by(id=check_id)
        return await self._get_scalar(query=query)

    async def get_check_by_id(self, check_id: int) -> Optional[CheckInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(Check).filter_by(id=check_id))
            check = result.scalar_one_or_none()
            return CheckInDB.model_validate(check) if check else None

    async def update_check(self, check_id: int, check_update: CheckUpdate) -> None:
        await self._update_field(check_id, **check_update.model_dump(exclude_unset=True))

    async def delete_check(self, check_id: int) -> None:
        async with self.session_maker() as session:
            stmt = delete(Check).where(Check.id == check_id)
            await session.execute(stmt)
            await session.commit()

    async def get_all_checks(self) -> List[CheckInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(Check))
            checks = result.scalars().all()
            return [CheckInDB.model_validate(check) for check in checks]
        
    async def get_all_active_checks_by_fil(self, fil_: str) -> Optional[List[CheckInDB]]:
        async with self.session_maker() as session:
            query = select(Check).where(
                and_(
                    Check.fil_ == fil_,
                    Check.mfc_finish.is_not(None),
                    )
            )
            result = await session.execute(query)
            checks = result.scalars().all()
            return [CheckInDB.model_validate(check) for check in checks] if checks else None

    async def get_checks_count(self) -> int:
        query = select(func.count()).select_from(Check)
        return await self._get_scalar(query=query) or 0

    async def get_checks_by_user(self, user_id: int) -> List[CheckInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(Check).filter_by(user_id=user_id))
            checks = result.scalars().all()
            return [CheckInDB.model_validate(check) for check in checks]

    async def _get_scalar(self, query) -> any:
        async with self.session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _update_field(self, check_id: int, **kwargs) -> None:
        async with self.session_maker() as session:
            stmt = update(Check).where(Check.id == check_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()
