from loguru import logger
from sqlalchemy import select

from app.config import settings
from app.database.database import session_maker
from app.database.models.dicts import Filials, Mos, Violations, Zones
from app.database.repositories.cache_config import cached

CACHE_EXPIRE_SHORT = settings.CACHE_SHORT
CACHE_EXPIRE_LONG = settings.CACHE_LONG


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_zones():
    async with session_maker() as session:
        query = select(Zones.zone_name)
        result = await session.execute(query)
        zones = result.scalars()
        logger.info('get all zones')
        return list(zones)


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_zone_violations(zone: str):
    async with session_maker() as session:
        query = select(Violations.violation_name).filter_by(zone=zone)
        result = await session.execute(query)
        violations = result.scalars()
        logger.info('get zone violations')
        return list(violations)


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_violations() -> list[str]:
    async with session_maker() as session:
        query = select(Violations.violation_name)
        result = await session.execute(query)
        violations = result.scalars().all()
        logger.info('get all violations')
        return list(violations)


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_filials():
    async with session_maker() as session:
        query = select(Filials.fil_)
        result = await session.execute(query)
        filials = result.scalars().all()
        logger.info('get all filials')
        return filials


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_mos():
    async with session_maker() as session:
        query = select(Mos.mo_)
        result = await session.execute(query)
        mos = result.scalars().all()
        logger.info('get all mos')
        return mos


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_fils_by_mo(mo: str):
    async with session_maker() as session:
        query = select(Filials.fil_).filter_by(mo_=mo)
        result = await session.execute(query)
        fils = result.scalars()
        logger.info('get fils by mo')
        return list(fils)
