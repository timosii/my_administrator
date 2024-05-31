from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.data import User, Check
from app.database.schemas.user_schema import UserCreate, UserUpdate, UserInDB
from app.database.schemas.check_schema import CheckInDB

class UserRepo:
    def __init__(self):
        self.session_maker = session_maker

    async def add_user(self, user_create: UserCreate) -> UserInDB:
        async with self.session_maker() as session:
            new_user = User(**user_create.model_dump())
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return UserInDB.model_validate(new_user)
        
    async def get_user_mo(self, user_id: int) -> str:
        query = select(User.mo_).filter_by(id=user_id)
        result = await self._get_scalar(query=query)
        return result

    async def user_exists(self, user_id: int) -> bool:
        query = select(User.id).filter_by(id=user_id)
        return await self._get_scalar(query=query)

    async def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()
            return UserInDB.model_validate(user) if user else None

    async def update_user(self, user_id: int, user_update: UserUpdate) -> None:
        await self._update_field(user_id, **user_update.model_dump(exclude_unset=True))

    async def delete_user(self, user_id: int) -> None:
        async with self.session_maker() as session:
            stmt = delete(User).where(User.id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def get_all_users(self) -> List[UserInDB]:
        async with self.session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return [UserInDB.model_validate(user) for user in users]

    async def get_user_active_checks(self, user_id: int) -> Optional[List[CheckInDB]]:
        async with self.session_maker() as session:
            query = select(Check).where(
                and_(
                    Check.user_id == user_id,
                    Check.mfc_finish.is_(None)
                )
            )
            result = await session.execute(query)
            checks = result.scalars().all()
            return [CheckInDB.model_validate(check) for check in checks] if checks else None

    async def get_user_count(self) -> int:
        query = select(func.count()).select_from(User)
        return await self._get_scalar(query=query) or 0
    
    async def is_admin(self, user_id: int) -> bool:
        query = select(User.is_admin).filter_by(id=user_id, is_archived=False)
        return await self._get_scalar(query=query)

    async def is_mfc(self, user_id: int) -> bool:
        query = select(User.is_mfc).filter_by(id=user_id, is_archived=False)
        return await self._get_scalar(query=query)

    async def is_mfc_leader(self, user_id: int) -> bool:
        query = select(User.is_mfc_leader).filter_by(id=user_id, is_archived=False)
        return await self._get_scalar(query=query)

    async def is_mo_performer(self, user_id: int) -> bool:
        query = select(User.is_mo_performer).filter_by(id=user_id, is_archived=False)
        return await self._get_scalar(query=query)

    async def is_mo_controler(self, user_id: int) -> bool:
        query = select(User.is_mo_controler).filter_by(id=user_id, is_archived=False)
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
