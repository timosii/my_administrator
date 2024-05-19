import asyncio
from app.database.database import engine, session_maker, Base
from app.database.models.data import (
    User,
    Check,
    ViolationFound
)


async def insert_data():
    async with session_maker() as session:
        user_test = User(
            telegram_id='581145287',
            mo_='ГП 107',
            is_admin='',
            is_mfc='',
            )
        user_test_2 =  User(user_id='2121212')
        session.add_all([user_test, user_test_2])
        await session.commit()
