import datetime as dt
import enum
from typing import Optional, Annotated
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    MetaData,
    ForeignKey,
    func,
    Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from app.database.models.vars import intpk, datetime_now, updated_at


class Mos(Base):
    __tablename__ = 'mos'
    __table_args__ = {'schema': 'dicts'}
    
    id: Mapped[intpk]
    mo_name: Mapped[str]


class Filials(Base):
    __tablename__ = 'filials'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id", ondelete="CASCADE"))
    fil_name: Mapped[str]


class ProblemBlocs(Base):
    __tablename__ = 'problems'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    problem_name: Mapped[str]


class Zones(Base):
    __tablename__ = 'zones'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    zone_name: Mapped[str]


class Violations(Base):
    __tablename__ = 'violations'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    violation_name: Mapped[str]
    zone_id: Mapped[int] = mapped_column(ForeignKey("dicts.zones.id", ondelete="CASCADE"))
    problem_id: Mapped[int] = mapped_column(ForeignKey("dicts.problems.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(nullable=True)
    need_photo_mfc: Mapped[bool]
    need_comment_mfc: Mapped[bool]
    need_photo_mo: Mapped[bool]
    need_comment_mo: Mapped[bool]
    no_data_button: Mapped[bool]
    time_to_correct: Mapped[dt.timedelta]
