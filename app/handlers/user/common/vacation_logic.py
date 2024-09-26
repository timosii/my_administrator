from aiogram import F, Router
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.schemas.user_schema import UserUpdate
from app.database.services.users import UserService
from app.filters.default import not_constants
from app.filters.mfc_filters import MfcLeaderFilter
from app.filters.mo_filters import MoControlerFilter
from app.handlers.messages import ToVacationMessages
from app.handlers.states import MfcLeaderStates, MoControlerStates, ToVacation
from app.keyboards.default import ToVacationKeyboards
from app.keyboards.mfc_part import MfcLeaderKeyboards
from app.keyboards.mo_part import MoControlerKeyboards
from app.view.users import get_user_info

router = Router()
router.message.filter(
    or_f(
        MoControlerFilter(),
        MfcLeaderFilter(),
    )
)


@router.message(
    F.text.lower() == 'отпуск сотрудника',
    StateFilter(
        MoControlerStates.mo_controler,
        MfcLeaderStates.mfc_leader,
    )
)
async def employee_to_vacation(
    message: Message,
    state: FSMContext
):
    current_state = await state.get_state()
    await state.update_data(
        current_state=current_state
    )
    await message.answer(
        text=ToVacationMessages.choose_surname,
        reply_markup=ToVacationKeyboards().just_back()
    )
    await state.set_state(ToVacation.vacation)


##############
# back_logic #
##############

@router.message(
    F.text.lower() == 'назад',
    StateFilter(ToVacation.vacation)
)
async def back_command(
    message: Message, state: FSMContext
):
    data = await state.get_data()
    current_state = data.get('current_state')
    keyboard = MfcLeaderKeyboards().main_menu() if current_state == MfcLeaderStates.mfc_leader else MoControlerKeyboards().main_menu()
    await message.answer(
        text=ToVacationMessages.back_to_menu,
        reply_markup=keyboard
    )
    await state.set_state(current_state)


@router.message(
    F.text,
    not_constants,
    StateFilter(ToVacation.vacation)
)
async def get_surname(
    message: Message,
    state: FSMContext
):
    surname = message.text
    data = await state.get_data()
    current_state = data.get('current_state')
    keyboard = MfcLeaderKeyboards().main_menu() if current_state == MfcLeaderStates.mfc_leader else MoControlerKeyboards().main_menu()
    final_state = current_state

    if current_state == MfcLeaderStates.mfc_leader:
        users = await UserService().get_mfc_users_by_surname(last_name=surname)
    else:
        controler_user_id = message.from_user.id
        user_fil = await UserService().get_user_fil(user_id=controler_user_id)
        users = await UserService().get_mo_users_by_surname_and_fil(
            last_name=surname,
            fil=user_fil
        )

    if not users:
        await message.answer(
            text=ToVacationMessages.no_employee,
            reply_markup=keyboard
        )
        await state.set_state(final_state)
        return
    else:
        for user in users:
            text = await get_user_info(user=user, is_mfc=True if current_state == MfcLeaderStates.mfc_leader else False)
            additional_text = '\nСтатус: <b>в отпуске</b>' if user.is_vacation else '\nСтатус: <b>не в отпуске</b>'
            await message.answer(
                text=text + additional_text,
                reply_markup=ToVacationKeyboards().choose_employee(user_id=user.user_id)
            )


@router.callback_query(
    F.data.startswith('choose_employee_'),
)
async def user_to_vacation(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()
    current_state = data.get('current_state')
    keyboard = MfcLeaderKeyboards().main_menu() if current_state == MfcLeaderStates.mfc_leader else MoControlerKeyboards().main_menu()
    final_state = current_state
    user_id = int(callback.data.split('_')[-1])
    await state.update_data(
        user_vacation=user_id
    )
    user = await UserService().get_user_by_id(user_id=user_id)
    if not user:
        await callback.message.answer(
            text=ToVacationMessages.no_user,
            reply_markup=ToVacationKeyboards().just_back()
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
            text=ToVacationMessages.from_vacation_success,
            reply_markup=keyboard
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
            text=ToVacationMessages.to_vacation_success,
            reply_markup=keyboard
        )
    await callback.answer()
    await state.set_state(final_state)
