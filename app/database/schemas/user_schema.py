from pydantic import BaseModel
from typing import Optional
import datetime as dt

class UserBase(BaseModel):
    id: int
    mo_: str
    last_name: str
    first_name: str
    patronymic: str
    post: str

class UserCreate(UserBase):
    is_admin: Optional[bool] = None
    is_mfc: Optional[bool] = None
    is_mfc_leader: Optional[bool] = None
    is_mo_performer: Optional[bool] = None
    is_mo_controler: Optional[bool] = None
    is_archived: Optional[bool] = None

class UserUpdate(UserCreate):
    pass

class UserInDB(UserBase):
    is_admin: Optional[bool] = None
    is_mfc: Optional[bool] = None
    is_mfc_leader: Optional[bool] = None
    is_mo_performer: Optional[bool] = None
    is_mo_controler: Optional[bool] = None
    created_at: dt.datetime

    class Config:
        from_attributes = True
