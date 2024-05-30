"""empty message

Revision ID: dac5d0f1594d
Revises: b51162f91c52
Create Date: 2024-05-30 22:48:43.027828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os
import glob
import pandas as pd
from typing import Sequence, Union
from sqlalchemy.orm import sessionmaker
from alembic import op
import sqlalchemy as sa
from app.database.models.dicts import Mos, Filials, Zones, Violations, ProblemBlocs


class DictsInsert:
    def __init__(self, path: str = "app/database/insert_dicts/data/") -> None:
        if not os.path.exists(path):
            raise FileNotFoundError("Папки со словарями не существует")
        self.path = path
        self.get_dfs()

    def get_dfs(self):
        excel_files = glob.glob(os.path.join(self.path, "*.xlsx"))
        self.dfs = {
            os.path.basename(file).split(".")[0]: pd.read_excel(file)
            for file in excel_files
        }

    def insert_mos(self, session):
        mos = [Mos(**row) for _, row in self.dfs["mos_dict"].iterrows()]
        session.add_all(mos)
        session.commit()

    def insert_fils(self, session):
        fils = [Filials(**row) for _, row in self.dfs["fils_dict"].iterrows()]
        session.add_all(fils)
        session.commit()

    def insert_zones(self, session):
        zones = [Zones(**row) for _, row in self.dfs["zones_dict"].iterrows()]
        session.add_all(zones)
        session.commit()

    def insert_problems(self, session):
        problems = [
            ProblemBlocs(**row) for _, row in self.dfs["problems_dict"].iterrows()
        ]
        session.add_all(problems)
        session.commit()

    def insert_violations(self, session):
        self.dfs["violations_dict"]["time_to_correct"] = pd.to_timedelta(
            self.dfs["violations_dict"]["time_to_correct"]
        ).astype(str)
        violations = [
            Violations(**row) for _, row in self.dfs["violations_dict"].iterrows()
        ]
        session.add_all(violations)
        session.commit()

    def insert_dicts_to_db(self, session):
        self.insert_mos(session)
        self.insert_fils(session)
        self.insert_zones(session)
        self.insert_problems(session)
        self.insert_violations(session)

# revision identifiers, used by Alembic.
revision: str = 'dac5d0f1594d'
down_revision: Union[str, None] = 'b51162f91c52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Session = sessionmaker(bind=bind)
    session = Session()

    # Instantiate your class and call the insert method
    inserter = DictsInsert()
    inserter.insert_dicts_to_db(session)


def downgrade() -> None:
    op.drop_table('violation_found', schema='data')
    op.drop_table('check', schema='data')
    op.drop_table('violations', schema='dicts')
    op.drop_table('filials', schema='dicts')
    op.drop_table('user', schema='data')
    op.drop_table('zones', schema='dicts')
    op.drop_table('problems', schema='dicts')
    op.drop_table('mos', schema='dicts')