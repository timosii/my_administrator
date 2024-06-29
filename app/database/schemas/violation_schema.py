import datetime as dt

from pydantic import BaseModel


class ViolationBase(BaseModel):
    violation_dict_id: int
    violation_name: str
    zone: str
    problem: str
    description: str


class ViolationInDB(ViolationBase):
    time_to_correct: dt.timedelta | None

    class Config:
        from_attributes = True
