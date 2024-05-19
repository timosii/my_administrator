import asyncio
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import engine, session_maker, Base
from app.database.models.data import (
    User,
    Check,
    ViolationFound
)

async def add_user(
        # new_user: User
        ) -> None:
    async with session_maker() as session:
        new_user = User(
            id=112,
            mo_='ГП 107',
            last_name='Тестов',
            first_name='Тест',
            patronymic='Тестович',
            post='Менеджер',
            is_mfc=True
            )
        session.add(new_user)
        await session.commit()


async def user_exists(id: int) -> bool:
    async with session_maker() as session:
        query = select(User.id).filter_by(id=id).limit(1)

        result = await session.execute(query)

        user = result.scalar_one_or_none()
        return bool(user)


async def get_first_name(id: int) -> str:
    async with session_maker() as session:
        query = select(User.first_name).filter_by(id=id)

        result = await session.execute(query)

        first_name = result.scalar_one_or_none()
        return first_name or ""


async def set_is_admin(id: int,
                       is_admin: bool) -> None:
    async with session_maker() as session:
        stmt = update(User).where(User.id == id).values(is_admin=is_admin)

        await session.execute(stmt)
        await session.commit()


async def get_all_users() -> list[User]:
    async with session_maker() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars()
        return list(users)


async def get_user_count() -> int:
    async with session_maker() as session:
        query = select(func.count()).select_from(User)

        result = await session.execute(query)

        count = result.scalar_one_or_none() or 0
        return int(count)


async def is_admin(id: int) -> bool:
    async with session_maker() as session:
        query = select(User.is_admin).filter_by(id=id, is_archived=False)

        result = await session.execute(query)

        is_admin = result.scalar_one_or_none()
        return bool(is_admin)


async def is_mfc(id: int) -> bool:
    async with session_maker() as session:
        query = select(User.is_mfc).filter_by(id=id, is_archived=False)
        result = await session.execute(query)
        is_mfc = result.scalar_one_or_none()
        return bool(is_mfc)


async def is_mfc_leader(id: int) -> bool:
    async with session_maker() as session:
        query = select(User.is_mfc_leader).filter_by(id=id, is_archived=False)
        result = await session.execute(query)
        is_mfc_leader = result.scalar_one_or_none()
        return bool(is_mfc_leader)


async def is_mo_performer(id: int) -> bool:
    async with session_maker() as session:
        query = select(User.is_mo_performer).filter_by(id=id, is_archived=False)
        result = await session.execute(query)
        is_mo_performer = result.scalar_one_or_none()
        return bool(is_mo_performer)


async def is_mo_controler(id: int) -> bool:
    async with session_maker() as session:
        query = select(User.is_mo_controler).filter_by(id=id, is_archived=False)
        result = await session.execute(query)
        is_mo_controler = result.scalar_one_or_none()
        return bool(is_mo_controler)


if __name__ == '__main__':
    # new_user = User(
    #     id=112,
    #     mo_='ГП 107',
    #     last_name='Тестов',
    #     first_name='Тест',
    #     patronymic='Тестович',
    #     post='Менеджер',
    #     is_mfc=True
    #     )
    print(asyncio.run(is_admin(id=581145287)))
    print(asyncio.run(is_mfc(id=581145287)))
    print(asyncio.run(is_mfc_leader(id=581145287)))
    print(asyncio.run(is_mo_performer(id=581145287)))
    print(asyncio.run(is_mo_controler(id=581145287)))
    print(asyncio.run(add_user(
        # new_user=new_user
        )))
    # print(asyncio.run(is_admin(id=new_user.id)))
    # print(asyncio.run(is_mfc(id=new_user.id)))
    # print(asyncio.run(is_mfc_leader(id=new_user.id)))
    # print(asyncio.run(is_mo_performer(id=new_user.id)))
    # print(asyncio.run(is_mo_controler(id=new_user.id)))
