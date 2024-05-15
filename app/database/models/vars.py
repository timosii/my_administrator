import datetime as dt
from typing import Optional, Annotated
from sqlalchemy import (
    func,
)
from sqlalchemy.orm import mapped_column

intpk = Annotated[int, mapped_column(primary_key=True)]
datetime_now = Annotated[dt.datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[dt.datetime, mapped_column(
        server_default=func.now(),
        onupdate=dt.datetime.now,
    )]
