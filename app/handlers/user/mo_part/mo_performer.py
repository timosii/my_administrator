import time
import json
import datetime as dt
from loguru import logger
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mo_part import MoPerformerKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import MoPerformerMessages, DefaultMessages
from app.handlers.states import MoPerformerStates
from app.filters.mo_filters import MoPerformerFilter
from app.filters.default import not_constants
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService
from app.database.services.users import UserService
from app.view.cards import FormCards
from app.database.schemas.check_schema import CheckOut, CheckUpdate
from app.database.schemas.violation_found_schema import (
    ViolationFoundOut,
    ViolationFoundUpdate,
)
from app.utils.utils import get_index_by_violation_id

router = Router()
router.message.filter(MoPerformerFilter())


@router.message(Command('start'))
async def cmd_start(
    message: Message, state: FSMContext, user_obj: UserService = UserService()
):
    user = message.from_user
    mo = await user_obj.get_user_mo(user_id=user.id)
    fil_ = await user_obj.get_user_fil(user_id=user.id)
    logger.info("User {0} {1} passed authorization".format(user.id, user.username))
    await state.clear()
    await state.update_data(mo_user_id=user.id,
                            mo=mo,
                            fil_=fil_
                            )
    await message.answer(
        text=MoPerformerMessages.start_message,
        reply_markup=MoPerformerKeyboards().check_or_tasks(),
    )
    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    F.text.lower() == "активные проверки",
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_active_violations(
    message: Message, state: FSMContext,
    check_obj: CheckService = CheckService(),
    user_obj: UserService=UserService()
):
    user = message.from_user
    mo = await user_obj.get_user_mo(user_id=user.id)
    fil_ = await user_obj.get_user_fil(user_id=user.id)
    await state.update_data(mo_user_id=user.id,
                            mo=mo,
                            fil_=fil_
                            )
    data = await state.get_data()
    fil_ = data["fil_"]
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
            reply_markup=message.reply_markup,
        )
    else:
        for check in checks:
            check_out = await check_obj.form_check_out(check=check)
            text_mes = check_out.form_card_check_out()
            keyboard = MoPerformerKeyboards().get_under_check(check_id=check.check_id) if check_out.violations_count > 0 else MoPerformerKeyboards().get_under_check_zero_violations(check_id=check.check_id)
            await message.answer(text=text_mes, reply_markup=keyboard)


@router.callback_query(
    F.data.startswith('violationszero_'),
    StateFilter(MoPerformerStates.mo_performer)
)
async def check_zero_violations(callback: CallbackQuery,
                          state: FSMContext,
                          check_obj:CheckService=CheckService()):
    check_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    await callback.answer(
        text=MoPerformerMessages.finish_check_zero_violations,
        show_alert=True
    )
    current_time = dt.datetime.now(dt.timezone.utc)
    check_upd = CheckUpdate(
        mo_user_id=data["mo_user_id"],
        mo_start=current_time,
        mo_finish=current_time,
    )
    await check_obj.update_check(check_id=check_id, check_update=check_upd)
    await callback.message.delete()

