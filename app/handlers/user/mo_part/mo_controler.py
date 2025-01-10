from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.filters.mo_filters import MoControlerFilter
from app.handlers.messages import MoControlerMessages
from app.handlers.states import MoControlerStates
from app.keyboards.mo_part import MoControlerKeyboards

router = Router()
router.message.filter(MoControlerFilter())


@router.message(
        or_f(
            Command('start'),
            Command('menu')
        ))
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
