from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.database.db_helpers.form_menu import (
    get_all_filials,
    get_all_mos,
    get_all_problems,
    get_all_violations,
    get_all_zones,
)
from app.view.menu_beautify import ICONS_MAPPING


class IsInMos(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        mos = [mo.strip() for mo in await get_all_mos()]
        return message.text in mos


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


class IsInProblems(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        problems = [violation.strip() for violation in await get_all_problems()]
        problems_marked = [f'✅ {problem}' for problem in problems]
        return (message.text in problems) or (message.text in problems_marked)


class IsInZones(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        zones = [zone.strip() for zone in await get_all_zones()]
        zones_iconned = [f'{ICONS_MAPPING[zone]} {zone}' for zone in zones]
        return message.text in zones_iconned
