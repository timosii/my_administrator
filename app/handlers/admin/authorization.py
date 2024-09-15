# import xlsxwriter

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.database.schemas.user_schema import UserBaseInfo, UserCreate
from app.database.services.helpers import HelpService
from app.database.services.users import UserService
from app.filters.default import is_digit, not_constants
from app.filters.form_menu import IsInFilials, IsInMos
from app.handlers.messages import AuthorizationMessages, DefaultMessages
from app.handlers.states import RegStates
from app.keyboards.admin import SelfRegistration
from app.keyboards.default import DefaultKeyboards
from app.utils.utils import check_password, is_mfc_role
from app.view.users import get_user_info

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message,
                    state: FSMContext,
                    user: UserService = UserService()
                    ):
    await state.clear()
    user_id = message.from_user.id
    user_obj = await user.get_user_by_id(user_id=user_id)
    if not user_obj:
        await message.answer(
            text=AuthorizationMessages.start_message,
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(RegStates.reg)
    else:
        await message.answer(
            text=AuthorizationMessages.archieved_mes,
            reply_markup=SelfRegistration().get_active()
        )
        await state.set_state(RegStates.get_active)


@router.message(F.text,
                StateFilter(RegStates.reg,
                            RegStates.get_active))
async def pass_in(message: Message,
                  state: FSMContext):
    text = message.text
    check_pass = await check_password(s=text)
    user_id = message.from_user.id
    if not check_pass:
        await message.answer(text=AuthorizationMessages.incorrect_pass)
        await state.set_state(None)
        return
    else:
        role = check_pass.get('role')
        category = check_pass.get('name')

        await state.update_data({
            'user_id': user_id,
            'category': category,
            role: True,
            'role': role
        })

        await message.answer(
            text=AuthorizationMessages.are_you_sure.format(category=category),
            reply_markup=SelfRegistration().are_you_sure()
        )
        await state.set_state(RegStates.start_registration)


@router.message(
    F.text.lower().in_(('отменить', 'начать сначала')),
    StateFilter(
        RegStates.start_registration,
        RegStates.surname_take,
        RegStates.name_take,
        RegStates.patronymic_take,
        RegStates.post_take,
        RegStates.department_take,
        RegStates.get_mo,
        RegStates.choose_mo_additional,
        RegStates.get_fil,
        RegStates.is_avail_status,
        RegStates.confirmation_reg,
    )
)
async def cancel_process(
        message: Message,
        state: FSMContext):
    current_state = await state.get_state()
    if current_state in (
        RegStates.start_registration,
        RegStates.surname_take
    ):
        await message.answer(
            text=AuthorizationMessages.press_start,
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    else:  # current_state != RegStates.start_registration:
        await message.answer(
            text=AuthorizationMessages.anketa,
            reply_markup=SelfRegistration().just_cancel()
        )
        await message.answer(
            text=AuthorizationMessages.get_surname,
            reply_markup=SelfRegistration().just_cancel()
        )
        await state.update_data(
            last_name=None,
            first_name=None,
            patronymic=None,
            post=None,
            department=None,
            mo_=None,
            fil_=None,
        )
        await state.set_state(RegStates.surname_take)


@router.message(
    F.text.lower() == 'да',
    StateFilter(RegStates.start_registration)
)
async def start_reg(
        message: Message,
        state: FSMContext):
    await message.answer(
        text=AuthorizationMessages.anketa,
        reply_markup=SelfRegistration().just_cancel()
    )
    await message.answer(
        text=AuthorizationMessages.get_surname,
        reply_markup=SelfRegistration().just_cancel()
    )
    await state.set_state(RegStates.surname_take)


@router.message(
    F.text,
    not_constants,
    StateFilter(RegStates.surname_take)
)
async def get_name(
        message: Message,
        state: FSMContext):
    last_name = message.text
    await state.update_data(
        last_name=last_name
    )
    await message.answer(
        text=AuthorizationMessages.get_name,
        reply_markup=SelfRegistration().from_start()
    )
    await state.set_state(RegStates.name_take)


@router.message(
    F.text,
    not_constants,
    StateFilter(RegStates.name_take)
)
async def get_surname(
        message: Message,
        state: FSMContext):
    first_name = message.text
    await state.update_data(
        first_name=first_name
    )
    await message.answer(
        text=AuthorizationMessages.get_patronymic,
        reply_markup=SelfRegistration().cancel_miss()
    )
    await state.set_state(RegStates.patronymic_take)


@router.message(
    F.text,
    StateFilter(RegStates.patronymic_take)
)
async def get_patron(
        message: Message,
        state: FSMContext):
    mes = message.text
    if mes.lower() != 'пропустить':
        await state.update_data(
            patronymic=mes
        )
    await message.answer(
        text=AuthorizationMessages.get_post,
        reply_markup=SelfRegistration().cancel_miss()
    )
    await state.set_state(RegStates.post_take)


@router.message(
    F.text,
    StateFilter(RegStates.post_take)
)
async def get_post(
        message: Message,
        state: FSMContext):
    mes = message.text
    if mes.lower() != 'пропустить':
        await state.update_data(
            post=mes
        )
    data = await state.get_data()
    current_role = data.get('role')
    is_mfc_role_ = await is_mfc_role(current_role)
    if is_mfc_role_:
        await message.answer(
            text=AuthorizationMessages.get_department,
            reply_markup=SelfRegistration().cancel_miss()
        )
        await state.set_state(RegStates.department_take)

    else:
        await message.answer(
            text=AuthorizationMessages.get_mo,
            reply_markup=SelfRegistration().from_start()
        )
        await state.set_state(RegStates.get_mo)


@router.message(
    F.text,
    StateFilter(RegStates.department_take)
)
async def get_department(
        message: Message,
        state: FSMContext):
    mes = message.text
    if mes.lower() != 'пропустить':
        await state.update_data(
            department=mes
        )

    await message.answer(
        text=AuthorizationMessages.control_data,
        reply_markup=SelfRegistration().save_cancel()
    )
    await state.update_data(
        is_avail=True
    )
    data = await state.get_data()
    user = UserBaseInfo(**data)
    data = await state.get_data()
    current_role = data.get('role')
    is_mfc_role_ = await is_mfc_role(current_role)

    await message.answer(
        text=await get_user_info(user=user, is_mfc=is_mfc_role_),
    )

    await state.set_state(
        RegStates.confirmation_reg
    )


# Логика МО
@router.message(
    F.text,
    is_digit,
    StateFilter(RegStates.get_mo)
)
async def get_mo(
    message: Message,
    state: FSMContext,
    helper: HelpService = HelpService()
):
    num = message.text
    mos = await helper.mo_define_by_num(num=num)
    if not mos:
        await message.answer(
            text=DefaultMessages.does_not_find
        )
        return
    elif len(mos) > 1:
        await message.answer(
            text=DefaultMessages.choose_mo_additional,
            reply_markup=DefaultKeyboards().choose_mo(mos=mos),
        )
        await state.set_state(RegStates.choose_mo_additional)
    else:
        mo = mos[0]
        await message.answer(
            text=DefaultMessages.choose_fil(mo=mo),
            reply_markup=await DefaultKeyboards().choose_fil(mo=mo),
        )
        await state.update_data(mo_=mo)
        await state.set_state(RegStates.get_fil)


@router.message(
    IsInMos(),
    StateFilter(RegStates.choose_mo_additional)
)
async def choose_mo_additional(message: Message, state: FSMContext):
    mo = message.text
    await message.answer(
        text=DefaultMessages.choose_fil(mo=mo),
        reply_markup=await DefaultKeyboards().choose_fil(mo=mo),
    )
    await state.update_data(mo_=mo)
    await state.set_state(RegStates.get_fil)


@router.message(
    ~IsInMos(),
    F.text,
    not_constants,
    StateFilter(RegStates.choose_mo_additional)
)
async def wrong_choose_mos_additional(message: Message):
    await message.answer(
        text=DefaultMessages.choose_mo_additional,
        reply_markup=message.reply_markup
    )


@router.message(
    F.text.lower() == 'назад',
    StateFilter(
        RegStates.choose_mo_additional,
        RegStates.get_fil)
)
async def back_choose_mos_additional(
    message: Message,
    state: FSMContext
):
    await message.answer(
        text=AuthorizationMessages.get_mo,
        reply_markup=SelfRegistration().from_start()
    )
    await state.set_state(RegStates.get_mo)


@router.message(
    ~F.text,
    StateFilter(RegStates.choose_mo_additional),
    StateFilter(RegStates.get_mo),
    StateFilter(RegStates.get_fil)
)
async def wrong_type(message: Message):
    await message.answer(
        text=DefaultMessages.something_wrong
    )


@router.message(
    IsInFilials(),
    StateFilter(RegStates.get_fil)
)
async def get_fil(
    message: Message,
    state: FSMContext
):
    fil = message.text
    await state.update_data(
        fil_=fil
    )
    await message.answer(
        text=AuthorizationMessages.is_avail,
        reply_markup=SelfRegistration().yes_no()
    )
    await state.set_state(RegStates.is_avail_status)


@router.message(
    F.text.lower().in_(('да', 'нет')),
    StateFilter(RegStates.is_avail_status)
)
async def get_avail_status(
    message: Message,
    state: FSMContext
):
    mes = message.text.lower()
    if mes == 'да':
        await state.update_data(
            is_avail=True
        )
    else:
        await state.update_data(
            is_avail=False
        )
    await message.answer(
        text=AuthorizationMessages.control_data,
        reply_markup=SelfRegistration().save_cancel()
    )
    data = await state.get_data()
    user = UserBaseInfo(**data)
    is_mfc = data.get('is_mfc')
    await message.answer(
        text=await get_user_info(user=user,
                                 is_mfc=is_mfc),
    )

    await state.set_state(
        RegStates.confirmation_reg
    )


@router.message(
    F.text.lower() == 'сохранить',
    StateFilter(RegStates.confirmation_reg)
)
async def confirmation_reg(
    message: Message,
    state: FSMContext,
    user: UserService = UserService()
):
    data = await state.get_data()
    user_id = data['user_id']
    category = data['category']

    user_create = UserCreate(
        **data
    )

    await user.add_user(user_create=user_create)
    await message.answer(
        text=await AuthorizationMessages.welcome_message(user_id=user_id, category=category),
        reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()


@router.message()
async def something_wrong(message: Message):
    await message.answer(text=DefaultMessages.something_wrong)
