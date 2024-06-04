from pydantic import BaseModel
from typing import Optional
import datetime as dt

class CheckBase(BaseModel):
    fil_: str
    user_id: int
    is_task: bool

class CheckCreate(CheckBase):
    pass

class CheckUpdate(BaseModel):
    mo_user_id: Optional[int] = None
    mfc_finish: Optional[dt.datetime] = None
    mo_start: Optional[dt.datetime] = None
    mo_finish: Optional[dt.datetime] = None

class CheckInDB(CheckBase):
    id: int
    mfc_start: dt.datetime
    mfc_finish: Optional[dt.datetime] = None
    mo_start: Optional[dt.datetime] = None
    mo_finish: Optional[dt.datetime] = None
    
    class Config:
        from_attributes = True

class CheckOut(BaseModel):
    id: int
    fil_: str
    mfc_start: dt.datetime
    mfc_finish: dt.datetime
    violations_count: int

    class Config:
        from_attributes = True

class CheckOutUnfinished(BaseModel):
    fil_: str
    mfc_start: dt.datetime
    violations_count: int

    class Config:
        from_attributes = True


