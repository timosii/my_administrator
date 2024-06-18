import os
import asyncio
import pandas as pd
import glob
from app.database.database import engine, session_maker, Base
from app.database.models.dicts import (
    Mos,
    Filials,
    Zones,
    Violations,
    ProblemBlocs
)
from sqlalchemy import select

class DictsInsert():
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

    async def insert_mos(self):
        async with session_maker() as session:
            result = await session.execute(select(Mos).limit(1))
            if not result.scalar():
                mos = []
                for _, row in self.dfs['mos_dict'].iterrows():
                    stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}
                    mos.append(Mos(**stripped_row))
                session.add_all(mos)
                await session.commit()

    async def insert_fils(self):
        async with session_maker() as session:
            result = await session.execute(select(Filials).limit(1))
            if not result.scalar():
                filials = []
                for _, row in self.dfs['fils_dict'].iterrows():
                    stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}
                    filials.append(Filials(**stripped_row))
                session.add_all(filials)
                await session.commit()

    async def insert_zones(self):
        async with session_maker() as session:
            result = await session.execute(select(Zones).limit(1))
            if not result.scalar():
                zones = []
                for _, row in self.dfs['zones_dict'].iterrows():
                    stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}
                    zones.append(Zones(**stripped_row))
                session.add_all(zones)
                await session.commit()

    async def insert_problems(self):
        async with session_maker() as session:
            result = await session.execute(select(ProblemBlocs).limit(1))
            if not result.scalar():
                problems = []
                for _, row in self.dfs['problems_dict'].iterrows():
                    stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}
                    problems.append(ProblemBlocs(**stripped_row))
                session.add_all(problems)
                await session.commit()

    async def insert_violations(self):
        self.dfs['violations_dict']['time_to_correct'] = pd.to_timedelta(self.dfs['violations_dict']['time_to_correct']).astype(str)
        async with session_maker() as session:
            result = await session.execute(select(Violations).limit(1))
            if not result.scalar():
                violations = []
                for _, row in self.dfs['violations_dict'].iterrows():
                    stripped_row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}
                    violations.append(Violations(**stripped_row))
                session.add_all(violations)
                await session.commit()


    def insert_dicts_to_db(self):
        asyncio.get_event_loop().run_until_complete(self.insert_mos())
        asyncio.get_event_loop().run_until_complete(self.insert_fils())
        asyncio.get_event_loop().run_until_complete(self.insert_zones())
        asyncio.get_event_loop().run_until_complete(self.insert_problems())
        asyncio.get_event_loop().run_until_complete(self.insert_violations())
        # asyncio.run(self.insert_mos())
        # asyncio.run(self.insert_fils())
        # asyncio.run(self.insert_zones())
        # asyncio.run(self.insert_problems())
        # asyncio.run(self.insert_violations())
        