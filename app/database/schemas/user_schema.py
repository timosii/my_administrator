import datetime as dt

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    user_id: int
    last_name: str
    first_name: str
    patronymic: str | None = None
    post: str | None = None


class UserBaseInfo(BaseModel):
    last_name: str
    first_name: str
    patronymic: str | None = None
    post: str | None = None
    mo_: str | None = None
    fil_: str | None = None
    department: str | None = None


class UserCreate(UserBase):
    mo_: str | None = None
    fil_: str | None = None
    department: str | None = None
    is_admin: bool = False
    is_mfc: bool = False
    is_mfc_leader: bool = False
    is_mo_performer: bool = False
    is_mo_controler: bool = False
    is_avail: bool = False
    is_archived: bool = False
    is_vacation: bool = False


class UserUpdate(BaseModel):
    mo_: str | None = None
    fil_: str | None = None
    department: str | None = None
    last_name: str
    first_name: str
    patronymic: str | None = None
    post: str | None = None
    is_admin: bool = False
    is_mfc: bool = False
    is_mfc_leader: bool = False
    is_mo_performer: bool = False
    is_mo_controler: bool = False
    is_archived: bool = False
    is_vacation: bool = False


class UserInDB(UserBase):
    mo_: str | None = None
    fil_: str | None = None
    department: str | None = None
    is_admin: bool | None = False
    is_mfc: bool | None = False
    is_mfc_leader: bool | None = False
    is_mo_performer: bool | None = False
    is_mo_controler: bool | None = False
    is_archived: bool | None = False
    is_vacation: bool | None = False
    created_at: dt.datetime
    updated_at: dt.datetime | None = None
    model_config = ConfigDict(from_attributes=True)