@router.message(
    F.text.lower() == "активные уведомления",
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_active_tasks(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    user_obj: UserService=UserService()
):
    user = message.from_user
    mo = await user_obj.get_user_mo(user_id=user.id)
    fil_ = await user_obj.get_user_fil(user_id=user.id)
    await state.update_data(mo_user_id=user.id,
                            mo=mo,
                            fil_=fil_
                            )
    data = await state.get_data()
    fil_ = data["fil_"]
    tasks = await violation_obj.get_active_violations_by_fil(fil_=fil_)
    await violation_obj.form_task_replies(
        message=message,
        state=state,
        fil_=fil_,
        # mo_start=data.get("mo_start"),
        tasks=tasks,
    )


@router.message(
    F.text.lower() == 'перенесенные нарушения',
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_pending_violations_found(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    user_obj: UserService=UserService()
):
    user = message.from_user
    mo = await user_obj.get_user_mo(user_id=user.id)
    fil_ = await user_obj.get_user_fil(user_id=user.id)
    await state.update_data(mo_user_id=user.id,
                            mo=mo,
                            fil_=fil_
                            )
    data = await state.get_data()
    fil_ = data["fil_"]
    violations_found_pending = await violation_obj.get_pending_violations_by_fil(fil_=fil_)
    await violation_obj.form_violations_pending_replies(
        message=message,
        state=state,
        fil_=fil_,
        violations_pending=violations_found_pending,
    )

@router.callback_query(
    F.data.startswith('pending_'),
    StateFilter(MoPerformerStates.mo_performer)
)
async def move_to_pending(callback: CallbackQuery,
                          state: FSMContext,
                          violation_found_obj: ViolationFoundService=ViolationFoundService(),
                          check_obj:CheckService=CheckService()):
    
    violation_found_id = int(callback.data.split("_")[1])

    data = await state.get_data()
    await callback.message.answer(
        text=MoPerformerMessages.move_to_pending,
        reply_markup=MoPerformerKeyboards().check_or_tasks()
    )
    await callback.answer(text=MoPerformerMessages.move_to_pending_alert, show_alert=True)
    
    violation_found_out = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    if violation_found_out.is_task:
        current_time = dt.datetime.now(dt.timezone.utc)
        check_upd = CheckUpdate(
            mo_user_id=data["mo_user_id"],
            mo_start=current_time,
            mo_finish=current_time,
        )
        check_id = data["check_id"]
        await check_obj.update_check(check_id=check_id, check_update=check_upd)
        await state.update_data(mo_start=None)
        await state.update_data(
        {   
            'check_id': None,
            "violation_found_id": None,
            "photo_id_mo": None,
            "comm_mo": None,
            "comm_mfc": None,
            "is_take": None,
            "is_task": None,
            "photo_id_mfc": None,
            "photo_id_mo": None,
            "time_to_correct": None,
            "violation_detected": None,
            "violation_dict_id": None,
            "violation_found_id": None,
            "violation_name": None,
            "zone": None,
            'is_pending': None,
            'violation_pending': None
        }
    )

    violation_found_out.is_pending = True
    await state.update_data(
        {f"vio_{violation_found_id}": violation_found_out.model_dump(mode='json')}
    )
    data = await state.get_data()
    is_task = violation_found_out.is_task
    await violation_found_obj.update_violation(
        violation_found_id=violation_found_id,
        violation_update=ViolationFoundUpdate(
            is_pending=True,
            violation_pending=dt.datetime.now(dt.timezone.utc)
        )
    )

    if is_task:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == True) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
    else:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == False) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
    if not violation_out_objects:
        await callback.message.delete()
        return
    
    order = get_index_by_violation_id(
        objects=violation_out_objects,
        violation_found_id=violation_found_id
    )
    reply_obj = FormCards().form_reply(
        violations_out=violation_out_objects, order=order + 1 if len(violation_out_objects) > 1 else 0
    )

    photo_id = reply_obj.photo_id
    text_mes = reply_obj.text_mes
    keyboard = reply_obj.keyboard   
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo_id, caption=text_mes), reply_markup=keyboard
    )


@router.callback_query(
    F.data.startswith("take_"), 
    ~StateFilter(MoPerformerStates.correct_violation)
)
async def take_to_work(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService=ViolationFoundService(),
    user_obj: UserService=UserService()
):
    await state.set_state(MoPerformerStates.mo_performer)
    await state.clear()
    user = callback.from_user
    mo = await user_obj.get_user_mo(user_id=user.id)
    fil_ = await user_obj.get_user_fil(user_id=user.id)
    await state.update_data(mo_user_id=user.id,
                            mo=mo,
                            fil_=fil_
                            )
    violation_found_id = int(callback.data.split("_")[1])
    is_fixed = await violation_obj.is_violation_already_fixed(
        violation_found_id=violation_found_id
    )
    if is_fixed:
        await callback.answer(text="Нарушение уже исправлено")
        await callback.message.delete()
        return

    violation_in_db = await violation_obj.get_violation_found_by_id(
        violation_found_id=violation_found_id
    )
    violation_out = await violation_obj.form_violation_out(violation_in_db)
    current_time = dt.datetime.now(dt.timezone.utc)
    if violation_out.is_task:
        await state.update_data(
            **violation_out.model_dump(mode="json"),
            is_take=True,
            mo_start=current_time.isoformat(),
        )
    else:
        await state.update_data(
            **violation_out.model_dump(mode="json"),
            is_take=True,
            # mo_start=current_time.isoformat(),
        )

    text_mes = violation_out.violation_card()
    await state.update_data({
        f'vio_{violation_found_id}': violation_out.model_dump(mode='json')
    })
    await callback.message.answer(
        text=MoPerformerMessages.correct_mode(text_mes=text_mes),
        reply_markup=MoPerformerKeyboards().cancel_correct_mode(violation_found_id=violation_found_id)
    )
    await callback.answer()
    await state.set_state(MoPerformerStates.correct_violation)


