import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_tests import MockedBot
from pytest_mock import MockerFixture

from app.handlers.user.mfc_part.mfc_main import router


class MfcStates(StatesGroup):
    choose_mo = State()
    choose_fil = State()
    choose_type_checking = State()
    choose_zone = State()
    choose_violation = State()
    add_content = State()
    continue_state = State()
    get_pending = State()


@pytest.fixture
def bot():
    return MockedBot(Bot(token='BOT_TOKEN'))


@pytest.fixture
def dispatcher(bot: MockedBot):
    dp = Dispatcher(bot)
    dp.include_router(router)
    return dp


@pytest.mark.asyncio
async def test_cmd_start(bot: MockedBot, dispatcher: Dispatcher, mocker: MockerFixture):
    async with bot:
        message = Message(
            message_id=1,
            date='2021-01-01',
            chat={'id': 12345, 'type': 'private'},
            from_user={'id': 12345, 'is_bot': False, 'username': 'test_user'},
            text='/start'
        )

        state = FSMContext(bot=bot, storage=bot.fsm_storage, key=('user', 12345))
        mocker.patch.object(state, 'clear', new_callable=mocker.AsyncMock)
        mocker.patch.object(state, 'update_data', new_callable=mocker.AsyncMock)

        violation_found_obj = mocker.Mock()
        mocker.patch.object(violation_found_obj, 'user_empty_violations_found_process', new_callable=mocker.AsyncMock)

        await bot.send(message)

        state.clear.assert_called_once()
        state.update_data.assert_called_once_with(mfc_user_id=12345)
        violation_found_obj.user_empty_violations_found_process.assert_called_once_with(user_id=12345)


@pytest.mark.asyncio
async def test_choose_mo(bot: MockedBot, dispatcher: Dispatcher, mocker: MockerFixture):
    async with bot:
        message = Message(
            message_id=1,
            date='2021-01-01',
            chat={'id': 12345, 'type': 'private'},
            from_user={'id': 12345, 'is_bot': False, 'username': 'test_user'},
            text='123'
        )

        helper = mocker.Mock()
        mocker.patch.object(helper, 'mo_define_by_num', new_callable=mocker.AsyncMock, return_value=['MO1'])

        state = FSMContext(bot=bot, storage=bot.fsm_storage, key=('user', 12345))
        mocker.patch.object(state, 'update_data', new_callable=mocker.AsyncMock)
        mocker.patch.object(state, 'set_state', new_callable=mocker.AsyncMock)

        await bot.send(message)

        state.update_data.assert_called_once_with(mo='MO1')
        state.set_state.assert_called_once_with(MfcStates.choose_fil)
