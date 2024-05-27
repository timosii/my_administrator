from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.repositories.check import CheckRepo
from app.database.models.data import Check
from app.database.schemas.check_schema import CheckCreate, CheckUpdate, CheckInDB


class CheckService:
    def __init__(self, db_repository: CheckRepo = CheckRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def add_check(self, check_create: CheckCreate) -> CheckInDB:
        result = await self.db_repository.add_check(check_create=check_create)
        return result

    async def check_exists(self, check_id: int) -> bool:
        result = await self.db_repository.check_exists(check_id=check_id)
        return result

    async def get_check_by_id(self, check_id: int) -> Optional[CheckInDB]:
        result = await self.db_repository.get_check_by_id(check_id=check_id)
        return result

    async def update_check(self, check_id: int, check_update: CheckUpdate) -> None:
        result = await self.db_repository.update_check(check_id=check_id, check_update=check_update)
        return result

    async def delete_check(self, check_id: int) -> None:
        result = await self.db_repository.delete_check(check_id=check_id)
        return result

    async def get_all_checks(self) -> List[CheckInDB]:
        result = await self.db_repository.get_all_checks()
        return result
    
    async def get_all_active_checks_by_fil(self, fil_: str) -> List[CheckInDB]:
        result = await self.db_repository.get_all_active_checks_by_fil(fil_=fil_)
        return result

    async def get_checks_count(self) -> int:
        result = await self.db_repository.get_all_checks()
        return result

    async def get_checks_by_user(self, user_id: int) -> List[CheckInDB]:
        result = await self.db_repository.get_checks_by_user(user_id=user_id)
        return result