@router.callback_query(
    F.data.startswith("take_") | F.data.startswith("correct_"),
    StateFilter(MoPerformerStates.correct_violation),
)
async def correct_first_violation(
    callback: CallbackQuery,
):
    await callback.answer(text=MoPerformerMessages.exit_first)


@router.callback_query(
    F.data.startswith("violations_"),
    StateFilter(MoPerformerStates.mo_performer)
)
async def get_violations(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    check_id = int(callback.data.split("_")[1])
    await state.update_data(
        check_id=check_id,
    )
    data = await state.get_data()
    await state.update_data({k: None for k in data.keys() if k.startswith("vio_")})
    violations = await violation_obj.get_violations_found_by_check(check_id=check_id)
    data = await state.get_data()
    current_time = dt.datetime.now(dt.timezone.utc)
    if not data.get("mo_start"):
        await state.update_data(mo_start=current_time.isoformat())

    await violation_obj.form_violations_replies(
        violations=violations, callback=callback, state=state
    )

@router.callback_query(
    F.data.startswith("next_") | F.data.startswith("prev_"),
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_violations_next_prev(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService=ViolationFoundService()
):
    violation_found_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    is_pending = violation_found_obj.is_pending
    is_task = violation_found_obj.is_task

    if is_pending:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_pending'] == True))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 1:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return

        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_violation_pending_reply(
            violations_out=violation_out_objects, order=order
        )

    elif is_task:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == True) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 1:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return
        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=order
        )

    else:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == False) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 1:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return
        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=order
        )


    photo_id = reply_obj.photo_id
    text_mes = reply_obj.text_mes
    keyboard = reply_obj.keyboard
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo_id, caption=text_mes), reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("next_") | F.data.startswith("prev_"),
    ~StateFilter(MoPerformerStates.mo_performer),
)
async def wrong_state(callback: CallbackQuery):
    await callback.answer(text="Вернитесь в режим выбора нарушений")


@router.callback_query(
    F.data.startswith("correct_"),
    StateFilter(MoPerformerStates.mo_performer)
)
async def process_correct_callback(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    violation_found_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    is_fixed = await violation_obj.is_violation_already_fixed(
        violation_found_id=violation_found_id
    )
    if is_fixed:
        await callback.answer(text="Нарушение уже исправлено")
        return

    violation_out = ViolationFoundOut(**data[f"vio_{violation_found_id}"])
    await state.update_data(
        **violation_out.model_dump(mode="json")
        )
    data = await state.get_data()
    if data.get('is_task') or not data.get('mo_start'):
        current_time = dt.datetime.now(dt.timezone.utc)
        await state.update_data(
            mo_user_id=callback.from_user.id,
            mo_start=current_time.isoformat()
        )

    text_mes = violation_out.violation_card()

    
    await callback.message.answer(
        text=MoPerformerMessages.correct_mode(text_mes=text_mes),
        reply_markup=MoPerformerKeyboards().cancel_correct_mode(violation_found_id=violation_found_id),
    )
    await state.set_state(MoPerformerStates.correct_violation)
    await callback.answer()


@router.callback_query(
    F.data.startswith('cancel_'),
    StateFilter(MoPerformerStates.correct_violation)
)
async def process_cancel_correct(
    callback: CallbackQuery,
    state: FSMContext,
):
    violation_found_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    is_pending = violation_found_obj.is_pending
    is_task = violation_found_obj.is_task

    if is_pending:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_pending'] == True))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 0:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return

        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_violation_pending_reply(
            violations_out=violation_out_objects, order=order
        )

    elif is_task:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == True) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 0:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return
        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=order
        )

    else:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == False) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 0:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return
        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=order
        )


    photo_id = reply_obj.photo_id
    text_mes = reply_obj.text_mes
    keyboard = reply_obj.keyboard
    await callback.message.answer_photo(
        photo=photo_id,
        caption=text_mes,
        reply_markup=keyboard
    )
    await callback.answer()
    if is_task:
        await state.update_data(
            {
                'mo_start': None
            }
        )

    await state.update_data(
        {
            # 'check_id': None,
            "violation_found_id": None,
            "photo_id_mo": None,
            "comm_mo": None,
            "comm_mfc": None,
            "is_take": None,
            "is_task": None,
            "photo_id_mfc": None,
            "photo_id_mo": None,
            "time_to_correct": None,
            "violation_detected": None,
            "violation_dict_id": None,
            "violation_found_id": None,
            "violation_name": None,
            "zone": None,
            'is_pending': None,
            'violation_pending': None
        }
    )
    await state.set_state(MoPerformerStates.mo_performer)


