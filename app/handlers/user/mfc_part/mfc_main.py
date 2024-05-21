from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import MfcKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import MfcMessages
from app.data import ZONES, TIME_POINTS, CHOOSE
from app.handlers.states import MfcStates
from app.filters.mfc_filters import MfcFilter

router = Router() 
router.message.filter(MfcFilter())


@router.message(F.text.lower() == 'пройти авторизацию',
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.welcome_message,
        reply_markup=MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.start_checking)

@router.message(F.text.lower() == 'начать проверку',
                StateFilter(MfcStates.start_checking))
async def choose_time_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.choose_time,
        reply_markup=MfcKeyboards().choose_check_time()
    )
    await state.set_state(MfcStates.choose_time)

#######################
# main mfc part logic #
#######################

@router.message(lambda message: message.text in TIME_POINTS,
                StateFilter(MfcStates.choose_time))
async def choose_time_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.choose_zone,
        reply_markup=MfcKeyboards().choose_zone()
    )
    await state.update_data(time_check=message.text)
    await state.set_state(MfcStates.choose_zone)


@router.message(lambda message: message.text in ZONES.keys(),
                StateFilter(MfcStates.choose_zone))
async def choose_zone_handler(message: Message, state: FSMContext):
    zone = message.text
    await message.answer(
        text=MfcMessages.choose_violation(zone=zone),
        reply_markup=MfcKeyboards().choose_violation(zone=zone)
    )
    await state.update_data(zone=message.text)
    await state.set_state(MfcStates.choose_violation)


@router.message(lambda message: message.text in sum(list(ZONES.values()), []),
                StateFilter(MfcStates.choose_violation))
async def choose_violation_handler(message: Message, state: FSMContext):
    violation = message.text
    await message.answer(
        text=MfcMessages.add_photo_comm(violation=violation),
        reply_markup=MfcKeyboards().choose_photo_comm()
    )
    await state.update_data(violation=message.text)
    await state.set_state(MfcStates.choose_photo_comm)


@router.message(F.text.lower() == 'загрузить фото',
                StateFilter(MfcStates.choose_photo_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.add_photo,
        reply_markup=MfcKeyboards().just_back()
    )
    await state.set_state(MfcStates.add_photo)


@router.message(F.text.lower() == 'написать комментарий',
                StateFilter(MfcStates.choose_photo_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.add_comm,
        reply_markup=MfcKeyboards().just_back()
    )
    await state.set_state(MfcStates.add_comm)


@router.callback_query(F.data == "save_and_go",
                       StateFilter(MfcStates.continue_state))
async def continue_check(callback: CallbackQuery, state: FSMContext):
    
    await callback.message.answer(
        text=MfcMessages.continue_check,
    )
    await callback.message.answer(
        text=MfcMessages.choose_zone,
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
        text=MfcMessages.cancel_check,
    )
    await callback.message.answer(
        text=MfcMessages.choose_zone,
        reply_markup=MfcKeyboards().choose_zone()
    )
    await callback.answer()
    await state.set_state(MfcStates.choose_zone)

###############
# add_content #
###############

@router.message(F.photo,
                StateFilter(MfcStates.add_photo))
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.photo_added,
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
        text=MfcMessages.add_comm,
        reply_markup=MfcKeyboards().just_back()
    )
    await callback.answer()

@router.message(F.text,
                StateFilter(MfcStates.add_comm))
async def add_comm_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.comm_added,
        reply_markup=MfcKeyboards().comm_added()
    )
    await state.set_state(MfcStates.continue_state) 

@router.callback_query(F.data == "add_photo_",
                       StateFilter(MfcStates.continue_state))
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MfcMessages.add_photo,
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
        text=MfcMessages.photo_comm_added(violation=violation),
        reply_markup=MfcKeyboards().save_or_cancel()
    )

##############
# back_logic #
##############

@router.message(F.text.lower() == 'назад')
async def back_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MfcStates.start_checking:
        await state.set_state(default_state)
        await message.answer(
            text=MfcMessages.start_message,
            reply_markup=ReplyKeyboardRemove()
        )
    elif current_state == MfcStates.choose_time:
        await state.set_state(MfcStates.start_checking)
        await message.answer(
            text=MfcMessages.welcome_message,
            reply_markup=MfcKeyboards().main_menu()
        )
    elif current_state == MfcStates.choose_zone:
        await state.set_state(MfcStates.choose_time)
        await message.answer(
            text=MfcMessages.choose_time,
            reply_markup=MfcKeyboards().choose_check_time()
        )
    elif current_state == MfcStates.choose_violation:
        await state.set_state(MfcStates.choose_zone)
        await message.answer(
            text=MfcMessages.choose_zone,
            reply_markup=MfcKeyboards().choose_zone()
        )

    elif current_state == MfcStates.choose_photo_comm:
        await state.set_state(MfcStates.choose_violation)
        data = await state.get_data()
        zone = data['zone']
        await state.update_data(violation=None)
        await message.answer(
            text=MfcMessages.choose_violation(zone=zone),
            reply_markup=MfcKeyboards().choose_violation(zone=zone)
            )
    
    elif current_state in (
        MfcStates.add_comm,
        MfcStates.add_photo,
        MfcStates.continue_state
    ):
        await state.set_state(MfcStates.choose_photo_comm)
        data = await state.get_data()
        violation = data['violation']
        await message.answer(
            text=MfcMessages.add_photo_comm(violation=violation),
            reply_markup=MfcKeyboards().choose_photo_comm()
        )

    else:
        await state.clear()
        await message.answer(
            text=MfcMessages.start_message()
        )


################
# finish_check #
################

@router.message(F.text.lower() == 'закончить проверку',
                StateFilter(MfcStates.choose_zone))
async def finish_check(message: Message, state: FSMContext):
     await state.clear()
     await message.answer(
            text=MfcMessages.finish_check,
            reply_markup=ReplyKeyboardRemove()
        )
        