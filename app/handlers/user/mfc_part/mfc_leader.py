from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.filters.mfc_filters import MfcLeaderFilter
from app.handlers.messages import MfcLeaderMessages
from app.handlers.states import MfcLeaderStates
from app.keyboards.mfc_part import MfcLeaderKeyboards

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
