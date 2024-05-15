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
datetime_now = Annotated[dt.datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[dt.datetime, mapped_column(
        server_default=func.now(),
        onupdate=dt.datetime.now,
    )]