from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import Chat, Message, Update, User

from app.handlers.states import MfcStates, MoPerformerStates
from tests.config import settings
from tests.utils import form_greeting

user_id_mfc = settings.TEST_ID_MFC
user_id_mo = settings.TEST_ID_MO


@pytest.mark.asyncio(scope='session')
@pytest.mark.parametrize(
    'expected_message, user_id, first_name, expected_state, expected_data',
    [
        [f'{form_greeting()}, Тест!\nПожалуйста, введите <b>номер</b> поликлиники для проверки:',
         user_id_mfc, 'Тест', MfcStates.choose_mo, {'mfc_user_id': int(user_id_mfc)}],
        [f'{form_greeting()}, Тест Тестович!\nВы можете выбрать активные уведомления, активные проверки или перенесенные нарушения',
         user_id_mo, 'Тест Тестович', MoPerformerStates.mo_performer, {'fil_': 'ГП 107', 'mo': 'ГП 107', 'mo_user_id': int(user_id_mo)}]
    ]
)
async def test_cmd_start_mfc(dp, bot, expected_message: str, user_id: int, first_name: str, expected_state: FSMContext, expected_data: dict):
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(None)
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    user = User(id=user_id, is_bot=False, first_name=first_name)
    message = Message(
        message_id=1,
        chat=chat,
        from_user=user,
        text='/start',
        date=datetime.now()
    )
    result = await dp.feed_update(
        bot,
        Update(message=message, update_id=1)
    )

    assert result is not UNHANDLED
    outgoing_message: TelegramType = bot.get_request()
    current_state = await fsm_context.get_state()
    current_data = await fsm_context.get_data()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == expected_message
    assert current_state == expected_state
    assert current_data == expected_data
