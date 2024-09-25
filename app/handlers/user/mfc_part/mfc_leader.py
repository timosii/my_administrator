import datetime as dt

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from app.database.repositories.get_reports import get_mfc_report
from app.database.schemas.user_schema import UserUpdate
from app.database.services.users import UserService
from app.filters.mfc_filters import MfcLeaderFilter
from app.handlers.messages import MfcLeaderMessages
from app.handlers.states import MfcLeaderStates
from app.keyboards.mfc_part import MfcLeaderKeyboards
from app.view.users import get_user_info

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
            start_date=None,
            finish_date=None
        )
    elif current_state == MfcLeaderStates.vacation:
        await state.set_state(MfcLeaderStates.mfc_leader)
        await message.answer(
            text=MfcLeaderMessages.start_message,
            reply_markup=MfcLeaderKeyboards().main_menu()
        )

    else:
        await state.set_state(MfcLeaderStates.mfc_leader)
        await message.answer(
            text=MfcLeaderMessages.start_message,
            reply_markup=MfcLeaderKeyboards().main_menu(),
        )

##############
# main_logic #
##############


@router.message(
    F.text.lower() == 'посмотреть отчет о работе сотрудников мфц',
    StateFilter(MfcLeaderStates.mfc_leader)
)
async def get_period(message: Message, state: FSMContext):
    await message.answer(
        text='<b>Выберите начало периода:</b> ',
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
            start_date=date.isoformat()
        )
        await callback_query.message.answer(
            text='<b>Выберите конец периода:</b> ',
            reply_markup=await SimpleCalendar(selected_date=date).start_calendar()
        )
        await state.set_state(MfcLeaderStates.get_end_period)


@router.callback_query(SimpleCalendarCallback.filter(),
                       StateFilter(MfcLeaderStates.get_end_period))
async def end_period_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = await state.get_data()
    start_date = dt.datetime.fromisoformat(data['start_date'])
    calendar = SimpleCalendar(
        show_alerts=True,
        selected_date=start_date
    )
    calendar.set_dates_range(dt.datetime(2022, 1, 1), dt.datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(
            end_date=date.isoformat()
        )

        await callback_query.message.answer(
            text=f"Отчетный период: <b>{dt.datetime.fromisoformat(data['start_date']).strftime('%d-%m-%Y')} - {date.strftime('%d-%m-%Y')}</b>\nНажмите <b>Получить отчет</b> для получения отчета",
            reply_markup=MfcLeaderKeyboards().get_report()
        )
        await state.set_state(MfcLeaderStates.full_period)


@router.message(F.text.lower() == 'получить отчет',
                StateFilter(MfcLeaderStates.full_period))
async def get_report(message: Message, state: FSMContext):
    data = await state.get_data()
    start_date = dt.datetime.fromisoformat(data['start_date']).strftime('%Y-%m-%d')
    end_date = dt.datetime.fromisoformat(data['end_date']).strftime('%Y-%m-%d')
    mfc_report_doc = await get_mfc_report(
        start_date=start_date,
        end_date=end_date
    )

    if not mfc_report_doc:
        await message.answer(text='Нет данных за выбранный период',
                             reply_markup=MfcLeaderKeyboards().finish_process())
    else:
        await message.answer_document(document=mfc_report_doc,
                                      caption='Отправляю отчет',
                                      reply_markup=MfcLeaderKeyboards().finish_process())
    await state.set_state(MfcLeaderStates.finish_stage)


@router.message(
    F.text.lower() == 'отпуск сотрудника',
    StateFilter(MfcLeaderStates.mfc_leader)
)
async def employee_to_vacation(
    message: Message,
    state: FSMContext
):
    await message.answer(
        text=MfcLeaderMessages.choose_surname,
        reply_markup=MfcLeaderKeyboards().just_back()
    )
    await state.set_state(MfcLeaderStates.vacation)


@router.message(
    F.text,
    StateFilter(MfcLeaderStates.vacation)
)
async def get_surname(
    message: Message,
    state: FSMContext
):
    surname = message.text
    users = await UserService().get_mfc_users_by_surname(last_name=surname)
    if not users:
        await message.answer(
            text=MfcLeaderMessages.no_employee,
            reply_markup=MfcLeaderKeyboards().main_menu()
        )
        await state.set_state(MfcLeaderStates.mfc_leader)
        return

    else:
        for user in users:
            text = await get_user_info(user=user, is_mfc=True)
            additional_text = '\nСтатус: <b>в отпуске</b>' if user.is_vacation else '\nСтатус: <b>не в отпуске</b>'
            await message.answer(
                text=text + additional_text,
                reply_markup=MfcLeaderKeyboards().choose_employee(user_id=user.user_id)
            )


@router.callback_query(
    F.data.startswith('choose_employee_'),
    StateFilter(MfcLeaderStates.vacation)
)
async def user_to_vacation(
    callback: CallbackQuery,
    state: FSMContext
):
    user_id = int(callback.data.split('_')[-1])
    await state.update_data(
        user_vacation=user_id
    )
    user = await UserService().get_user_by_id(user_id=user_id)
    if not user:
        await callback.message.answer(
            text=MfcLeaderMessages.no_user,
            reply_markup=MfcLeaderKeyboards().just_back()
        )
        await callback.answer()
        return
    if user.is_vacation is True:
        user.is_vacation = False
        await UserService().update_user(
            user_id=user_id,
            user_update=UserUpdate(
                **user.model_dump()
            )
        )
        await callback.message.answer(
            text=MfcLeaderMessages.from_vacation_success,
            reply_markup=MfcLeaderKeyboards().main_menu()
        )

    else:
        user.is_vacation = True
        await UserService().update_user(
            user_id=user_id,
            user_update=UserUpdate(
                **user.model_dump()
            )
        )
        await callback.message.answer(
            text=MfcLeaderMessages.to_vacation_success,
            reply_markup=MfcLeaderKeyboards().main_menu()
        )
    await callback.answer()
    await state.set_state(MfcLeaderStates.mfc_leader)


@router.message(F.text.lower() == 'закончить', StateFilter(MfcLeaderStates.finish_stage))
async def finish_report(message: Message, state: FSMContext):
    await message.answer(
        'Спасибо, работа закончена!',
        reply_markup=MfcLeaderKeyboards().main_menu()
    )
    await state.clear()
    await state.set_state(MfcLeaderStates.mfc_leader)
