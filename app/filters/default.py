from aiogram.types import Message

async def not_back_filter(message: Message) -> bool:
    return message.text.lower() != 'назад'

async def not_cancel_filter(message: Message) -> bool:
    return message.text.lower() != 'отменить'