@router.message(F.photo,
                StateFilter(MoPerformerStates.correct_violation))
async def add_photo_handler(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    violation_found_id = data["violation_found_id"]
    photo_id_mo = message.photo[-1].file_id
    comm_mo = message.caption
    if not comm_mo:
        await message.answer(
            text='Вы не добавили комментарий к фотографии. Пожалуйста, повторите'
        )
        return
    await state.update_data(
        photo_id_mo=photo_id_mo,
        comm_mo=comm_mo
        )
    violation_found_out = ViolationFoundOut(**data[f"vio_{violation_found_id}"])
    await message.answer(
        text=MoPerformerMessages.finish_mes(violation_found_out.violation_name),
        reply_markup=MoPerformerKeyboards().save_violation_found(
            violation_found_id=violation_found_id
        ),
    )
    await state.set_state(MoPerformerStates.save_vio_update)

@router.callback_query(
    F.data.startswith('cancelsave_'),
    StateFilter(MoPerformerStates.save_vio_update)
)
async def cancel_save_process(
    callback: CallbackQuery,
    state: FSMContext
):
    violation_found_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    is_pending = violation_found_obj.is_pending
    is_task = violation_found_obj.is_task

    if is_pending:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_pending'] == True))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 0:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return

        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_violation_pending_reply(
            violations_out=violation_out_objects, order=order
        )

    elif is_task:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == True) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 0:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return
        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=order
        )

    else:
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**v)
                for k, v in data.items()
                if (k.startswith("vio_") and v and (v['is_task'] == False) and (v['is_pending'] == False))
            ],
            key=lambda x: x.violation_dict_id,
        )
        if len(violation_out_objects) == 0:
            await callback.answer(text=MoPerformerMessages.no_violations_buttons)
            return
        order = get_index_by_violation_id(
            objects=violation_out_objects, violation_found_id=violation_found_id
        )
        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=order
        )


    photo_id = reply_obj.photo_id
    text_mes = reply_obj.text_mes
    keyboard = reply_obj.keyboard
    await callback.message.answer_photo(
        photo=photo_id,
        caption=text_mes,
        reply_markup=keyboard
    )
    await callback.answer()
    if is_task:
        await state.update_data(
            {
                'mo_start': None
            }
        )
    await state.update_data(
        {
            # 'check_id': None,
            "violation_found_id": None,
            "photo_id_mo": None,
            "comm_mo": None,
            "comm_mfc": None,
            "is_take": None,
            "is_task": None,
            "photo_id_mfc": None,
            "photo_id_mo": None,
            "time_to_correct": None,
            "violation_detected": None,
            "violation_dict_id": None,
            "violation_found_id": None,
            "violation_name": None,
            "zone": None,
            'is_pending': None,
            'violation_pending': None
        }
    )
    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    F.text,
    not_constants,
    StateFilter(MoPerformerStates.correct_violation)
)
async def add_text_wrong(
    message: Message,
):
    await message.answer(
        text='Добавьте фотографию и комментарий к нарушению в качестве подписи к фото'
    )

@router.message(
        ~F.text & ~F.photo,
        StateFilter(MoPerformerStates.correct_violation)
        )
async def wrong_add_content(
    message: Message,
):
    await message.answer(
        text='Поддерживается только фото и текст (в качестве подписи к фото)'
    )

