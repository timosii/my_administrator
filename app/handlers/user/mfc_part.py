from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from app.keyboards.mfc_part import choose_check_time

router = Router() 

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Выберите время проверки",
        reply_markup=choose_check_time()
    )
