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
async def define_fil_age_category(fil: str):
    async with session_maker() as session:
        query = select(Filials.fil_population).filter_by(is_archieved=False, fil_=fil)
        result = await session.execute(query)
        age_category = result.scalar_one()
        logger.info('define fil age category')
        return age_category


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_zone_violations(zone: str, fil: str):
    age_category = await define_fil_age_category(fil=fil)
    async with session_maker() as session:
        if age_category in ('детские', 'смешанные'):
            query = select(Violations.violation_name).filter_by(zone=zone, is_archieved=False, is_dgp=True).distinct()
        else:
            query = select(Violations.violation_name).filter_by(zone=zone, is_archieved=False, is_gp=True).distinct()
        result = await session.execute(query)
        violations = result.scalars()
        logger.info('get zone violations')
        return list(violations)


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_violation_problems(violation_name: str, zone: str):
    async with session_maker() as session:
        query = select(Violations.problem).filter_by(violation_name=violation_name, zone=zone, is_archieved=False)
        result = await session.execute(query)
        problems = result.scalars()
        logger.info('get violation problems')
        return list(problems)


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_problems() -> list[str]:
    async with session_maker() as session:
        query = select(Violations.problem).filter_by(is_archieved=False).distinct()
        result = await session.execute(query)
        problems = result.scalars().all()
        logger.info('get all problems')
        return list(problems)


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_violations() -> list[str]:
    async with session_maker() as session:
        query = select(Violations.violation_name).filter_by(is_archieved=False).distinct()
        result = await session.execute(query)
        violations = result.scalars().all()
        logger.info('get all violations')
        return list(violations)


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_filials():
    async with session_maker() as session:
        query = select(Filials.fil_).filter_by(is_archieved=False)
        result = await session.execute(query)
        filials = result.scalars().all()
        logger.info('get all filials')
        return filials


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_all_mos():
    async with session_maker() as session:
        query = select(Mos.mo_).filter_by(is_archieved=False)
        result = await session.execute(query)
        mos = result.scalars().all()
        logger.info('get all mos')
        return mos


@cached(ttl=CACHE_EXPIRE_LONG, namespace='dicts_info')
async def get_fils_by_mo(mo: str):
    async with session_maker() as session:
        query = select(Filials.fil_).filter_by(
            mo_=mo,
            is_archieved=False)
        result = await session.execute(query)
        fils = result.scalars()
        logger.info('get fils by mo')
        return list(fils)
