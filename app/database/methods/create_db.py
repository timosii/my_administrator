import asyncio
from app.database.database import engine, session_maker, Base
from app.database.models.dicts import *
from app.database.models.data import *

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# async def insert_data():
#     async with session_maker() as session:
#         user_test = Users(user_id='661772')
#         user_test_2 =  Users(user_id='2121212')
#         session.add_all([user_test, user_test_2])
#         await session.commit()
