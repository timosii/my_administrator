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
    str_255,
    datetime_now,
    updated_at,
    bigint_pk,
    bigint_pk_tg,
    bigint,
    str_pk
)

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'data'}

    id: Mapped[bigint_pk_tg]

    mo_: Mapped[str_255] = mapped_column(ForeignKey("dicts.mos.mo_"))
    last_name: Mapped[str_255]
    first_name: Mapped[str_255]
    patronymic: Mapped[str_255]
    post: Mapped[str_255]
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_mfc: Mapped[bool] = mapped_column(default=False)
    is_mfc_leader: Mapped[bool] = mapped_column(default=False)
    is_mo_performer: Mapped[bool] = mapped_column(default=False)
    is_mo_controler: Mapped[bool] = mapped_column(default=False)
    is_archived: Mapped[bool] = mapped_column(default=False)
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
    photo_id: Mapped[str_255] = mapped_column(nullable=True)
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
    fil_: Mapped[str_255] = mapped_column(ForeignKey("dicts.filials.fil_"))
    user_id: Mapped[bigint] = mapped_column(ForeignKey("data.user.id"))
    mfc_start: Mapped[dt.datetime]
    mfc_finish: Mapped[dt.datetime] = mapped_column(nullable=True)
    mo_start: Mapped[dt.datetime] = mapped_column(nullable=True)
    mo_finish: Mapped[dt.datetime] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(
        back_populates="checks",
    )

    violations: Mapped[list['ViolationFound']] = relationship(
        back_populates="check"
    )
    # Добавить валидацию, что время финиша больше времени старта проверки
