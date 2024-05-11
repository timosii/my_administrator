from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import MfcKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import Messages
from app.data import ZONES, TIME_POINTS, CHOOSE
from app.handlers.user.states import MfcStates

router = Router() 


@router.message(lambda message: message.text in TIME_POINTS,
                StateFilter(MfcStates.choose_time))
async def choose_time_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.choose_zone(),
        reply_markup=MfcKeyboards().choose_zone()
    )
    await state.update_data(time_check=message.text)
    await state.set_state(MfcStates.choose_zone)


@router.message(lambda message: message.text in ZONES.keys(),
                StateFilter(MfcStates.choose_zone))
async def choose_zone_handler(message: Message, state: FSMContext):
    zone = message.text
    await message.answer(
        text=Messages.choose_violation(zone=zone),
        reply_markup=MfcKeyboards().choose_violation(zone=zone)
    )
    await state.update_data(zone=message.text)
    await state.set_state(MfcStates.choose_violation)


@router.message(lambda message: message.text in sum(list(ZONES.values()), []),
                StateFilter(MfcStates.choose_violation))
async def choose_violation_handler(message: Message, state: FSMContext):
    violation = message.text
    await message.answer(
        text=Messages.add_photo_comm(violation=violation),
        reply_markup=MfcKeyboards().choose_photo_comm()
    )
    await state.update_data(violation=message.text)
    await state.set_state(MfcStates.choose_photo_comm)


@router.message(F.text.lower() == 'загрузить фото',
                StateFilter(MfcStates.choose_photo_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.add_photo(),
        reply_markup=MfcKeyboards().just_back()
    )
    await state.set_state(MfcStates.add_photo)


@router.message(F.text.lower() == 'написать комментарий',
                StateFilter(MfcStates.choose_photo_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.add_comm(),
        reply_markup=MfcKeyboards().just_back()
    )
    await state.set_state(MfcStates.add_comm)


@router.callback_query(F.data == "save_and_go",
                       StateFilter(MfcStates.continue_state))
async def continue_check(callback: CallbackQuery, state: FSMContext):
    
    await callback.message.answer(
        text=Messages.continue_check(),
    )
    await callback.message.answer(
        text=Messages.choose_zone(),
        reply_markup=MfcKeyboards().choose_zone()
    )
    # сохранить всё здесь
    await callback.answer(text='Информация о нарушении сохранена!', show_alert=True)
    await state.set_state(MfcStates.choose_zone)


@router.callback_query(F.data == "cancel",
                       StateFilter(MfcStates.continue_state))
# добавить окошко "проверка закончена"
async def cancel_check(callback: CallbackQuery,
                       state: FSMContext):
    await callback.message.answer(
        text=Messages.cancel_check(),
    )
    await callback.message.answer(
        text=Messages.choose_zone(),
        reply_markup=MfcKeyboards().choose_zone()
    )
    await callback.answer()
    await state.set_state(MfcStates.choose_zone)

