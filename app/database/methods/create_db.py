import asyncio
from app.database.database import engine, session_maker, Base
from app.database.models.dicts import *
from app.database.models.data import *

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
