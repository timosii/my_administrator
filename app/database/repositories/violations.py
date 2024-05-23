from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.dicts import Violations
# from app.database.schemas.violation_found_schema import (
#     ViolationFoundCreate,
#     ViolationFoundUpdate,
#     ViolationFoundInDB,
# )


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
            violation = result.scalar_one_or_none()
            return violation if violation else None        
