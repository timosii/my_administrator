import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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
    dispatcher = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
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
