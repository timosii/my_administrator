from aiogram.types import Message
from app.database.db_helpers.form_menu import get_all_zones, get_all_violations, get_all_filials


async def is_in_zones(message: Message) -> bool:
    zones = await get_all_zones()
    return message.text in zones

async def is_in_violations(message: Message) -> bool:
    violations = await get_all_violations()
    return message.text in violations

async def is_in_filials(message: Message) -> bool:
    filials = await get_all_filials()
    return message.text in filials
