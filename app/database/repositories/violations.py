from loguru import logger
from sqlalchemy import select

from app.config import settings
from app.database.database import session_maker
from app.database.models.dicts import Violations
from app.database.repositories.cache_config import cached, caches
from app.database.schemas.violation_schema import ViolationInDB

CACHE_EXPIRE_SHORT = settings.CACHE_SHORT
CACHE_EXPIRE_LONG = settings.CACHE_LONG


class ViolationsRepo:
    def __init__(self):
        self.session_maker = session_maker
        self.cache = caches.get('default')

    @cached(ttl=CACHE_EXPIRE_LONG, namespace='violations')
    async def get_dict_id_by_name(
        self,
        violation_name: str,
        zone: str
    ) -> int:
        async with self.session_maker() as session:
            result = await session.execute(
                select(Violations.violation_dict_id).filter_by(violation_name=violation_name,
                                                               zone=zone)
            )
            violation_id = result.scalar_one_or_none()
            logger.info('get dict vio id by name and zone')
            return violation_id if violation_id else None

    @cached(ttl=CACHE_EXPIRE_LONG, namespace='violations')
    async def get_violation_dict_by_id(
        self,
        violation_dict_id: int
    ) -> ViolationInDB:
        async with self.session_maker() as session:
            result = await session.execute(
                select(Violations).filter_by(violation_dict_id=violation_dict_id)
            )
            violation = result.scalar_one()
            logger.info('get_violation_dict_by_id')
            return ViolationInDB.model_validate(violation)
