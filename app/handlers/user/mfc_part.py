from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import MfcKeyboards
from app.handlers.messages import Messages
from app.data import ZONES, TIME_POINTS, CHOOSE
from app.handlers.user.states import MfcStates

router = Router() 

@router.message(Command("start"), StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.main_menu(),
        reply_markup=MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.choose_time)

@router.message(F.text.lower() == 'начать проверку', StateFilter(MfcStates.choose_time))
async def cmd_main_menu(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.choose_time(),
        reply_markup=MfcKeyboards().choose_check_time()
    )
    await state.set_state(MfcStates.choose_zone)

@router.message(F.text.lower() == 'назад')
async def back_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MfcStates.choose_time:
        await state.set_state(default_state)
        await message.answer(
            text=Messages.main_menu(),
        )
    elif current_state == MfcStates.choose_zone:
        await state.set_state(MfcStates.choose_time)
        await message.answer(
            text=Messages.choose_time(),
            reply_markup=MfcKeyboards().choose_check_time()
        )
    elif current_state == MfcStates.choose_violation:
        await state.set_state(MfcStates.choose_zone)
        await message.answer(
            text=Messages.choose_zone(),
            reply_markup=MfcKeyboards().choose_zone()
        )
    elif current_state == MfcStates.choose_photo_comm:
        await state.set_state(MfcStates.choose_violation)
        data = await state.get_data()
        zone = data['zone']
        await message.answer(
            text=Messages.choose_violation(zone=zone),
            reply_markup=MfcKeyboards().choose_violation(zone=zone)
        )
    elif current_state in (
        MfcStates.add_comm,
        MfcStates.add_photo
    ):
        await state.set_state(MfcStates.choose_photo_comm)
        data = await state.get_data()
        violation = data['violation']
        await message.answer(
            text=Messages.add_photo_comm(violation=violation),
            reply_markup=MfcKeyboards().choose_photo_comm()
        )
    else:
        await state.clear()
        await message.answer(
            text=Messages.start_message()
        )


@router.message(lambda message: message.text in TIME_POINTS, StateFilter(MfcStates.choose_zone))
async def choose_zone_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.choose_zone(),
        reply_markup=MfcKeyboards().choose_zone()
    )
    await state.update_data(time_check=message.text)
    await state.set_state(MfcStates.choose_violation)


@router.message(lambda message: message.text in ZONES.keys(), StateFilter(MfcStates.choose_violation))
async def choose_violation_handler(message: Message, state: FSMContext):
    zone = message.text
    await message.answer(
        text=Messages.choose_violation(zone=zone),
        reply_markup=MfcKeyboards().choose_violation(zone=zone)
    )
    await state.update_data(zone=message.text)
    await state.set_state(MfcStates.choose_photo_comm)


@router.message(lambda message: message.text in sum(list(ZONES.values()), []), StateFilter(MfcStates.choose_photo_comm))
async def make_choice_handler(message: Message, state: FSMContext):
    violation = message.text
    await message.answer(
        text=Messages.add_photo_comm(violation=violation),
        reply_markup=MfcKeyboards().choose_photo_comm()
    )
    await state.update_data(violation=message.text)
    # await state.set_state(MfcStates.add_comm)



@router.message(F.text.lower() == 'загрузить фото', StateFilter(MfcStates.choose_photo_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.add_photo(),
        reply_markup=MfcKeyboards().add_photo_comm_kb()
    )
    await state.set_state(MfcStates.add_photo)


@router.message(F.text.lower() == 'написать комментарий', StateFilter(MfcStates.choose_photo_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.add_comm(),
        reply_markup=MfcKeyboards().add_photo_comm_kb()
    )
    await state.set_state(MfcStates.add_comm)


@router.message(F.photo, StateFilter(MfcStates.add_photo))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.photo_added(),
        reply_markup=MfcKeyboards().add_photo_comm_kb()
    )
    await state.set_state(MfcStates.add_comm)

@router.message(F.text, StateFilter(MfcStates.add_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.comm_added(),
        reply_markup=MfcKeyboards().add_photo_comm_kb()
    )
    await state.set_state(MfcStates.add_comm)


# @router.message(lambda message: message.text in CHOOSE, StateFilter(MfcStates.choose_photo_comm))
# async def result_choose_handler(message: Message, state: FSMContext):
#     mes = Messages()
#     choice = message.text
#     data = await state.get_data()
#     zone = data['zone']
#     await message.answer(
#         text=mes.photo_comm_added(),
#         reply_markup=back_level(zone=zone)
#     )



# @router.message(F.text, StateFilter(MfcStates.add_comm))
# async def add_comm_handler(message: Message, state: FSMContext):
#     mes = Messages()
#     await message.answer(
#         text=mes.add_comm(),
#         reply_markup=add_photo_comm_kb()
#     )
