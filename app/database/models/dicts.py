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
    str_255
)


class Mos(Base):
    __tablename__ = 'mos'
    __table_args__ = {'schema': 'dicts'}
    
    mo_: Mapped[str_pk]
    mo_population: Mapped[str_255]
    mo_type: Mapped[str_255]


class Filials(Base):
    __tablename__ = 'filials'
    __table_args__ = {'schema': 'dicts'}

    fil_: Mapped[str_pk]
    fil_population: Mapped[str_255]
    fil_type: Mapped[str_255]
    mo_: Mapped[str_255] = mapped_column(ForeignKey("dicts.mos.mo_", ondelete="CASCADE"))


class ProblemBlocs(Base):
    __tablename__ = 'problems'
    __table_args__ = {'schema': 'dicts'}

    problem_name: Mapped[str_pk]


class Zones(Base):
    __tablename__ = 'zones'
    __table_args__ = {'schema': 'dicts'}

    zone_name: Mapped[str_pk]


class Violations(Base):
    __tablename__ = 'violations'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    violation_name: Mapped[str_255]
    zone: Mapped[str_255] = mapped_column(ForeignKey("dicts.zones.zone_name", ondelete="CASCADE"))
    problem: Mapped[str_255] = mapped_column(ForeignKey("dicts.problems.problem_name", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(nullable=True)
    is_photo_mfc: Mapped[bool]
    is_comment_mfc: Mapped[bool]
    is_photo_mo: Mapped[bool]
    is_comment_mo: Mapped[bool]
    is_no_data_button: Mapped[bool]
    time_to_correct: Mapped[dt.timedelta] = mapped_column(Interval)

    violation_found: Mapped[list['ViolationFound']] = relationship(
        "ViolationFound",
        back_populates="violation_describe"
    )


