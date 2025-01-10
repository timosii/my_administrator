"""initial migration

Revision ID: 5f5f981f8a46
Revises: 48bc0ffff4b8
Create Date: 2025-01-10 09:52:58.130449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f5f981f8a46'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('CREATE SCHEMA IF NOT EXISTS dicts')
    op.execute('CREATE SCHEMA IF NOT EXISTS data')

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'dicts' AND table_name = 'mos') THEN
                DROP TABLE dicts.mos CASCADE;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'dicts' AND table_name = 'filials') THEN
                DROP TABLE dicts.filials CASCADE;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'dicts' AND table_name = 'violations') THEN
                DROP TABLE dicts.violations CASCADE;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'dicts' AND table_name = 'zones') THEN
                DROP TABLE dicts.zones CASCADE;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'data' AND table_name = 'check') THEN
                DROP TABLE "data"."check" CASCADE;
                IF EXISTS (SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = 'check_id_seq') THEN
                    DROP SEQUENCE "data"."check_id_seq";
                END IF;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'data' AND table_name = 'user') THEN
                DROP TABLE data."user" CASCADE;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'data' AND table_name = 'violation_found') THEN
                DROP TABLE data.violation_found CASCADE;
                IF EXISTS (SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = 'violation_found_id_seq') THEN
                    DROP SEQUENCE "data"."violation_found_id_seq";
                END IF;
            END IF;
        END
        $$;
    """)

    op.create_table('mos',
    sa.Column('mo_', sa.String(length=255), nullable=False),
    sa.Column('mo_population', sa.String(length=255), nullable=False),
    sa.Column('mo_type', sa.String(length=255), nullable=False),
    sa.Column('is_archieved', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('mo_'),
    schema='dicts'
    )
    op.create_table('violations',
    sa.Column('violation_dict_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('violation_name', sa.String(length=255), nullable=False),
    sa.Column('zone', sa.String(length=255), nullable=False),
    sa.Column('problem', sa.String(length=255), nullable=False),
    sa.Column('time_to_correct', sa.Interval(), nullable=False),
    sa.Column('is_gp', sa.Boolean(), nullable=False),
    sa.Column('is_dgp', sa.Boolean(), nullable=False),
    sa.Column('is_archieved', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('violation_dict_id'),
    schema='dicts'
    )
    op.create_table('zones',
    sa.Column('zone_name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('zone_name'),
    schema='dicts'
    )
    op.create_table('filials',
    sa.Column('fil_', sa.String(length=255), nullable=False),
    sa.Column('fil_population', sa.String(length=255), nullable=False),
    sa.Column('fil_type', sa.String(length=255), nullable=False),
    sa.Column('mo_', sa.String(length=255), nullable=False),
    sa.Column('is_archieved', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['mo_'], ['dicts.mos.mo_'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('fil_'),
    schema='dicts'
    )
    op.create_table('user',
    sa.Column('user_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('mo_', sa.String(length=255), nullable=True),
    sa.Column('fil_', sa.String(length=255), nullable=True),
    sa.Column('department', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('patronymic', sa.String(length=255), nullable=True),
    sa.Column('post', sa.String(length=255), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_mfc', sa.Boolean(), nullable=False),
    sa.Column('is_mfc_leader', sa.Boolean(), nullable=False),
    sa.Column('is_mo_performer', sa.Boolean(), nullable=False),
    sa.Column('is_mo_controler', sa.Boolean(), nullable=False),
    sa.Column('is_avail', sa.Boolean(), nullable=False),
    sa.Column('is_archived', sa.Boolean(), nullable=False),
    sa.Column('is_vacation', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.CheckConstraint('is_admin OR is_mfc OR is_mfc_leader OR is_mo_performer OR is_mo_controler', name='check_role_logic'),
    sa.ForeignKeyConstraint(['fil_'], ['dicts.filials.fil_'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mo_'], ['dicts.mos.mo_'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id'),
    schema='data'
    )
    op.create_table('check',
    sa.Column('check_id', sa.UUID(), nullable=False),
    sa.Column('fil_', sa.String(length=255), nullable=False),
    sa.Column('mfc_user_id', sa.BigInteger(), nullable=False),
    sa.Column('mfc_start', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('mfc_finish', sa.DateTime(), nullable=True),
    sa.Column('mo_start', sa.DateTime(), nullable=True),
    sa.Column('mo_finish', sa.DateTime(), nullable=True),
    sa.Column('is_task', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['fil_'], ['dicts.filials.fil_'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mfc_user_id'], ['data.user.user_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('check_id'),
    schema='data'
    )
    op.create_table('violation_found',
    sa.Column('violation_found_id', sa.UUID(), nullable=False),
    sa.Column('check_id', sa.UUID(), nullable=False),
    sa.Column('violation_dict_id', sa.Integer(), nullable=False),
    sa.Column('photo_id_mfc', sa.ARRAY(sa.String(length=255)), nullable=True),
    sa.Column('comm_mfc', sa.String(), nullable=True),
    sa.Column('mo_user_id', sa.BigInteger(), nullable=True),
    sa.Column('photo_id_mo', sa.String(length=255), nullable=True),
    sa.Column('comm_mo', sa.String(), nullable=True),
    sa.Column('violation_detected', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('violation_fixed', sa.DateTime(), nullable=True),
    sa.Column('is_pending', sa.Boolean(), nullable=False),
    sa.Column('violation_pending', sa.DateTime(), nullable=True),
    sa.Column('pending_period', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['check_id'], ['data.check.check_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mo_user_id'], ['data.user.user_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['violation_dict_id'], ['dicts.violations.violation_dict_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('violation_found_id'),
    schema='data'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('violation_found', schema='data')
    op.drop_table('check', schema='data')
    op.drop_table('user', schema='data')
    op.drop_table('filials', schema='dicts')
    op.drop_table('zones', schema='dicts')
    op.drop_table('violations', schema='dicts')
    op.drop_table('mos', schema='dicts')
    # ### end Alembic commands ###
