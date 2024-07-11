import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage

from app.config import settings
from app.handlers import additional, default, dev
from app.handlers.admin import admin
from app.handlers.user.mfc_part import mfc_leader, mfc_main
from app.handlers.user.mo_part import (
    mo_controler,
    mo_performer,
    pending_process,
    take_process,
)
from tests.mocked_aiogram import MockedBot, MockedSession


@pytest.fixture(scope='session')
def dp() -> Dispatcher:
    redis = Redis(host=settings.REDIS_HOST)
    storage = RedisStorage(redis=redis)
    dispatcher = Dispatcher(storage=storage)
    # dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_routers(
        admin.router,
        additional.router,
        dev.router,
        mfc_leader.router,
        mfc_main.router,
        pending_process.router,
        take_process.router,
        mo_performer.router,
        mo_controler.router,
        default.router,
    )
    return dispatcher


@pytest.fixture(scope='session')
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot


@pytest.fixture(scope='session', autouse=True)
async def reset_fsm(dp: Dispatcher):
    yield
    storage = dp.fsm.storage
    if hasattr(storage, 'data'):
        storage.data.clear()
    if hasattr(storage, 'states'):
        storage.states.clear()
    if hasattr(storage, 'keys'):
        storage.keys.clear()

# @pytest.fixture(scope='function', autouse=True)
# async def close_cache():
#     yield
#     cache = caches.get('default')
#     await cache.close()
