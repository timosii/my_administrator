import os
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
        
    async def insert_to_db(self):
        self.get_dfs()
        async with session_maker() as session:
            # for obj in (
            #         Mos,
            #         Filials,
            #         Zones,
            #         Violations,
            #         ProblemBlocs
            #     ):
                
                # objects = [obj(**row) for _, row in df.iterrows()]
            mos = [Mos(**row) for _, row in self.dfs['mos_dict'].drop_duplicates(subset='mo_name').iterrows()]
            fils = [Filials(**row) for _, row in self.dfs['fils_dict'].iterrows()]
            # zones = [Mos(**row) for _, row in self.dfs['mos_dict'].drop_duplicates(subset='mo_name').iterrows()]
            # violations = [Mos(**row) for _, row in self.dfs['mos_dict'].drop_duplicates(subset='mo_name').iterrows()]
            # ProblemBlocs = [Mos(**row) for _, row in self.dfs['mos_dict'].drop_duplicates(subset='mo_name').iterrows()]
            session.add_all(mos)
            session.add_all(fils)
            await session.commit()

        

    # async def insert_data():
    # async with session_maker() as session:
    #     user_test = User(user_id='661772')
    #     user_test_2 =  User(user_id='2121212')
    #     session.add_all([user_test, user_test_2])
    #     await session.commit()

        


