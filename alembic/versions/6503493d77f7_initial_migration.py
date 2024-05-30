"""initial migration

Revision ID: 6503493d77f7
Revises: 493738470241
Create Date: 2024-05-30 10:55:32.808940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6503493d77f7'
down_revision: Union[str, None] = '493738470241'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mos',
    sa.Column('mo_', sa.String(length=255), nullable=False),
    sa.Column('mo_population', sa.String(length=255), nullable=False),
    sa.Column('mo_type', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('mo_'),
    schema='dicts'
    )
    op.create_table('problems',
    sa.Column('problem_name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('problem_name'),
    schema='dicts'
    )
    op.create_table('zones',
    sa.Column('zone_name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('zone_name'),
    schema='dicts'
    )
    op.create_table('user',
    sa.Column('id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('mo_', sa.String(length=255), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('patronymic', sa.String(length=255), nullable=False),
    sa.Column('post', sa.String(length=255), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_mfc', sa.Boolean(), nullable=False),
    sa.Column('is_mfc_leader', sa.Boolean(), nullable=False),
    sa.Column('is_mo_performer', sa.Boolean(), nullable=False),
    sa.Column('is_mo_controler', sa.Boolean(), nullable=False),
    sa.Column('is_archived', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['mo_'], ['dicts.mos.mo_'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='data'
    )
    op.create_table('filials',
    sa.Column('fil_', sa.String(length=255), nullable=False),
    sa.Column('fil_population', sa.String(length=255), nullable=False),
    sa.Column('fil_type', sa.String(length=255), nullable=False),
    sa.Column('mo_', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['mo_'], ['dicts.mos.mo_'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('fil_'),
    schema='dicts'
    )
    op.create_table('violations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('violation_name', sa.String(length=255), nullable=False),
    sa.Column('zone', sa.String(length=255), nullable=False),
    sa.Column('problem', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('is_photo_mfc', sa.Boolean(), nullable=False),
    sa.Column('is_comment_mfc', sa.Boolean(), nullable=False),
    sa.Column('is_photo_mo', sa.Boolean(), nullable=False),
    sa.Column('is_comment_mo', sa.Boolean(), nullable=False),
    sa.Column('is_no_data_button', sa.Boolean(), nullable=False),
    sa.Column('time_to_correct', sa.Interval(), nullable=False),
    sa.ForeignKeyConstraint(['problem'], ['dicts.problems.problem_name'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['zone'], ['dicts.zones.zone_name'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='dicts'
    )
    op.create_table('check',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('fil_', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('mfc_start', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('mfc_finish', sa.DateTime(), nullable=True),
    sa.Column('mo_user_id', sa.BigInteger(), nullable=True),
    sa.Column('mo_start', sa.DateTime(), nullable=True),
    sa.Column('mo_finish', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['fil_'], ['dicts.filials.fil_'], ),
    sa.ForeignKeyConstraint(['user_id'], ['data.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='data'
    )
    op.create_table('violation_found',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('check_id', sa.BigInteger(), nullable=False),
    sa.Column('violation_id', sa.Integer(), nullable=False),
    sa.Column('photo_id', sa.String(length=255), nullable=True),
    sa.Column('comm', sa.String(), nullable=True),
    sa.Column('photo_id_mo', sa.String(length=255), nullable=True),
    sa.Column('comm_mo', sa.String(), nullable=True),
    sa.Column('violation_detected', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('violation_fixed', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['check_id'], ['data.check.id'], ),
    sa.ForeignKeyConstraint(['violation_id'], ['dicts.violations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='data'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('violation_found', schema='data')
    op.drop_table('check', schema='data')
    op.drop_table('violations', schema='dicts')
    op.drop_table('filials', schema='dicts')
    op.drop_table('user', schema='data')
    op.drop_table('zones', schema='dicts')
    op.drop_table('problems', schema='dicts')
    op.drop_table('mos', schema='dicts')
    # ### end Alembic commands ###
