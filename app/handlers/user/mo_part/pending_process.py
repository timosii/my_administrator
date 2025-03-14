import asyncio
import datetime as dt
from uuid import UUID

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from loguru import logger

from app.database.schemas.check_schema import CheckUpdate
from app.database.schemas.violation_found_schema import (
    ViolationFoundClearData,
    ViolationFoundOut,
    ViolationFoundUpdate,
)
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService
from app.filters.default import not_constants
from app.filters.mo_filters import MoPerformerFilter
from app.handlers.messages import MoPerformerMessages
from app.handlers.states import MoPerformerStates
from app.handlers.user.mo_part.performer_card_constructor import MoPerformerCard
from app.keyboards.mo_part import MoPerformerKeyboards

router = Router()
router.message.filter(MoPerformerFilter())


@router.callback_query(
    F.data.startswith('pending_'),
    StateFilter(MoPerformerStates.mo_performer,
                MoPerformerStates.pending_period)
)
async def move_to_pending(callback: CallbackQuery,
                          state: FSMContext,
                          ):

    violation_found_id = str(callback.data.split('_')[1])
    await state.update_data(
        pending_vio=violation_found_id
    )
    data = await state.get_data()
    current_time = dt.datetime.now(dt.timezone.utc)
    await state.update_data(
        mo_user_id=callback.from_user.id,
        mo_start=current_time.isoformat() if not data.get('mo_start') else data['mo_start']
    )
    await callback.answer(
        text=MoPerformerMessages.move_to_pending_alert, show_alert=True)
    await callback.message.answer(
        text=MoPerformerMessages.choose_pending_period,
        reply_markup=await SimpleCalendar().start_calendar()
    )

    await state.set_state(MoPerformerStates.pending_period)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(MoPerformerStates.pending_period))
async def start_period_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        show_alerts=True
    )
    calendar.set_dates_range(dt.datetime(2022, 1, 1), dt.datetime(2025, 12, 31))
    logger.debug(f'CANCEL: {callback_data.act}')
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if callback_data.act == 'CANCEL':
        await callback_query.message.delete()
        await state.set_state(MoPerformerStates.mo_performer)
    if selected:
        if (date + dt.timedelta(days=1)) < dt.datetime.today():
            logger.debug(f'DATE: {date}')
            logger.debug(f'TODAY: {dt.datetime.today()}')
            await callback_query.answer(text='Дата переноса не может быть меньше сегодняшней',
                                        show_alert=True)
            await callback_query.message.delete()
            await callback_query.message.answer(
                text=MoPerformerMessages.choose_pending_period,
                reply_markup=await SimpleCalendar().start_calendar()
            )
            return
        logger.info(f'ВЫБРАННАЯ ДАТА: {date}')
        await state.update_data(
            pending_period=date.isoformat()
        )
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=await MoPerformerMessages.pending_period(pending_date=date)
        )
        await callback_query.message.answer(
            text=MoPerformerMessages.add_pending_comm,
            reply_markup=await MoPerformerKeyboards().just_cancel()
        )
        await state.set_state(MoPerformerStates.pending_process)


@router.message(
    F.text,
    not_constants,
    StateFilter(MoPerformerStates.pending_process)
)
async def add_comm_pending_text(
        message: Message,
        state: FSMContext,
        violation_found_obj: ViolationFoundService = ViolationFoundService(),
        check_obj: CheckService = CheckService()):

    comm_mo = message.text

    data = await state.get_data()
    mo_user_id = data['mo_user_id']
    violation_found_id = data['pending_vio']
    pending_period = dt.datetime.fromisoformat(data['pending_period'])
    violation_found_out = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    current_time = dt.datetime.now(dt.timezone.utc)
    check_id: str = data[f'vio_{violation_found_id}']['check_id']

    current_check = await check_obj.get_check_by_id(check_id=UUID(check_id))

    if not current_check.mo_start:
        check_upd_mo_start = CheckUpdate(
            mo_start=current_time
        )
        await check_obj.update_check(check_id=check_id, check_update=check_upd_mo_start)
        logger.info('MO_START time updated from current_time')

    if violation_found_out.is_task:
        check_upd = CheckUpdate(
            mo_finish=current_time,
        )
        await check_obj.update_check(check_id=check_id, check_update=check_upd)
        await state.update_data(
            mo_start=None
        )

        await state.update_data(
            **ViolationFoundClearData().model_dump(mode='json')
        )

    order_before_pending = await MoPerformerCard(
        data=data
    ).get_index_violation_found(violation_found_out=violation_found_out)
    if order_before_pending is None:
        return

    violation_found_out_after_pending = violation_found_out.model_copy()
    violation_found_out_after_pending.is_pending = True
    violation_found_out_after_pending.comm_mo = comm_mo
    await state.update_data(
        {
            f'vio_{violation_found_id}': violation_found_out_after_pending.model_dump(mode='json')
        }
    )

    data = await state.get_data()
    await violation_found_obj.update_violation(
        violation_found_id=violation_found_id,
        violation_update=ViolationFoundUpdate(
            is_pending=True,
            mo_user_id=mo_user_id,
            comm_mo=f'При переносе:\n{comm_mo}',
            violation_pending=dt.datetime.now(dt.timezone.utc),
            pending_period=pending_period
        )
    )
    reply_obj = await MoPerformerCard(
        data=data
    ).get_pending_process(
        order=order_before_pending,
        violation_found_out=violation_found_out
    )

    await message.answer(
        text=MoPerformerMessages.comm_added
    )
    await message.answer(
        text=MoPerformerMessages.pending_continue
    )
    await message.answer_sticker(
        sticker=MoPerformerMessages.watch_sticker
    )
    await asyncio.sleep(3)

    if not reply_obj:
        if violation_found_out.is_task:
            await message.answer(
                text=MoPerformerMessages.no_violations_in_tasks,
                reply_markup=await MoPerformerKeyboards().check_or_tasks()
            )
        else:
            await message.answer(
                text=MoPerformerMessages.no_violations_after_pending,
                reply_markup=await MoPerformerKeyboards().check_or_tasks()
            )
    else:
        await message.answer_photo(
            **reply_obj.model_dump(mode='json')
        )
    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    F.text.lower() == 'отменить',
    StateFilter(MoPerformerStates.pending_process,
                MoPerformerStates.pending_period)
)
async def add_comm_pending_cancel(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    violation_found_id = data['pending_vio']

    violation_found_out = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    reply_obj = await MoPerformerCard(data=data).cancel_process(
        violation_found_out=violation_found_out
    )

    if not reply_obj:
        await message.answer(text=MoPerformerMessages.no_violations_after_pending)
        return

    await message.answer(
        text=MoPerformerMessages.continue_check,
        reply_markup=await MoPerformerKeyboards().check_or_tasks()
    )

    await message.answer_photo(
        **reply_obj.model_dump(mode='json')
    )

    if violation_found_out.is_task:
        await state.update_data(
            {
                'mo_start': None
            }
        )

    await state.update_data(
        **ViolationFoundClearData().model_dump(mode='json')
    )
    await state.update_data(
        pending_vio=None
    )

    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    ~F.text,
    StateFilter(MoPerformerStates.pending_process,
                MoPerformerStates.pending_period)
)
async def wrong_add_content(
    message: Message,
):
    await message.answer(
        text=MoPerformerMessages.add_comm_pending
    )
