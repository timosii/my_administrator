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
from app.database.database import (
    Base,
    intpk,
    str_256,
    datetime_now,
    updated_at,
    bigint_pk,
    bigint
)

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'data'}

    id: Mapped[intpk]
    telegram_id: Mapped[str_256]

    mo_: Mapped[str_256] = mapped_column(ForeignKey("dicts.mos.mo_name"))
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_mfc: Mapped[bool] = mapped_column(default=False)
    is_mfc_leader: Mapped[bool] = mapped_column(default=False)
    is_mo_performer: Mapped[bool] = mapped_column(default=False)
    is_mo_controler: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime_now]
    updated_at: Mapped[updated_at]

    checks: Mapped[list['Check']] = relationship(
        back_populates = "user"
    )

class ViolationFound(Base):
    __tablename__ = 'violation_found'
    __table_args__ = {'schema': 'data'}

    id: Mapped[bigint_pk]
    check_id: Mapped[bigint] = mapped_column(ForeignKey("data.check.id"))
    violation_id: Mapped[int] = mapped_column(ForeignKey("dicts.violations.id"))
    photo_id: Mapped[str_256] = mapped_column(nullable=True)
    comm: Mapped[str] = mapped_column(nullable=True)
    violation_detected: Mapped[dt.datetime]
    violation_fixed: Mapped[dt.datetime] = mapped_column(nullable=True)

    check: Mapped['Check'] = relationship(
        back_populates="violations"
    )


class Check(Base):
    __tablename__ = 'check'
    __table_args__ = {'schema': 'data'}

    id: Mapped[bigint_pk]
    fil: Mapped[str_256] = mapped_column(ForeignKey("dicts.filials.fil_name"))
    user_id: Mapped[int] = mapped_column(ForeignKey("data.user.id"))
    check_start: Mapped[dt.datetime]
    check_finish: Mapped[dt.datetime]

    user: Mapped["User"] = relationship(
        back_populates="checks",
    )

    violations: Mapped[list['ViolationFound']] = relationship(
        back_populates="check"
    )
