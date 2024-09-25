from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.schemas.user_schema import UserUpdate
from app.database.services.users import UserService
from app.filters.mo_filters import MoControlerFilter
from app.handlers.messages import MoControlerMessages
from app.handlers.states import MoControlerStates
from app.keyboards.mo_part import MoControlerKeyboards
from app.view.users import get_user_info

router = Router()
router.message.filter(MoControlerFilter())


@router.message(Command('start'))
async def cmd_start(message: Message,
                    state: FSMContext):
    await state.clear()
    await message.answer(
        text=MoControlerMessages.start_message,
        reply_markup=MoControlerKeyboards().main_menu()
    )
    await state.set_state(MoControlerStates.mo_controler)


##############
# back_logic #
##############

@router.message(F.text.lower() == 'назад')
async def back_command(message: Message, state: FSMContext):
    await message.answer(
        text=MoControlerMessages.start_message,
        reply_markup=MoControlerKeyboards().main_menu(),
    )
    await state.set_state(MoControlerStates.mo_controler)


##############
# main_logic #
##############

@router.message(
    F.text.lower() == 'отпуск сотрудника',
    StateFilter(MoControlerStates.mo_controler)
)
async def employee_to_vacation(
    message: Message,
    state: FSMContext
):
    await message.answer(
        text=MoControlerMessages.choose_surname,
        reply_markup=MoControlerKeyboards().just_back()
    )
    await state.set_state(MoControlerStates.vacation)


@router.message(
    F.text,
    StateFilter(MoControlerStates.vacation)
)
async def get_surname(
    message: Message,
    state: FSMContext
):
    surname = message.text
    controler_user_id = message.from_user.id
    user_fil = await UserService().get_user_fil(user_id=controler_user_id)
    users = await UserService().get_mo_users_by_surname_and_fil(
        last_name=surname,
        fil=user_fil
    )
    if not users:
        await message.answer(
            text=MoControlerMessages.no_employee,
            reply_markup=MoControlerKeyboards().main_menu()
        )
        await state.set_state(MoControlerStates.mo_controler)
        return

    else:
        for user in users:
            text = await get_user_info(user=user, is_mfc=False)
            additional_text = '\nСтатус: <b>в отпуске</b>' if user.is_vacation else '\nСтатус: <b>не в отпуске</b>'
            await message.answer(
                text=text + additional_text,
                reply_markup=MoControlerKeyboards().choose_employee(user_id=user.user_id)
            )


@router.callback_query(
    F.data.startswith('choose_employee_'),
    StateFilter(MoControlerStates.vacation)
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
            text=MoControlerMessages.no_user,
            reply_markup=MoControlerKeyboards().just_back()
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
            text=MoControlerMessages.from_vacation_success,
            reply_markup=MoControlerKeyboards().main_menu()
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
            text=MoControlerMessages.to_vacation_success,
            reply_markup=MoControlerKeyboards().main_menu()
        )
    await callback.answer()
    await state.set_state(MoControlerStates.mo_controler)
