from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.repositories.violations_found import ViolationRepo
from app.database.models.data import ViolationFound
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundUpdate,
    ViolationFoundInDB,
)


class ViolationService:
    def __init__(self, db_repository: ViolationRepo = ViolationRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def add_violation(
        self, violation_create: ViolationFoundCreate
    ) -> ViolationFoundInDB:
        result = await self.db_repository.add_violation(violation_create=violation_create)
        return result

    async def violation_exists(self, violation_id: int) -> bool:
        result = await self.db_repository.violation_exists(violation_id=violation_id)
        return result

    async def get_violation_by_id(
        self, violation_id: int
    ) -> Optional[ViolationFoundInDB]:
        result = await self.db_repository.get_violation_by_id(violation_id=violation_id)
        return result

    async def update_violation(
        self, violation_id: int, violation_update: ViolationFoundUpdate
    ) -> None:
        result = await self.db_repository.update_violation(
            violation_id=violation_id,
            violation_update=violation_update
            )
        return result

    async def delete_violation(self, violation_id: int) -> None:
        result = await self.db_repository.delete_violation(violation_id=violation_id)
        return result

    async def get_all_violations(self) -> List[ViolationFoundInDB]:
        result = await self.db_repository.get_all_violations()
        return result

    async def get_violations_count(self) -> int:
        result = await self.db_repository.get_violations_count()
        return result

    async def get_violations_by_check(self, check_id: int) -> List[ViolationFoundInDB]:
        result = await self.db_repository.get_violations_by_check(check_id=check_id)
        return result
