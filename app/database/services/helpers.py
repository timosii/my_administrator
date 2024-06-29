from app.database.database import session_maker
from app.database.repositories.helpers import HelpRepo


class HelpService:
    def __init__(self, db_repository: HelpRepo = HelpRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def get_mo_by_fil(self, fil_: str) -> str:
        return await self.db_repository.get_mo_by_fil(fil_=fil_)

    async def mo_define_by_num(self, num: str) -> list[str] | None:
        mos = await self.db_repository.mo_define_by_num(num=num)
        return mos
