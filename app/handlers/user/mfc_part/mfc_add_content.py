from aiogram import Router, F, Bot
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


@router.message(F.photo,
                StateFilter(MfcStates.add_photo))
async def add_photo_handler(message: Message, state: FSMContext, bot: Bot):
    await message.answer(
        text=Messages.photo_added(),
        reply_markup=MfcKeyboards().photo_added()
    )
    # id_photo = message.photo[-1].file_id
    # await message.answer(
    #     text=id_photo,
    #     # reply_markup=MfcKeyboards().photo_added()
    # )
    # await message.reply_photo(
    #     photo=id_photo,
    #     # reply_markup=MfcKeyboards().photo_added()
    # )
    # await bot.send_photo(chat_id=message.from_user.id, photo=id_photo)
    await state.set_state(MfcStates.continue_state)

@router.callback_query(F.data == "add_comm_",
                       StateFilter(MfcStates.continue_state))
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=Messages.add_comm(),
        reply_markup=MfcKeyboards().just_back()
    )
    await callback.answer()

@router.message(F.text,
                StateFilter(MfcStates.add_comm))
async def add_comm_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.comm_added(),
        reply_markup=MfcKeyboards().comm_added()
    )
    await state.set_state(MfcStates.continue_state) 

@router.callback_query(F.data == "add_photo_",
                       StateFilter(MfcStates.continue_state))
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=Messages.add_photo(),
        reply_markup=MfcKeyboards().just_back()
    )
    await callback.answer()

@router.message(F.photo | F.text,
                StateFilter(MfcStates.continue_state))
async def add_photo_after_comm_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    zone = data['zone']
    violation = data['violation']
    await message.answer(
        text=Messages.photo_comm_added(zone=zone, violation=violation),
        reply_markup=MfcKeyboards().save_or_cancel()
    )
