from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import choose_check_time, choose_zone, choose_violation, choose_photo_comm, back_level
from app.handlers.messages import Messages
from app.data import ZONES, TIME_POINTS, CHOOSE
from app.handlers.user.states import MfcStates

router = Router() 

@router.message(Command("start"), StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    mes = Messages()
    await message.answer(
        text=mes.get_welcome_message(),
        reply_markup=choose_check_time()
    )
    await state.set_state(MfcStates.choose_zone)


@router.message(F.text in TIME_POINTS, StateFilter(MfcStates.choose_zone))
async def choose_zone(message: Message, state: FSMContext):
    mes = Messages()
    await message.answer(
        text=mes.choose_zone(),
        reply_markup=choose_zone()
    )
    await state.update_data(time_check=message.text)
    await state.set_state(MfcStates.choose_violation)


@router.message(F.text in ZONES.keys(), StateFilter(MfcStates.choose_violation))
async def choose_violation(message: Message, state: FSMContext):
    mes = Messages()
    mes.zone = message.text
    await message.answer(
        text=mes.choose_violation(),
        reply_markup=choose_violation()
    )
    await state.update_data(zone=message.text)
    await state.set_state(MfcStates.choose_photo_comm)


@router.message(F.text in ZONES.values(), StateFilter(MfcStates.choose_photo_comm))
async def make_choice(message: Message, state: FSMContext):
    mes = Messages()
    mes.violation = message.text
    await message.answer(
        text=mes.add_photo_comm(),
        reply_markup=choose_photo_comm()
    )
    await state.update_data(violation=message.text)
    # await state.set_state(MfcStates.add_comm)


@router.message(F.text in CHOOSE, StateFilter(MfcStates.choose_photo_comm))
async def result_choose(message: Message, state: FSMContext):
    mes = Messages()
    choice = message.text
    await message.answer(
        text=mes.photo_comm_added(),
        reply_markup=back_level()
    )
    await state.update_data(choice=message.text)
    if choice == 'Загрузить фото':
        await state.set_state(MfcStates.add_photo)
    else:
        await state.set_state(MfcStates.add_comm)
