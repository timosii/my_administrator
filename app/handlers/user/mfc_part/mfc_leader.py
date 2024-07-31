import datetime as dt
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.filters.mfc_filters import MfcLeaderFilter
from app.handlers.messages import MfcLeaderMessages
from app.handlers.states import MfcLeaderStates
from app.keyboards.mfc_part import MfcLeaderKeyboards
from aiogram.types import CallbackQuery, InputMediaPhoto, Message, ReplyKeyboardRemove
from aiogram.filters.callback_data import CallbackData

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale



router = Router()
router.message.filter(MfcLeaderFilter())


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MfcLeaderMessages.start_message,
        reply_markup=MfcLeaderKeyboards().main_menu(),
    )
    await state.set_state(MfcLeaderStates.mfc_leader)


##############
# back_logic #
##############

@router.message(F.text.lower() == 'назад', StateFilter(MfcLeaderStates.mfc_leader))
async def back_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=MfcLeaderMessages.start_message,
        reply_markup=MfcLeaderKeyboards().main_menu(),
    )


@router.message(F.text.lower() == 'посмотреть отчет о работе сотрудников мфц', StateFilter(MfcLeaderStates.mfc_leader))
async def get_report(message: Message, state: FSMContext):

    await message.answer(
        text=MfcLeaderMessages.choose_period,
        reply_markup=MfcLeaderKeyboards().get_report(),
    )
    await state.set_state(state=MfcLeaderStates.get_report)


@router.message(F.text.lower() == 'выбрать период', StateFilter(MfcLeaderStates.get_report))
async def get_period(message: Message, state: FSMContext):

    await message.answer(
        "Выберите начало периода: ",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await state.set_state(state=MfcLeaderStates.get_start_period)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(MfcLeaderStates.get_start_period))
async def process_simple_calendar(state: FSMContext, callback_query: CallbackQuery, callback_data: CallbackData):
    calendar = SimpleCalendar(
        show_alerts=True
    )
    calendar.set_dates_range(dt.datetime(2022, 1, 1), dt.datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data({'start_period' : date})
        await callback_query.message.answer(
            f'Вы выбрали начало периода: {date.strftime("%d-%m-%Y")}\nВыберите конец периода:',
            reply_markup=await SimpleCalendar().start_calendar()
        )
        await state.set_state(MfcLeaderStates.get_end_period)

@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(MfcLeaderStates.get_end_period))
async def process_simple_calendar(state: FSMContext, callback_query: CallbackQuery, callback_data: CallbackData):
    calendar = SimpleCalendar(
        show_alerts=True
    )
    calendar.set_dates_range(dt.datetime(2022, 1, 1), dt.datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data({'finish_period' : date})
        await callback_query.message.answer(
            f'Вы выбрали конец периода: {date.strftime("%d-%m-%Y")}\nВыберите конец периода:',
            reply_markup=await SimpleCalendar().start_calendar()
        )
        await state.set_state(MfcLeaderStates.full_period)

