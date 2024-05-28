from pydantic import BaseModel
from typing import Optional
import datetime as dt


class ViolationFoundBase(BaseModel):
    check_id: int
    violation_id: int


class ViolationFoundCreate(ViolationFoundBase):
    photo_id: Optional[str] = None
    comm: Optional[str] = None


class ViolationFoundUpdate(BaseModel):
    photo_id: Optional[str] = None
    comm: Optional[str] = None
    violation_fixed: Optional[dt.datetime] = None


class ViolationFoundInDB(ViolationFoundBase):
    id: int
    photo_id: Optional[str] = None
    comm: Optional[str] = None
    violation_detected: dt.datetime
    violation_fixed: Optional[dt.datetime] = None

    class Config:
        from_attributes = True

class ViolationFoundOut(BaseModel):
    id: int
    zone: str
    violation_name: str
    time_to_correct: dt.timedelta
    violation_detected: dt.datetime
    comm: Optional[str] = None,
    photo_id: Optional[str] = None

    class Config:
        from_attributes = True
