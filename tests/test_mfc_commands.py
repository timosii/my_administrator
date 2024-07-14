from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.methods import (
    AnswerCallbackQuery,
    EditMessageText,
    SendMessage,
    SendPhoto,
    SendSticker,
)
from aiogram.methods.base import TelegramType
from aiogram.types import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    PhotoSize,
    Update,
    User,
)

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


async def send_callback_with_message(dp, bot, user_id, callback_data: str):
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    user = User(id=user_id, is_bot=False, first_name='Тест')
    message = Message(
        message_id=1,
        chat=chat,
        from_user=user,
        text='Тест',
        date=datetime.now()
    )
    callback_ = CallbackQuery(
        id='2212121',
        chat_instance='3212121',
        from_user=User(id=user_id, is_bot=False, first_name='Тест'),
        data=callback_data,
        message=message
    )
    return await dp.feed_update(bot, Update(callback_query=callback_, update_id=1))


async def send_fake_photo(dp, bot, user_id):
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    user = User(id=user_id, is_bot=False, first_name='Тест')
    photo = PhotoSize(file_id='fake_file_id', width=800, height=600, file_unique_id='unique_id_of_photo')
    send_photo_ = Message(
        message_id=1,
        chat=chat,
        from_user=user,
        photo=[photo],
        caption='Тестовая подпись',
        date=datetime.now()
    )
    return await dp.feed_update(bot, Update(message=send_photo_, update_id=1))


async def assert_send_message(bot, expected_text):
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == expected_text
    return outgoing_message


async def assert_save_violation_found(dp, bot, violation_name: str):
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True,
    )
    bot.add_result_for(
        method=EditMessageText,
        ok=True
    )
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )
    description_callback_result = await send_callback_with_message(dp, bot, user_id=user_id, callback_data='save_and_go')
    assert description_callback_result is not UNHANDLED
    outgoing_callback = bot.get_request()
    assert outgoing_callback.text == f'Мы сохранили нарушение <b>"{violation_name}"</b>. Спасибо!'
    outgoing_callback = bot.get_request()
    assert outgoing_callback.text == 'Отправляю нарушение сотрудникам ГП 107 ...'
    outgoing_callback = bot.get_request()
    assert isinstance(outgoing_callback, SendSticker)
    outgoing_callback = bot.get_request()
    assert isinstance(outgoing_callback, SendPhoto)
    outgoing_callback = bot.get_request()
    assert outgoing_callback.text == 'Оповещение в телеграм <b>отправлено</b> 1 сотруднику филиала ГП 107.'
    outgoing_callback = bot.get_request()
    assert outgoing_callback.text == 'Информация сохранена ✅'
    assert outgoing_callback.show_alert is True
    outgoing_callback = bot.get_request()
    assert outgoing_callback.text == 'Вы можете продолжить проверку'
    outgoing_callback = bot.get_request()
    assert outgoing_callback.text == 'Выберите нарушение в зоне <b>"Входная группа"</b>'


async def assert_add_content(dp, bot, fsm_context: FSMContext, violation_name: str):
    bot.add_result_for(
        method=SendPhoto,
        ok=True,
    )
    result_photo = await send_fake_photo(dp, bot, user_id=user_id)
    assert result_photo is not UNHANDLED
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert current_state == MfcStates.continue_state
    photo_id_mfc = current_data.get('photo_id_mfc')
    comm_mfc = current_data.get('comm_mfc')
    assert comm_mfc == 'Тестовая подпись'
    assert photo_id_mfc is not None
    outgoing_message = await assert_send_message(bot, f'Вы приложили фото и написали комментарий по проблеме <b>"{violation_name}"</b>.\nСохранить нарушение?')
    assert outgoing_message.reply_markup is not None
    markup = outgoing_message.reply_markup
    assert isinstance(markup, InlineKeyboardMarkup)
    button: InlineKeyboardButton = markup.inline_keyboard[0][0]
    assert button.text == 'Сохранить'
    assert button.callback_data == 'save_and_go'


