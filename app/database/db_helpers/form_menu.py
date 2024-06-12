import datetime as dt
import asyncio
from sqlalchemy import func, select, update
from app.database.database import engine, session_maker, Base
from app.database.models.dicts import (
    Zones,
    Violations,
    Filials
)
from loguru import logger
from aiocache import cached, Cache

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info')
async def get_all_zones():
    async with session_maker() as session:
        query = select(Zones.zone_name)
        result = await session.execute(query)
        zones = result.scalars()
        logger.info('get all zones')
        return list(zones)

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info')
async def get_zone_violations(zone: str):
    async with session_maker() as session:
        query = select(Violations.violation_name).filter_by(zone=zone)
        result = await session.execute(query)
        violations = result.scalars()
        logger.info('get zone violations')
        return list(violations)

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info')
async def get_all_violations():
    async with session_maker() as session:
        query = select(Violations.violation_name)
        result = await session.execute(query)
        violations = result.scalars().all()
        logger.info('get all violations')
        return violations

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info')
async def get_all_filials():
    async with session_maker() as session:
        query = select(Filials.fil_)
        result = await session.execute(query)
        filials = result.scalars().all()
        logger.info('get all filials')
        return filials

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info')
async def get_fils_by_mo(mo: str):
    async with session_maker() as session:
        query = select(Filials.fil_).filter_by(mo_=mo)
        result = await session.execute(query)
        fils = result.scalars()
        logger.info('get fils by mo')
        return list(fils)

ZONES = None
VIOLATIONS = None
FILIALS = None

async def initialize_constants():
    global ZONES, VIOLATIONS, FILIALS
    ZONES = await get_all_zones()
    VIOLATIONS = await get_all_violations()
    FILIALS = await get_all_filials()

asyncio.get_event_loop().run_until_complete(initialize_constants())
# asyncio.run(initialize_constants())

# def get_zones():
#     return ZONES

# def get_violations():
#     return VIOLATIONS

# def get_filials():
#     return FILIALS
