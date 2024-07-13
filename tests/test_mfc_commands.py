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
from tests.config import settings_test
from tests.utils import time_determiner

user_id = settings_test.TEST_ID_MFC


async def send_message(dp, bot, user_id, text):
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    user = User(id=user_id, is_bot=False, first_name='Тест')
    message = Message(
        message_id=1,
        chat=chat,
        from_user=user,
        text=text,
        date=datetime.now()
    )
    return await dp.feed_update(bot, Update(message=message, update_id=1))


async def assert_send_message(bot, expected_text):
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == expected_text


@pytest.mark.asyncio(scope='session')
async def test_mfc_choose_mo(dp, bot):
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.clear()
    await fsm_context.set_state(MfcStates.choose_mo)
    await fsm_context.set_data(
        {'mfc_user_id': int(user_id)}
    )
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )

    result = await send_message(dp, bot, user_id, '107')
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert result is not UNHANDLED
    await assert_send_message(bot, 'Ваша поликлиника: ГП 107, пожалуйста выберите филиал проверки')
    assert current_state == MfcStates.choose_fil
    assert current_data == {'mfc_user_id': int(user_id), 'mo': 'ГП 107'}
    await fsm_context.clear()


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

    result = await send_message(dp, bot, user_id, 'ГП 107')
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert result is not UNHANDLED
    await assert_send_message(bot, MfcMessages.main_menu)
    assert current_state == MfcStates.choose_type_checking
    assert current_data == {'fil_': 'ГП 107', 'mfc_user_id': int(user_id), 'mo': 'ГП 107'}
    await fsm_context.clear()


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

    result = await send_message(dp, bot, user_id, 'Начать проверку')
    assert result is not UNHANDLED
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    await assert_send_message(bot, f'Вы начали проверку {time_determiner()}. Выберите зону нарушения: ')
    assert current_state == MfcStates.choose_zone
    assert len(current_data.keys()) == 9
    check_id_test = current_data.get('check_id')
    fil_ = current_data.get('fil_')
    is_task = current_data.get('is_task')
    mfc_finish = current_data.get('mfc_finish')
    mfc_start = current_data.get('mfc_start')
    mfc_user_id = current_data.get('mfc_user_id')
    mo = current_data.get('mo')
    mo_finish = current_data.get('mo_finish')
    mo_start = current_data.get('mo_start')
    assert check_id_test is not None
    assert fil_ == 'ГП 107'
    assert is_task is False
    assert mfc_finish is None
    assert mfc_start is not None
    assert mfc_user_id == int(user_id)
    assert mo == 'ГП 107'
    assert mo_finish is None
    assert mo_start is None

    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    result = await send_message(dp, bot, user_id, '🏥 Входная группа')
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    await assert_send_message(bot, 'Выберите нарушение в зоне <b>"Входная группа"</b>')
    assert current_state == MfcStates.choose_violation
    assert current_data.get('check_id') == check_id_test
    assert current_data.get('fil_') == fil_
    assert current_data.get('is_task') == is_task
    assert current_data.get('mfc_start') == mfc_start
    assert current_data.get('mfc_user_id') == mfc_user_id
    assert current_data.get('mo') == mo
    assert current_data.get('mo_start') is None
    assert current_data.get('mo_finish') is None
    assert current_data.get('zone') == 'Входная группа'
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    result = await send_message(dp, bot, user_id, 'Загрязнения во входной группе')

    first_message: TelegramType = bot.get_request()
    assert isinstance(first_message, SendMessage)
    assert first_message.text == 'Вы обнаружили проблему ☑️'

    second_message: TelegramType = bot.get_request()
    assert isinstance(second_message, SendMessage)
    assert second_message.text == 'Приложите фото и напишите комментарий по проблеме <b>"Загрязнения во входной группе"</b>'

    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    violation_detected = current_data.get('violation_detected')
    violation_name = current_data.get('violation_name')
    assert current_state == MfcStates.add_content
    assert current_data.get('check_id') == check_id_test
    assert current_data.get('comm_mfc') is None
    assert current_data.get('comm_mo') is None
    assert current_data.get('fil_') == fil_
    assert current_data.get('is_pending') is False
    assert current_data.get('is_task') == is_task
    assert current_data.get('mfc_start') == mfc_start
    assert current_data.get('mfc_user_id') == mfc_user_id
    assert current_data.get('mo') == mo
    assert current_data.get('mo_start') is None
    assert current_data.get('mo_finish') is None
    assert current_data.get('photo_id_mfc') is None
    assert current_data.get('photo_id_mo') is None
    assert isinstance(current_data.get('time_to_correct'), str)
    assert isinstance(violation_detected, str)
    assert current_data.get('violation_dict_id') == 1
    assert isinstance(current_data.get('violation_found_id'), int)
    assert violation_name == 'Загрязнения во входной группе'
    assert current_data.get('violation_pending') is None
    assert current_data.get('zone') == 'Входная группа'
    await fsm_context.clear()
