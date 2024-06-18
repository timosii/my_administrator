import datetime as dt
import enum
from typing import Optional, Annotated
from sqlalchemy import (
    ForeignKey,
    CheckConstraint,
    TIMESTAMP
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
    str_pk,
)
from sqlalchemy.types import DateTime


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        CheckConstraint('is_admin OR is_mfc OR is_mfc_leader OR is_mo_performer OR is_mo_controler', name='check_role_logic'),
        {'schema': 'data'},
    )

    user_id: Mapped[bigint_pk_tg]

    mo_: Mapped[str_255] = mapped_column(ForeignKey("dicts.mos.mo_"), nullable=True)
    fil_: Mapped[str_255] = mapped_column(ForeignKey("dicts.filials.fil_"), nullable=True)
    
    department: Mapped[str_255] = mapped_column(nullable=True)
    last_name: Mapped[str_255]
    first_name: Mapped[str_255]
    patronymic: Mapped[str_255]= mapped_column(nullable=True)
    post: Mapped[str_255]= mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_mfc: Mapped[bool] = mapped_column(default=False)
    is_mfc_leader: Mapped[bool] = mapped_column(default=False)
    is_mo_performer: Mapped[bool] = mapped_column(default=False)
    is_mo_controler: Mapped[bool] = mapped_column(default=False)
    is_archived: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime_now]
    updated_at: Mapped[updated_at]


class ViolationFound(Base):
    __tablename__ = 'violation_found'
    __table_args__ = {'schema': 'data'}

    violation_found_id: Mapped[bigint_pk]

    check_id: Mapped[bigint] = mapped_column(ForeignKey("data.check.check_id", ondelete='CASCADE'))
    violation_dict_id: Mapped[int] = mapped_column(ForeignKey("dicts.violations.violation_dict_id"))
    photo_id_mfc: Mapped[str_255] = mapped_column(nullable=True)
    comm_mfc: Mapped[str] = mapped_column(nullable=True)
    photo_id_mo: Mapped[str_255] = mapped_column(nullable=True)
    comm_mo: Mapped[str] = mapped_column(nullable=True)
    violation_detected: Mapped[datetime_now]
    violation_fixed: Mapped[dt.datetime] = mapped_column(nullable=True)
    is_pending: Mapped[bool] = mapped_column(default=False)
    violation_pending: Mapped[dt.datetime] = mapped_column(nullable=True)

    check: Mapped['Check'] = relationship(
        back_populates="violations"
    )


class Check(Base):
    __tablename__ = 'check'
    __table_args__ = (
        # CheckConstraint('mo_start > mfc_finish', name='check_time_mo_check'),
        {'schema': 'data'},
    )

    check_id: Mapped[bigint_pk]
    fil_: Mapped[str_255] = mapped_column(ForeignKey("dicts.filials.fil_"))
    mfc_user_id: Mapped[bigint] = mapped_column(ForeignKey("data.user.user_id"))
    mfc_start: Mapped[datetime_now]
    mfc_finish: Mapped[dt.datetime] = mapped_column(nullable=True)
    mo_user_id: Mapped[bigint] = mapped_column(ForeignKey("data.user.user_id"), nullable=True)
    mo_start: Mapped[dt.datetime] = mapped_column(nullable=True)
    mo_finish: Mapped[dt.datetime] = mapped_column(nullable=True)
    is_task: Mapped[bool] = mapped_column(default=False)
    
    mfc_user: Mapped["User"] = relationship('User', foreign_keys=[mfc_user_id])
    mo_user: Mapped["User"] = relationship('User', foreign_keys=[mo_user_id])

    violations: Mapped[list['ViolationFound']] = relationship(
        back_populates="check"
    )