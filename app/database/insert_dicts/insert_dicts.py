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
                file
                ) for file in excel_files
            }        

    async def insert_mos(self):
        async with session_maker() as session:
            mos = [Mos(**row) for _, row in self.dfs['mos_dict'].iterrows()]
            session.add_all(mos)
            await session.commit()

    async def insert_fils(self):
        async with session_maker() as session:
            fils = [Filials(**row) for _, row in self.dfs['fils_dict'].iterrows()]
            session.add_all(fils)
            await session.commit()  

    async def insert_zones(self):
        async with session_maker() as session:
            zones = [Zones(**row) for _, row in self.dfs['zones_dict'].iterrows()]
            session.add_all(zones)
            await session.commit()

    async def insert_problems(self):
        async with session_maker() as session:
            problems = [ProblemBlocs(**row) for _, row in self.dfs['problems_dict'].iterrows()]
            session.add_all(problems)
            await session.commit()

    async def insert_violations(self):
        async with session_maker() as session:
            violations = [Violations(**row) for _, row in self.dfs['violations_dict'].iterrows()]
            session.add_all(violations)
            await session.commit()


    def insert_dicts_to_db(self):
        asyncio.run(self.insert_mos())
        asyncio.run(self.insert_fils())
        asyncio.run(self.insert_zones())
        asyncio.run(self.insert_problems())
        asyncio.run(self.insert_violations())
        
        

    # async def insert_data():
    # async with session_maker() as session:
    #     user_test = User(user_id='661772')
    #     user_test_2 =  User(user_id='2121212')
    #     session.add_all([user_test, user_test_2])
    #     await session.commit()

        


