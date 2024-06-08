from pydantic import BaseModel
from typing import Optional
import datetime as dt


class ViolationBase(BaseModel):
    violation_dict_id: int
    violation_name: str    
    zone: str
    problem: str
    description: str

class ViolationInDB(ViolationBase):
    time_to_correct: Optional[dt.timedelta]

    class Config:
        from_attributes = True
