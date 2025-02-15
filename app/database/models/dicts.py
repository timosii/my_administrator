import datetime as dt

from sqlalchemy import ForeignKey, Interval
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base, intpk, str_255, str_pk


class Mos(Base):
    __tablename__ = 'mos'
    __table_args__ = {'schema': 'dicts'}

    mo_: Mapped[str_pk]
    mo_population: Mapped[str_255]
    mo_type: Mapped[str_255]
    is_archieved: Mapped[bool]


class Filials(Base):
    __tablename__ = 'filials'
    __table_args__ = {'schema': 'dicts'}

    fil_: Mapped[str_pk]
    fil_population: Mapped[str_255]
    fil_type: Mapped[str_255]
    mo_: Mapped[str_255] = mapped_column(ForeignKey('dicts.mos.mo_', ondelete='CASCADE', onupdate='CASCADE'))
    is_archieved: Mapped[bool]


# class ProblemBlocs(Base):
#     __tablename__ = 'problems'
#     __table_args__ = {'schema': 'dicts'}

#     problem_name: Mapped[str_pk]


class Zones(Base):
    __tablename__ = 'zones'
    __table_args__ = {'schema': 'dicts'}

    zone_name: Mapped[str_pk]


class Violations(Base):
    __tablename__ = 'violations'
    __table_args__ = {'schema': 'dicts'}

    violation_dict_id: Mapped[intpk]
    violation_name: Mapped[str_255]
    zone: Mapped[str_255]
    problem: Mapped[str_255]
    # description: Mapped[str] = mapped_column(nullable=True)
    # is_photo_mfc: Mapped[bool]
    # is_comment_mfc: Mapped[bool]
    # is_photo_mo: Mapped[bool]
    # is_comment_mo: Mapped[bool]
    # is_no_data_button: Mapped[bool]
    time_to_correct: Mapped[dt.timedelta] = mapped_column(Interval)
    is_gp: Mapped[bool]
    is_dgp: Mapped[bool]
    is_archieved: Mapped[bool]
