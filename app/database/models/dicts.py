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
    Interval,
    func,
    Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import (
    Base,
    intpk,
    str_pk,
    str_256
)


class Mos(Base):
    __tablename__ = 'mos'
    __table_args__ = {'schema': 'dicts'}
    
    # id: Mapped[intpk]
    mo_name: Mapped[str_pk]


class Filials(Base):
    __tablename__ = 'filials'
    __table_args__ = {'schema': 'dicts'}

    # id: Mapped[intpk]
    fil_name: Mapped[str_pk]
    mo_name: Mapped[int] = mapped_column(ForeignKey("dicts.mos.mo_name", ondelete="CASCADE"))


class ProblemBlocs(Base):
    __tablename__ = 'problems'
    __table_args__ = {'schema': 'dicts'}

    # id: Mapped[intpk]
    problem_name: Mapped[str_pk]

class Zones(Base):
    __tablename__ = 'zones'
    __table_args__ = {'schema': 'dicts'}

    # id: Mapped[intpk]
    zone_name: Mapped[str_pk]


class Violations(Base):
    __tablename__ = 'violations'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    violation_name: Mapped[str_256]
    zone: Mapped[str_256] = mapped_column(ForeignKey("dicts.zones.zone_name", ondelete="CASCADE"))
    problem: Mapped[str_256] = mapped_column(ForeignKey("dicts.problems.problem_name", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(nullable=True)
    need_photo_mfc: Mapped[bool]
    need_comment_mfc: Mapped[bool]
    need_photo_mo: Mapped[bool]
    need_comment_mo: Mapped[bool]
    no_data_button: Mapped[bool]
    time_to_correct: Mapped[dt.timedelta] = mapped_column(Interval)