async def assert_choose_violation(dp, bot, fsm_context, violation_name: str):
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    result = await send_message(dp, bot, user_id, f'{violation_name}')
    assert result is not UNHANDLED
    current_data = await fsm_context.get_data()
    violation_dict_id = current_data.get('violation_dict_id')
    first_message: TelegramType = bot.get_request()
    assert isinstance(first_message, SendMessage)
    assert first_message.text == 'Вы обнаружили проблему ☑️'

    second_message: TelegramType = bot.get_request()
    assert isinstance(second_message, SendMessage)
    assert second_message.text == f'Приложите фото и напишите комментарий по проблеме <b>"{violation_name}"</b>'
    assert second_message.reply_markup is not None
    markup = second_message.reply_markup
    assert isinstance(markup, InlineKeyboardMarkup)
    button: InlineKeyboardButton = markup.inline_keyboard[0][0]
    assert button.text == 'Посмотреть описание нарушения'
    assert button.callback_data == f'description_{violation_dict_id}'


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
async def test_mfc_checking_process(dp, bot):
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
    assert result is not UNHANDLED
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

    await assert_choose_violation(dp, bot, fsm_context, violation_name='Загрязнения во входной группе')
    current_data = await fsm_context.get_data()
    current_state = await fsm_context.get_state()
    violation_dict_id = current_data.get('violation_dict_id')
    violation_detected = current_data.get('violation_detected')
    violation_name = current_data.get('violation_name')
    violation_found_id = current_data.get('violation_found_id')
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
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )
    description_callback_result = await send_callback_with_message(dp, bot, user_id=user_id, callback_data=f'description_{violation_dict_id}')
    assert description_callback_result is not UNHANDLED
    outgoing_callback: TelegramType = bot.get_request()
    assert isinstance(outgoing_callback, AnswerCallbackQuery)
    assert outgoing_callback.text == 'Грязный пол во входной группе. Наличие сезонного мусора (листья, реагенты), Ковры на входе грязные, с разводами грязи, присутствует реагент.'
    assert outgoing_callback.show_alert is True

    await assert_add_content(dp, bot, fsm_context, violation_name='Загрязнения во входной группе')
    await assert_save_violation_found(dp, bot, violation_name='Загрязнения во входной группе')

    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert current_state == MfcStates.choose_violation
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
    assert current_data.get('time_to_correct') is None
    assert current_data.get('violation_detected') is None
    assert current_data.get('violation_dict_id') is None
    assert current_data.get('violation_found_id') is None
    assert current_data.get('violation_name') is None
    assert current_data.get('violation_pending') is None
    assert current_data.get('violations_completed') == ['Загрязнения во входной группе']
    assert current_data.get('zone') == 'Входная группа'

    await assert_choose_violation(dp, bot, fsm_context, violation_name='Мусор, посторонние предметы во входной группе')
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert current_state == MfcStates.add_content
    assert current_data.get('check_id') == check_id_test
    assert current_data.get('mfc_start') == mfc_start
    assert current_data.get('violation_name') == 'Мусор, посторонние предметы во входной группе'
    assert current_data.get('violation_detected') != violation_detected
    assert current_data.get('violation_found_id') != violation_found_id
    assert current_data.get('violation_dict_id') == 2
    assert current_data.get('violations_completed') == ['Загрязнения во входной группе']
    assert current_data.get('zone') == 'Входная группа'

    await assert_add_content(dp, bot, fsm_context, violation_name='Мусор, посторонние предметы во входной группе')
    await assert_save_violation_found(dp, bot, violation_name='Мусор, посторонние предметы во входной группе')

    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert current_state == MfcStates.choose_violation
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
    assert current_data.get('time_to_correct') is None
    assert current_data.get('violation_detected') is None
    assert current_data.get('violation_dict_id') is None
    assert current_data.get('violation_found_id') is None
    assert current_data.get('violation_name') is None
    assert current_data.get('violation_pending') is None
    assert current_data.get('violations_completed') == [
        'Загрязнения во входной группе', 'Мусор, посторонние предметы во входной группе']
    assert current_data.get('zone') == 'Входная группа'

    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    result = await send_message(dp, bot, user_id=user_id, text='⬅️ К выбору зоны')
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    await assert_send_message(bot, 'Выберите зону нарушения:')
    assert current_state == MfcStates.choose_zone
    assert current_data.get('violations_completed') == [
        'Загрязнения во входной группе', 'Мусор, посторонние предметы во входной группе']
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    result = await send_message(dp, bot, user_id=user_id, text='⛔️ Закончить проверку')
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendSticker)
    outgoing_message: TelegramType = bot.get_request()
    assert outgoing_message.text == MfcMessages.finish_check
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert current_state == MfcStates.choose_type_checking
    assert current_data.get('violations_completed') == []
    assert current_data.get('fil_') == 'ГП 107'
    assert current_data.get('mo') == 'ГП 107'
    assert current_data.get('mfc_user_id') == int(user_id)
    assert current_data.get('mfc_start') is None
    assert current_data.get('mfc_finish') is None
    assert current_data.get('mo_start') is None
    assert current_data.get('mo_finish') is None
    assert current_data.get('photo_id_mfc') is None
    assert current_data.get('photo_id_mo') is None
    assert current_data.get('time_to_correct') is None
    assert current_data.get('violation_detected') is None
    assert current_data.get('violation_dict_id') is None
    assert current_data.get('violation_found_id') is None
    assert current_data.get('violation_name') is None
    assert current_data.get('violation_pending') is None
    assert current_data.get('zone') is None
    await fsm_context.clear()
