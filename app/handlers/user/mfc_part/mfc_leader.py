import datetime as dt

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from app.database.repositories.get_reports import get_mfc_report
from app.filters.mfc_filters import MfcLeaderFilter
from app.handlers.messages import DefaultMessages, MfcLeaderMessages
from app.handlers.states import MfcLeaderStates
from app.keyboards.mfc_part import MfcLeaderKeyboards

router = Router()
router.message.filter(MfcLeaderFilter())


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=MfcLeaderMessages.start_message,
        reply_markup=MfcLeaderKeyboards().main_menu(),
    )
    await state.set_state(MfcLeaderStates.mfc_leader)


##############
# back_logic #
##############

@router.message(F.text.lower() == 'назад')
async def back_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MfcLeaderStates.mfc_leader:
        await state.clear()
        await message.answer(
            text=MfcLeaderMessages.start_message,
            reply_markup=MfcLeaderKeyboards().main_menu(),
        )
    elif current_state == MfcLeaderStates.get_start_period:
        await state.set_state(MfcLeaderStates.mfc_leader)
        await message.answer(
            text=MfcLeaderMessages.start_message,
            reply_markup=MfcLeaderKeyboards().main_menu(),
        )
    elif current_state in (
        MfcLeaderStates.get_end_period,
        MfcLeaderStates.full_period
    ):
        await state.set_state(MfcLeaderStates.get_start_period)
        await message.answer(
            text='<b>Выберите начало периода:</b> ',
            reply_markup=await SimpleCalendar().start_calendar()
        )
        await state.update_data(
            start_period=None,
            finish_period=None
        )
    else:
        await message.answer(
            text=DefaultMessages.something_wrong,
            reply_markup=message.reply_markup,
        )

##############
# main_logic #
##############


@router.message(F.text.lower() == 'посмотреть отчет о работе сотрудников мфц')
async def get_period(message: Message, state: FSMContext):
    await message.answer(
        '<b>Выберите начало периода:</b> ',
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await state.set_state(state=MfcLeaderStates.get_start_period)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(MfcLeaderStates.get_start_period))
async def start_period_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        show_alerts=True
    )
    calendar.set_dates_range(dt.datetime(2022, 1, 1), dt.datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(
            start_period=date.isoformat()
        )
        await callback_query.message.answer(
            text='<b>Выберите конец периода:</b> ',
            reply_markup=await SimpleCalendar(selected_date=date).start_calendar()
        )
        await state.set_state(MfcLeaderStates.get_end_period)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(MfcLeaderStates.get_end_period))
async def end_period_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = await state.get_data()
    start_period = dt.datetime.fromisoformat(data['start_period'])
    calendar = SimpleCalendar(
        show_alerts=True,
        selected_date=start_period
    )
    calendar.set_dates_range(dt.datetime(2022, 1, 1), dt.datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(
            finish_period=date.isoformat()
        )

        await callback_query.message.answer(
            text=f"Отчетный период: <b>{dt.datetime.fromisoformat(data['start_period']).strftime('%d-%m-%Y')} - {date.strftime('%d-%m-%Y')}</b>\nНажмите <b>Получить отчет</b> для получения отчета",
            reply_markup=MfcLeaderKeyboards().get_report()
        )
        await state.set_state(MfcLeaderStates.full_period)


@router.message(F.text.lower() == 'получить отчет', StateFilter(MfcLeaderStates.full_period))
async def get_report(message: Message, state: FSMContext):
    mfc_report_doc = await get_mfc_report()

    await message.answer_document(document=mfc_report_doc, caption='Отправляю отчет')

    # await message.answer(
    #     text='Здесь будет отправлен отчет',
    #     reply_markup=MfcLeaderKeyboards().finish_process()
    # )
    await state.set_state(MfcLeaderStates.finish_stage)


@router.message(F.text.lower() == 'закончить', StateFilter(MfcLeaderStates.finish_stage))
async def finish_report(message: Message, state: FSMContext):
    await message.answer(
        'Спасибо, работа закончена!',
        reply_markup=MfcLeaderKeyboards().main_menu()
    )
    await state.clear()
    await state.set_state(MfcLeaderStates.mfc_leader)
