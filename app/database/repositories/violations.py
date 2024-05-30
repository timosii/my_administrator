from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.dicts import Violations
from app.database.schemas.violation_schema import (
    ViolationInDB
)


class ViolationsRepo:
    def __init__(self):
        self.session_maker = session_maker
        
    async def get_id_by_name(
        self,
        violation_name: str,
        zone: str
    ) -> int:
        async with self.session_maker() as session:
            result = await session.execute(
                select(Violations.id).filter_by(violation_name=violation_name,
                                                zone=zone)
            )
            violation_id = result.scalar_one_or_none()
            return violation_id if violation_id else None       

    async def get_violation_by_id(
        self,
        violation_id: int
    ) -> Optional[ViolationInDB]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(Violations).filter_by(id=violation_id)
            )
            violation = result.scalar_one_or_none()
            return ViolationInDB.model_validate(violation) if violation else None  