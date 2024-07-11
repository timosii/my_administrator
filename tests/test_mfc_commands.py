from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import Chat, Message, Update, User

from app.handlers.messages import MfcMessages
from app.handlers.states import MfcStates
from tests.config import settings
from tests.utils import time_determiner

user_id = settings.TEST_ID_MFC


@pytest.mark.asyncio(scope='session')
async def test_mfc_choose_mo(dp, bot):
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(MfcStates.choose_mo)
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )

    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    user = User(id=user_id, is_bot=False, first_name='Тест')
    message = Message(
        message_id=1,
        chat=chat,
        from_user=user,
        text='107',
        date=datetime.now()
    )
    result = await dp.feed_update(
        bot,
        Update(message=message, update_id=1)
    )
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert result is not UNHANDLED
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == 'Ваша поликлиника: ГП 107, пожалуйста выберите филиал проверки'
    assert current_state == MfcStates.choose_fil
    assert current_data == {'mfc_user_id': int(user_id), 'mo': 'ГП 107'}


@pytest.mark.asyncio(scope='session')
async def test_mfc_choose_fil(dp, bot):
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(MfcStates.choose_fil)
    await fsm_context.set_data(
        {'mfc_user_id': int(user_id), 'mo': 'ГП 107'}
    )
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )

    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    user = User(id=user_id, is_bot=False, first_name='Тест')
    message = Message(
        message_id=1,
        chat=chat,
        from_user=user,
        text='ГП 107',
        date=datetime.now()
    )
    result = await dp.feed_update(
        bot,
        Update(message=message, update_id=1)
    )
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert result is not UNHANDLED
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == MfcMessages.main_menu
    assert current_state == MfcStates.choose_type_checking
    assert current_data == {'fil_': 'ГП 107', 'mfc_user_id': int(user_id), 'mo': 'ГП 107'}


@pytest.mark.asyncio(scope='session')
async def test_mfc_start_checking(dp, bot):
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(MfcStates.choose_type_checking)
    await fsm_context.set_data(
        {'fil_': 'ГП 107', 'mfc_user_id': int(user_id), 'mo': 'ГП 107'}
    )
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )

    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    user = User(id=user_id, is_bot=False, first_name='Тест')
    message = Message(
        message_id=1,
        chat=chat,
        from_user=user,
        text='Начать проверку',
        date=datetime.now()
    )
    result = await dp.feed_update(
        bot,
        Update(message=message, update_id=1)
    )
    current_state = await fsm_context.get_state()
    assert result is not UNHANDLED
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == f'Вы начали проверку {time_determiner()}. Выберите зону нарушения: '
    assert current_state == MfcStates.choose_zone
