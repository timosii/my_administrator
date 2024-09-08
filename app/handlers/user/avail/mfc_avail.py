import datetime as dt
import re

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.database.services.users import UserService
from app.filters.mfc_filters import MfcAvailFilter
from app.handlers.messages import DefaultMessages, MfcMessages
from app.handlers.states import MfcAvailStates, MfcStates
from app.keyboards.mfc_part import MfcKeyboards

OUT = '''
<b>Филиал:</b> {fil_}
<b>Специальность:</b> {spec}
<b>Полис:</b> {oms}
<b>Телефон:</b> {phone}
<b>Время:</b> {ud_time}
'''


SPECS = [
    'Акушер-гинеколог (детский)',
    'Аллерголог',
    'Гастроэнтеролог',
    'Инфекционист',
    'Кардиолог',
    'Колопроктолог',
    'Невролог',
    'Нефролог (детский)',
    'Оториноларинголог',
    'Офтальмолог',
    'Пульмонолог',
    'Уролог',
    'Участковый врач',
    'Хирург',
    'Эндокринолог',
    'ЭХО-КГ',
    'ЭКГ',
    'Гастроскопия',
    'Холтер',
    'ФВД',
    'Флюорография',
    'УЗИ',
    'УЗДГ-УЗДС-БЦА',
    'СМАД',
    'Рентген',
    'Маммография',
    'КТ',
    'МРТ',
    'Взятие крови',
]


def format_phone(phone_str):
    phone_str = re.sub(r'\D', '', phone_str)
    try:
        if phone_str[0] in ['7', '8']:
            phone_str = phone_str[1:]
    except IndexError:
        return 'отсутствует'
    return phone_str


def check_phone(phone_str):
    return len(phone_str) == 10


def format_oms(oms_str):
    oms_str = re.sub(r'\D', '', oms_str)
    return oms_str


def check_oms(oms_str):
    return len(oms_str) in [16, 9]


# "Полис ОМС некорректный",
# "Телефон некорректный"

router = Router()
router.message.filter(MfcAvailFilter())


@router.message(
    F.text.lower() == 'доступность у инфомата',
    StateFilter(MfcStates.choose_type_checking)
)
async def avail_process(
    message: Message,
    state: FSMContext,
):
    await message.answer(
        text='Вам будет предложено ввести информацию о невозможности записи у инфомата.\nПосле этого она будет отправлена в МО',
        reply_markup=MfcKeyboards().avail_cancel()
    )
    await message.answer(
        text='Выберите специальность:',
        reply_markup=MfcKeyboards().get_specs()
    )
    await state.set_state(MfcAvailStates.avail_main)


@router.callback_query(
    F.data.startswith('spec_'),
    StateFilter(MfcAvailStates.avail_main)
)
async def choose_oms_avail(
    callback: CallbackQuery,
    state: FSMContext,
):
    spec = callback.data.split('_')[-1]
    await state.update_data(
        spec=spec
    )
    await callback.message.answer(
        text='Введите <b>полис ОМС:</b>',
        reply_markup=MfcKeyboards().avail_cancel()
    )
    await callback.answer()
    await state.set_state(MfcAvailStates.choose_oms)


@router.message(
    F.text,
    StateFilter(MfcAvailStates.choose_oms)
)
async def get_number(
    message: Message,
    state: FSMContext,
):
    oms_str = message.text
    oms_format = format_oms(oms_str)
    if not check_oms(oms_format):
        await message.answer(
            text='Полис некорректный, попробуйте ещё раз',
            reply_markup=MfcKeyboards().avail_cancel()
        )
        return

    await state.update_data(
        oms=oms_format
    )
    await message.answer(
        text='Введите <b>номер телефона:</b>',
        reply_markup=MfcKeyboards().avail_cancel()
    )

    await state.set_state(MfcAvailStates.get_number)


@router.message(
    F.text,
    StateFilter(MfcAvailStates.get_number)
)
async def process_sending_avail(
    message: Message,
    state: FSMContext,
):
    phone = message.text
    phone_format = format_phone(phone)
    if not check_phone(phone_format):
        await message.answer(
            text='Телефон некорректный, попробуйте ещё раз',
            reply_markup=MfcKeyboards().avail_cancel()
        )
        return

    ud_time = dt.datetime.now()
    await state.update_data(
        phone=phone_format,
        ud_time=ud_time.strftime('%H:%M')
    )
    data = await state.get_data()
    res = OUT.format(
        fil_=data['fil_'],
        spec=data['spec'],
        oms=data['oms'],
        phone=data['phone'],
        ud_time=data['ud_time']
    )

    await message.answer(
        text=f'В МО будет отправлено сообщение:\n{res}\nОтправляем?',
        reply_markup=MfcKeyboards().avail_cancel_yes()
    )
    await state.set_state(MfcAvailStates.form_send_mo)


@router.message(
    F.text.lower() == 'да',
    StateFilter(MfcAvailStates.form_send_mo)
)
async def form_send_avail(
    message: Message,
    state: FSMContext,
    user: UserService = UserService(),
):
    data = await state.get_data()
    fil_ = data['fil_']
    res = OUT.format(
        fil_=fil_,
        spec=data['spec'],
        oms=data['oms'],
        phone=data['phone'],
        ud_time=data['ud_time']
    )

    performers = await user.get_avail_performer_by_fil(fil_=fil_)
    if not performers:
        await message.answer(
            text=MfcMessages.zero_performers
        )
        return

    norm_users_count = 0
    troubles_user_count = 0
    for performer in performers:
        try:
            await message.bot.send_message(
                chat_id=performer.user_id,
                text=MfcMessages.there_is_new_ud,
            )
            await message.bot.send_message(
                chat_id=performer.user_id,
                text=res,
            )
            norm_users_count += 1
        except TelegramBadRequest:
            troubles_user_count += 1
            continue

    if norm_users_count > 0:
        await message.answer(
            text=MfcMessages.violation_sending(fil_=fil_, count=norm_users_count, flag=True),
            reply_markup=ReplyKeyboardRemove()
        )

    if troubles_user_count > 0:
        await message.answer(
            text=MfcMessages.violation_sending(fil_=fil_, count=troubles_user_count, flag=False),
            reply_markup=ReplyKeyboardRemove()
        )

    await message.answer(
        text='Возвращаемся в меню',
        reply_markup=MfcKeyboards().main_menu()
    )

    await state.update_data(
        spec=None,
        oms=None,
        phone=None,
        ud_time=None
    )
    await state.set_state(MfcStates.choose_type_checking)


@router.message(
    F.text.lower() == 'отменить',
    StateFilter(
        MfcAvailStates.avail_main,
        MfcAvailStates.choose_oms,
        MfcAvailStates.get_number,
        MfcAvailStates.form_send_mo
    )
)
async def avail_cancel_logic(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        spec=None,
        oms=None,
        phone=None,
        ud_time=None
    )

    await message.answer(
        text=MfcMessages.main_menu,
        reply_markup=MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.choose_type_checking)


@router.message(
    StateFilter(
        MfcAvailStates.avail_main,
        MfcAvailStates.choose_oms,
        MfcAvailStates.get_number,
        MfcAvailStates.form_send_mo
    )
)
async def wrong_avail(
    message: Message,
):
    await message.answer(
        text=DefaultMessages.something_wrong
    )
