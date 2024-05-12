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


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[dt.datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[dt.datetime, mapped_column(
        server_default=func.now(),
        onupdate=dt.datetime.now,
    )]


class MOs(Base):
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


class Violations(Base):
    __tablename__ = 'violations'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    violation_name: Mapped[str]


class Zones(Base):
    __tablename__ = 'zones'
    __table_args__ = {'schema': 'dicts'}

    id: Mapped[intpk]
    zone_name: Mapped[str]


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    telegram_id: Mapped[str]
    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id", ondelete="CASCADE"))
    fil_id: Mapped[int] = mapped_column(ForeignKey("dicts.filials.id", ondelete="CASCADE"))
    is_admin: Mapped[bool]
    is_mfc: Mapped[bool]
    is_mo: Mapped[bool]


class Checks(Base):
    __tablename__ = 'checks'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    zone_id: Mapped[int] = mapped_column(ForeignKey("dicts.zones.id", ondelete="CASCADE"))
    violation_id: Mapped[int] = mapped_column(ForeignKey("dicts.violations.id", ondelete="CASCADE"))
    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id", ondelete="CASCADE"))
    fil_id: Mapped[int] = mapped_column(ForeignKey("dicts.filials.id", ondelete="CASCADE"))
    check_start: Mapped[dt.datetime]
    check_finish: Mapped[dt.datetime]
    photo_id: Mapped[str]
    comm: Mapped[str]
