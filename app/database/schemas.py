import datetime as dt
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
# expire_on_commit=False

class CheckAddDTO(BaseModel):
    mo_id: int
    fil_id: int
    user_id: int
    check_start: dt.datetime
    check_finish: dt.datetime

class CheckDTO(CheckAddDTO):
    id: int

class UserAddDTO(BaseModel):
    telegram_id: str
    mo_id: int
    is_admin: bool
    is_mfc: bool
    is_mfc_leader: bool
    is_mo_performer: bool
    is_mo_controler: bool

class UserDTO(UserAddDTO):
    id: int
    created_at: dt.datetime
    updated_at: dt.datetime

class ViolationFoundAddDTO(BaseModel):
    check_id: int
    violation_id: int
    photo_id: str | None
    comm: str | None
    violation_detected: dt.datetime
    violation_fixed: dt.datetime | None

class ViolationsFoundDTO(ViolationFoundAddDTO):
    id: int

class ChecksRelDTO(CheckDTO):
    user: 'UserDTO'
    violations: list['ViolationsFoundDTO']

class UserRelDTO(UserDTO):
    checks: list['CheckDTO']

class ViolationsFoundRelDTO(ViolationsFoundDTO):
    check: 'CheckDTO'
