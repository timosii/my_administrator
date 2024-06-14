from aiogram.types import Message
from app.database.db_helpers.form_menu import get_all_zones, get_all_violations, get_all_filials
from loguru import logger
from app.misc.menu_beautify import ICONS_MAPPING


async def is_in_zones(message: Message) -> bool:
    zones = await get_all_zones()
    zones_iconned = [f'{ICONS_MAPPING[zone]} {zone}' for zone in zones]
    logger.info(zones_iconned)
    return message.text in zones_iconned

async def is_in_violations(message: Message) -> bool:
    violations = await get_all_violations()
    violations_marked = [f'✅ {violation}' for violation in violations]
    return (message.text in violations) or (message.text in violations_marked)

async def is_in_filials(message: Message) -> bool:
    filials = await get_all_filials()
    return message.text in filials