@router.callback_query(
    F.data.startswith("save_"),
    StateFilter(MoPerformerStates.save_vio_update),
)
async def save_violation_found_process(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    is_pending = data.get('is_pending')
    is_task = data.get("is_task")
    is_take = data.get("is_take")
    violation_found_id = int(callback.data.split("_")[1])
    current_time = dt.datetime.now(dt.timezone.utc)
    vio_upd = ViolationFoundUpdate(
        photo_id_mo=data["photo_id_mo"],
        comm_mo=data["comm_mo"],
        violation_fixed=current_time,
    )
    await violation_obj.update_violation(
        violation_found_id=violation_found_id, violation_update=vio_upd
    )
    await state.update_data(
        {
            "violation_found_id": None,
            "photo_id_mo": None,
            "comm_mo": None,
            "comm_mfc": None,
            f"vio_{violation_found_id}": None,
            "is_take": None,
            "is_task": None,
            "photo_id_mfc": None,
            "photo_id_mo": None,
            "time_to_correct": None,
            "violation_detected": None,
            "violation_dict_id": None,
            "violation_found_id": None,
            "violation_name": None,
            "zone": None,
            'is_pending': None,
            'violation_pending': None
        }
    )
    data = await state.get_data()

    if is_pending:
        await callback.message.answer(
            text=MoPerformerMessages.can_continue_or_finish,
            reply_markup=MoPerformerKeyboards().back_to_menu(),
        )
      
        fil_ = data["fil_"]
        violations_pending = await violation_obj.get_pending_violations_by_fil(fil_=fil_)
        await violation_obj.form_violations_pending_replies(
            message=callback.message,
            state=state,
            fil_=fil_,
            violations_pending=violations_pending,
        )

    elif is_task:
        check_id = data["check_id"]
        current_time = dt.datetime.now(dt.timezone.utc)
        check_upd = CheckUpdate(
            mo_user_id=data['mo_user_id'],
            mo_start=dt.datetime.fromisoformat(data["mo_start"]),
            mo_finish=current_time,
        )
        await check_obj.update_check(check_id=check_id, check_update=check_upd)
        await state.update_data(mo_start=None, check_id=None)
        await callback.message.answer(
            text=MoPerformerMessages.can_continue_or_finish,
            reply_markup=ReplyKeyboardRemove(),
        )
        fil_ = data["fil_"]
        tasks = await violation_obj.get_active_violations_by_fil(fil_=fil_)
        await violation_obj.form_task_replies(
            message=callback.message,
            state=state,
            fil_=fil_,
            tasks=tasks,
        )

    elif not is_take:
        await callback.message.answer(
            text=MoPerformerMessages.can_continue_or_finish,
            reply_markup=MoPerformerKeyboards().back_to_violations(),
        )
    else:
        await callback.message.answer(
            text=MoPerformerMessages.can_continue_or_finish,
            reply_markup=ReplyKeyboardRemove(),
        )


    await callback.answer(text=MoPerformerMessages.photo_comm_added, show_alert=True)
    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    F.text.lower() == "вернуться в меню", StateFilter(MoPerformerStates.mo_performer)
)
async def back_to_menu(
    message: Message,
):
    await message.answer(
        text=MoPerformerMessages.choose_check_task,
        reply_markup=MoPerformerKeyboards().check_or_tasks(),
    )

@router.message(
    F.text.lower() == "вернуться в меню", StateFilter(MoPerformerStates.correct_violation)
)
async def back_to_menu(
    message: Message,
):
    await message.answer(
        text=MoPerformerMessages.exit_first,
    )

@router.message(
    F.text.lower() == "продолжить проверку",
    StateFilter(MoPerformerStates.mo_performer),
)
async def correct_vio_process_continue(
    message: Message,
    state: FSMContext,
):
    await message.answer(
        text=MoPerformerMessages.continue_check, reply_markup=ReplyKeyboardRemove()
    )
    time.sleep(1)
    data = await state.get_data()
    check_id = data['check_id']
    violation_out_objects = sorted(
        [
            ViolationFoundOut(**v)
            for k, v in data.items()
            if (k.startswith("vio_") and v and (v['is_task'] == False) and (v['is_pending'] == False) and (v['check_id'] == check_id))
        ],
        key=lambda x: x.violation_dict_id,
    )

    if not violation_out_objects:
        await message.answer(
            text=MoPerformerMessages.no_violations,
            reply_markup=MoPerformerKeyboards().check_finished(),
        )

    else:
        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=0
        )
        photo_id = reply_obj.photo_id
        text_mes = reply_obj.text_mes
        keyboard = reply_obj.keyboard
        await message.answer_photo(
            photo=photo_id, caption=text_mes, reply_markup=keyboard
        )


