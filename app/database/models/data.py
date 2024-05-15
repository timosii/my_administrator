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

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    telegram_id: Mapped[str]

    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id"))
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_mfc: Mapped[bool]
    is_mfc_leader: Mapped[bool] = mapped_column(default=False)
    is_mo_performer: Mapped[bool]
    is_mo_controler: Mapped[bool]
    created_at: Mapped[datetime_now]
    updated_at: Mapped[updated_at]

    checks: Mapped[list['Check']] = relationship(
        back_populates = "user"
    )

class ViolationFound(Base):
    __tablename__ = 'violation_found'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    check_id: Mapped[int] = mapped_column(ForeignKey("data.check.id"))
    violation_id: Mapped[int] = mapped_column(ForeignKey("dicts.violations.id"))
    photo_id: Mapped[str] = mapped_column(nullable=True)
    comm: Mapped[str] = mapped_column(nullable=True)
    violation_detected: Mapped[dt.datetime]
    violation_fixed: Mapped[dt.datetime] = mapped_column(nullable=True)

    check: Mapped['Check'] = relationship(
        back_populates="violations"
    )


class Check(Base):
    __tablename__ = 'check'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    mo_id: Mapped[int] = mapped_column(ForeignKey("dicts.mos.id"))
    fil_id: Mapped[int] = mapped_column(ForeignKey("dicts.filials.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("data.user.id"))
    check_start: Mapped[dt.datetime]
    check_finish: Mapped[dt.datetime]

    user: Mapped["User"] = relationship(
        back_populates="checks",
    )

    violations: Mapped[list['ViolationFound']] = relationship(
        back_populates="check"
    )
