from pydantic import BaseModel
from typing import Optional
import datetime as dt

class UserBase(BaseModel):
    user_id: int
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    post: Optional[str] = None

class UserCreate(UserBase):
    mo_: Optional[str] = None
    fil_: Optional[str] = None
    department: Optional[str] = None
    is_admin: Optional[bool] = None
    is_mfc: Optional[bool] = None
    is_mfc_leader: Optional[bool] = None
    is_mo_performer: Optional[bool] = None
    is_mo_controler: Optional[bool] = None
    is_archived: Optional[bool] = None

class UserUpdate(UserCreate):
    pass

class UserInDB(UserBase):
    fil_: Optional[str] = None
    is_admin: Optional[bool] = None
    is_mfc: Optional[bool] = None
    is_mfc_leader: Optional[bool] = None
    is_mo_performer: Optional[bool] = None
    is_mo_controler: Optional[bool] = None
    created_at: dt.datetime
    updated_at: Optional[dt.datetime] = None

    class Config:
        from_attributes = True
