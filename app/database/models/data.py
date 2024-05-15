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
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from vars import intpk, datetime_now, updated_at


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    telegram_id: Mapped[str]

    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id", ondelete="CASCADE"))
    is_admin: Mapped[bool]
    is_mfc: Mapped[bool]
    is_mfc_leader: Mapped[bool]
    is_mo_performer: Mapped[bool]
    is_mo_controler: Mapped[bool]
    created_at: Mapped[datetime_now]
    updated_at: Mapped[updated_at]    


class ViolationsFound(Base):
    __tablename__ = 'violations_found'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    check_id: Mapped[int] = mapped_column(ForeignKey("data.checks.id"))
    zone_id: Mapped[int] = mapped_column(ForeignKey("dicts.zones.id"))
    violation_id: Mapped[int] = mapped_column(ForeignKey("dicts.violations.id"))
    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id", ondelete="CASCADE"))
    fil_id: Mapped[int] = mapped_column(ForeignKey("dicts.filials.id", ondelete="CASCADE"))
    photo_id: Mapped[str] = mapped_column(nullable=True)
    comm: Mapped[str] = mapped_column(nullable=True)
    check_start: Mapped[dt.datetime]
    check_finish: Mapped[dt.datetime]


class Checks(Base):
    __tablename__ = 'checks'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id", ondelete="CASCADE"))
    check_start: Mapped[dt.datetime]
    check_finish: Mapped[dt.datetime]