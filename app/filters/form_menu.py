from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.database.db_helpers.form_menu import get_all_zones, get_all_violations, get_all_filials
from loguru import logger
from app.view.menu_beautify import ICONS_MAPPING


class IsInFilials(BaseFilter): 
    def __init__(self): 
        pass

    async def __call__(self, message: Message) -> bool:
        filials = [filial.strip() for filial in await get_all_filials()]
        return message.text in filials


class IsInViolations(BaseFilter): 
    def __init__(self): 
        pass

    async def __call__(self, message: Message) -> bool: 
        violations = [violation.strip() for violation in await get_all_violations()]
        violations_marked = [f'✅ {violation}' for violation in violations]
        return (message.text in violations) or (message.text in violations_marked)


class IsInZones(BaseFilter): 
    def __init__(self): 
        pass

    async def __call__(self, message: Message) -> bool: 
        zones = [zone.strip() for zone in await get_all_zones()]
        zones_iconned = [f'{ICONS_MAPPING[zone]} {zone}' for zone in zones]
        return message.text in zones_iconned

