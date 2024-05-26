from pydantic import BaseModel
from typing import Optional
import datetime as dt


class ViolationBase(BaseModel):
    id: int
    violation_name: str    
    zone: str
    problem: str
    description: str

class ViolationInDB(ViolationBase):
    pass

    class Config:
        from_attributes = True
