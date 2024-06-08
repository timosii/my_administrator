from pydantic import BaseModel
from typing import Optional
import datetime as dt


class ViolationFoundBase(BaseModel):
    check_id: int
    violation_dict_id: int

class ViolationFoundCreate(ViolationFoundBase):
    photo_id_mfc: Optional[str] = None
    comm_mfc: Optional[str] = None

class ViolationFoundUpdate(BaseModel):
    photo_id_mo: Optional[str] = None
    comm_mo: Optional[str] = None
    violation_fixed: Optional[dt.datetime] = None

class ViolationFoundInDB(ViolationFoundBase):
    violation_found_id: int
    photo_id_mfc: Optional[str] = None
    comm_mfc: Optional[str] = None
    violation_detected: dt.datetime
    violation_fixed: Optional[dt.datetime] = None

    class Config:
        from_attributes = True

class ViolationFoundOut(BaseModel):
    violation_found_id: int
    violation_dict_id: int
    zone: str
    violation_name: str
    time_to_correct: dt.timedelta
    violation_detected: dt.datetime
    comm_mfc: Optional[str] = None,
    photo_id_mfc: Optional[str] = None

    class Config:
        from_attributes = True
