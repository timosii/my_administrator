import datetime as dt
import asyncio
from sqlalchemy import func, select, update
from app.database.database import engine, session_maker, Base
from app.database.models.dicts import (
    Zones,
    Violations,
    Filials,
    Mos
)
from loguru import logger
from aiocache import cached, Cache
import redis.asyncio as redis
from app.config import settings
import redis.asyncio as redis

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info', endpoint=settings.REDIS_HOST)
async def get_all_zones():
    async with session_maker() as session:
        query = select(Zones.zone_name)
        result = await session.execute(query)
        zones = result.scalars()
        logger.info('get all zones')
        return list(zones)

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info', endpoint=settings.REDIS_HOST)
async def get_zone_violations(zone: str):
    async with session_maker() as session:
        query = select(Violations.violation_name).filter_by(zone=zone)
        result = await session.execute(query)
        violations = result.scalars()
        logger.info('get zone violations')
        return list(violations)

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info', endpoint=settings.REDIS_HOST)
async def get_all_violations() -> list[str]:
    async with session_maker() as session:
        query = select(Violations.violation_name)
        result = await session.execute(query)
        violations = result.scalars().all()
        logger.info('get all violations')
        return violations

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info', endpoint=settings.REDIS_HOST)
async def get_all_filials():
    async with session_maker() as session:
        query = select(Filials.fil_)
        result = await session.execute(query)
        filials = result.scalars().all()
        logger.info('get all filials')
        return filials
    
@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info', endpoint=settings.REDIS_HOST)
async def get_all_mos():
    async with session_maker() as session:
        query = select(Mos.mo_)
        result = await session.execute(query)
        mos = result.scalars().all()
        logger.info('get all mos')
        return mos

@cached(ttl=60, cache=Cache.REDIS, namespace='dicts_info', endpoint=settings.REDIS_HOST)
async def get_fils_by_mo(mo: str):
    async with session_maker() as session:
        query = select(Filials.fil_).filter_by(mo_=mo)
        result = await session.execute(query)
        fils = result.scalars()
        logger.info('get fils by mo')
        return list(fils)
