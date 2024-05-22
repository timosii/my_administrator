from pydantic import BaseModel
from typing import Optional
import datetime as dt

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    is_admin: Optional[bool] = None
    is_mfc: Optional[bool] = None
    is_mfc_leader: Optional[bool] = None
    is_mo_performer: Optional[bool] = None
    is_mo_controler: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_admin: bool
    is_mfc: bool
    is_mfc_leader: bool
    is_mo_performer: bool
    is_mo_controler: bool
    created_at: dt.datetime

    class Config:
        from_attributes = True