@router.message(
    F.text.lower() == "закончить проверку",
    StateFilter(MoPerformerStates.mo_performer),
)
async def correct_vio_process_finish(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    check_id = data['check_id']
    violation_out_objects = sorted(
        [
            ViolationFoundOut(**v)
            for k, v in data.items()
            if (k.startswith("vio_") and v and (v['is_task'] == False) and (v['is_pending'] == False) and (v['check_id'] == check_id))
        ],
        key=lambda x: x.violation_dict_id,
    )
    if violation_out_objects:
        await message.answer(
            text=MoPerformerMessages.cant_finish, reply_markup=message.reply_markup
        )
        return
    current_time = dt.datetime.now(dt.timezone.utc)
    check_upd = CheckUpdate(
        mo_user_id=data["mo_user_id"],
        mo_start=dt.datetime.fromisoformat(data["mo_start"]),
        mo_finish=current_time,
    )
    await check_obj.update_check(check_id=check_id, check_update=check_upd)
    await state.update_data(mo_start=None)
    fil_ = data["fil_"]
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    await message.answer(text=MoPerformerMessages.back_to_checks)
    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
    else:
        for check in checks:
            check_out = await check_obj.form_check_out(check=check)
            text_mes = check_out.form_card_check_out()
            keyboard = MoPerformerKeyboards().get_under_check(check_id=check.check_id)
            await message.answer(text=text_mes, reply_markup=keyboard)


##############
# back_logic #
##############


@router.message(F.text.lower() == "назад", StateFilter(MoPerformerStates))
async def back_command(
    message: Message,
    state: FSMContext,
    user_obj: UserService=UserService()
):
    current_state = await state.get_state()
    if current_state == MoPerformerStates.mo_performer:
        await state.clear()
        user = message.from_user
        mo = await user_obj.get_user_mo(user_id=user.id)
        fil_ = await user_obj.get_user_fil(user_id=user.id)
        await state.clear()
        await state.update_data(mo_user_id=user.id,
                                mo=mo,
                                fil_=fil_
                                )
        await message.answer(
            text=MoPerformerMessages.start_message,
            reply_markup=MoPerformerKeyboards().check_or_tasks()
        )

    elif current_state in (
        MoPerformerStates.correct_violation,
    ):
        data = await state.get_data()
        if data.get("is_take"):
            await state.clear()
            await message.answer(text=MoPerformerMessages.exit_take)
            return
        await message.answer(
            text=MoPerformerMessages.choose_vio,
            reply_markup=MoPerformerKeyboards().check_or_tasks()
        )
        await state.set_state(MoPerformerStates.mo_performer)
        violation_found_obj = ViolationFoundOut(
            **data
        )
        is_pending = violation_found_obj.is_pending
        is_task = violation_found_obj.is_task

        if is_pending:
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**v)
                    for k, v in data.items()
                    if (k.startswith("vio_") and v and (v['is_pending'] == True))
                ],
                key=lambda x: x.violation_dict_id,
            )
            order_back = get_index_by_violation_id(
                violation_found_id=data["violation_found_id"],
                objects=violation_out_objects, 
            )
            reply_obj = FormCards().form_violation_pending_reply(
                violations_out=violation_out_objects, order=order_back
            )

        elif is_task:
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**v)
                    for k, v in data.items()
                    if (k.startswith("vio_") and v and (v['is_task'] == True))
                ],
                key=lambda x: x.violation_dict_id,
            )
            order_back = get_index_by_violation_id(
                violation_found_id=data["violation_found_id"],
                objects=violation_out_objects, 
            )
            reply_obj = FormCards().form_reply(
                violations_out=violation_out_objects, order=order_back
            )

        else:
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**v)
                    for k, v in data.items()
                    if (k.startswith("vio_") and v)
                ],
                key=lambda x: x.violation_dict_id,
            )
            order_back = get_index_by_violation_id(
                violation_found_id=data["violation_found_id"],
                objects=violation_out_objects, 
            )
            reply_obj = FormCards().form_reply(
                violations_out=violation_out_objects, order=order_back
            )

        await state.update_data(
            violation_found_id=None,
            photo_id_mo=None,
            comm_mo=None,
            violation_detected=None,
            violation_dict_id=None,
            violation_name=None,
            violation_pending=None,
            zone=None,
            # check_id=None,
            comm_mfc=None,
            is_pending=None,
            is_task=None,
            photo_id_mfc=None,
            time_to_correct=None,
            )
        photo_id = reply_obj.photo_id
        text_mes = reply_obj.text_mes
        keyboard = reply_obj.keyboard
        await message.answer_photo(
            photo=photo_id, caption=text_mes, reply_markup=keyboard
        )

    else:
        await state.clear()
        await message.answer(text=MoPerformerMessages.exit_take)


@router.message()
async def something_wrong(message: Message, state: FSMContext):
    await message.answer(text=DefaultMessages.something_wrong)


@router.callback_query()
async def something_wrong(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text=DefaultMessages.not_good_time)
