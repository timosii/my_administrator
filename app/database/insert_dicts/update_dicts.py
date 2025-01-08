import asyncio
import glob
import os

import pandas as pd
from loguru import logger
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database.database import session_maker
from app.database.models.dicts import Filials, Mos, Violations, Zones


class DictsUpdate():
    def __init__(self,
                 path: str = 'app/database/insert_dicts/data/') -> None:
        if not os.path.exists(path):
            raise FileNotFoundError('Папки со словарями не существует')
        self.path = path
        self.get_dfs()

    def get_dfs(self):
        excel_files = glob.glob(
            os.path.join(
                self.path,
                '*.xlsx'
            )
        )
        self.dfs = {
            os.path.basename(file).split('.')[0]: pd.read_excel(
                file, engine='openpyxl'
            ) for file in excel_files
        }

    async def update_mos(self):
        async with session_maker() as session:
            for _, row in self.dfs['mos_dict'].iterrows():
                stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

                stmt = pg_insert(Mos).values(**stripped_row).on_conflict_do_update(
                    index_elements=['mo_'],
                    set_=stripped_row
                )
                await session.execute(stmt)
            await session.commit()
        logger.info('MOS_UPDATED')

    async def update_fils(self):
        async with session_maker() as session:
            for _, row in self.dfs['fils_dict'].iterrows():
                stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

                stmt = pg_insert(Filials).values(**stripped_row).on_conflict_do_update(
                    index_elements=['fil_'],
                    set_=stripped_row
                )
                await session.execute(stmt)
            await session.commit()
        logger.info('FILIALS_UPDATED')

    async def update_zones(self):
        async with session_maker() as session:
            for _, row in self.dfs['zones_dict'].iterrows():
                stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

                stmt = pg_insert(Zones).values(**stripped_row).on_conflict_do_update(
                    index_elements=['zone_name'],
                    set_=stripped_row
                )
                await session.execute(stmt)
            await session.commit()
        logger.info('ZONES_UPDATED')

    # async def update_problems(self):
    #     async with session_maker() as session:
    #         for _, row in self.dfs['problems_dict'].iterrows():
    #             stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

    #             stmt = pg_insert(ProblemBlocs).values(**stripped_row).on_conflict_do_update(
    #                 index_elements=['problem_name'],
    #                 set_=stripped_row
    #             )

    #             await session.execute(stmt)
    #         await session.commit()
    #     logger.info('PROBLEMS_UPDATED')

    # async def update_violations(self):
    #     self.dfs['violations_dict']['time_to_correct'] = pd.to_timedelta(
    #         self.dfs['violations_dict']['time_to_correct']).astype(str)
    #     self.dfs['violations_dict']['violation_dict_id'] = self.dfs['violations_dict']['violation_dict_id'].astype(int)
    #     async with session_maker() as session:
    #         for _, row in self.dfs['violations_dict'].iterrows():
    #             stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

    #             stmt = pg_insert(Violations).values(**stripped_row).on_conflict_do_update(
    #                 index_elements=['violation_dict_id'],
    #                 set_=stripped_row
    #             )
    #             await session.execute(stmt)

    #         await session.commit()
    #     logger.info('VIOLATIONS_UPDATED')

    async def update_violations_new(self):
        self.dfs['violations_dict_new']['time_to_correct'] = pd.to_timedelta(
            self.dfs['violations_dict_new']['time_to_correct']).astype(str)
        self.dfs['violations_dict_new']['violation_dict_id'] = self.dfs['violations_dict_new']['violation_dict_id'].astype(
            int)
        async with session_maker() as session:
            for _, row in self.dfs['violations_dict'].iterrows():
                stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}

                stmt = pg_insert(Violations).values(**stripped_row).on_conflict_do_update(
                    index_elements=['violation_dict_id'],
                    set_=stripped_row
                )
                await session.execute(stmt)

            await session.commit()
        logger.info('VIOLATIONS_NEW_UPDATED')

    def update_dicts_to_db(self):
        asyncio.get_event_loop().run_until_complete(self.update_mos())
        asyncio.get_event_loop().run_until_complete(self.update_fils())
        asyncio.get_event_loop().run_until_complete(self.update_zones())
        # asyncio.get_event_loop().run_until_complete(self.update_problems())
        asyncio.get_event_loop().run_until_complete(self.update_violations_new())


if __name__ == '__main__':
    DictsUpdate().update_dicts_to_db()
