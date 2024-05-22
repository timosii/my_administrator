from pydantic import BaseModel
from typing import Optional
import datetime as dt

class ViolationFoundBase(BaseModel):
    check_id: int
    violation_id: int
    violation_detected: dt.datetime

class ViolationFoundCreate(ViolationFoundBase):
    pass

class ViolationFoundUpdate(BaseModel):
    photo_id: Optional[str] = None
    comm: Optional[str] = None
    violation_fixed: Optional[dt.datetime] = None

class ViolationFoundInDB(ViolationFoundBase):
    id: int
    photo_id: Optional[str] = None
    comm: Optional[str] = None
    violation_fixed: Optional[dt.datetime] = None

    class Config:
        from_attributes = True
