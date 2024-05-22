import datetime as dt
import asyncio
from sqlalchemy import func, select, update
from app.database.database import engine, session_maker, Base
from app.database.models.dicts import (
    Zones,
    Violations
)

async def get_all_zones():
    async with session_maker() as session:
        query = select(Zones.zone_name)
        result = await session.execute(query)
        zones = result.scalars()
        return list(zones)

async def get_zone_violations(zone: str):
    async with session_maker() as session:
        query = select(Violations.violation_name).filter_by(zone=zone)
        result = await session.execute(query)
        violations = result.scalars()
        return list(violations)
    
async def get_all_violations():
    async with session_maker() as session:
        query = select(Violations.violation_name)
        result = await session.execute(query)
        violations = result.scalars().all()
        return violations

ZONES = None
VIOLATIONS = None

async def initialize_constants():
    global ZONES, VIOLATIONS
    ZONES = await get_all_zones()
    VIOLATIONS = await get_all_violations()

asyncio.run(initialize_constants())

def get_zones():
    return ZONES

def get_violations():
    return VIOLATIONS