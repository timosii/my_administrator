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
    is_admin: bool = False
    is_mfc: bool = False
    is_mfc_leader: bool = False
    is_mo_performer: bool = False
    is_mo_controler: bool = False
    is_archived: bool = False

class UserUpdate(BaseModel):
    mo_: Optional[str] = None
    fil_: Optional[str] = None
    department: Optional[str] = None
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    post: Optional[str] = None
    is_admin: bool = False
    is_mfc: bool = False
    is_mfc_leader: bool = False
    is_mo_performer: bool = False
    is_mo_controler: bool = False
    is_archived: bool = False

class UserInDB(UserBase):
    mo_: Optional[str] = None
    fil_: Optional[str] = None
    department: Optional[str] = None
    is_admin: Optional[bool] = False
    is_mfc: Optional[bool] = False
    is_mfc_leader: Optional[bool] = False
    is_mo_performer: Optional[bool] = False
    is_mo_controler: Optional[bool] = False
    is_archived: Optional[bool] = False
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]

    class Config:
        from_attributes = True
