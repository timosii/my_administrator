from pydantic import BaseModel
from typing import Optional
import datetime as dt
from app.utils.utils import format_timedelta, to_moscow_time


class ViolationFoundBase(BaseModel):
    check_id: int
    violation_dict_id: int

class ViolationFoundCreate(ViolationFoundBase):
    pass

class ViolationFoundTestCreate(ViolationFoundCreate):
    violation_dict_id: int
    violation_detected: dt.datetime
    photo_id_mfc: str
    comm_mfc: str

class ViolationFoundUpdate(BaseModel):
    photo_id_mfc: Optional[str] = None
    comm_mfc: Optional[str] = None
    photo_id_mo: Optional[str] = None
    comm_mo: Optional[str] = None
    violation_fixed: Optional[dt.datetime] = None
    is_pending: Optional[bool] = False
    violation_pending: Optional[dt.datetime] = None

class ViolationFoundInDB(ViolationFoundBase):
    violation_found_id: int
    photo_id_mfc: Optional[str]
    comm_mfc: Optional[str]
    violation_detected: dt.datetime
    violation_fixed: Optional[dt.datetime]
    is_pending: bool
    violation_pending: Optional[dt.datetime]

    class Config:
        from_attributes = True

class ViolationFoundDeleteMfc(BaseModel):
    violation_detected: None=None
    time_to_correct: None=None
    violation_found_id: None=None
    violation_name: None=None
    violation_dict_id: None=None
    photo_id_mfc: None=None
    comm_mfc: None=None

class ViolationFoundClearData(BaseModel):
    # check_id: None=None
    violation_found_id: None=None
    photo_id_mo: None=None
    comm_mo: None=None
    comm_mfc: None=None
    is_take: None=None
    is_task: None=None
    photo_id_mfc: None=None
    photo_id_mo: None=None
    time_to_correct: None=None
    violation_detected: None=None
    violation_dict_id: None=None
    violation_found_id: None=None
    violation_name: None=None
    zone: None=None
    is_pending: None=None
    violation_pending: None=None


class ViolationFoundRedisSaved(BaseModel):
    check_id: Optional[int]=None
    violation_found_id: Optional[int]=None
    photo_id_mo: Optional[str]=None
    comm_mo: Optional[str]=None
    comm_mfc: Optional[str]=None
    is_take: Optional[None]=None
    is_task: Optional[bool]=None
    photo_id_mfc: Optional[str]=None
    photo_id_mo: Optional[str]=None
    time_to_correct: Optional[str]=None
    violation_detected: Optional[str]=None
    violation_dict_id: Optional[int]=None
    violation_found_id: Optional[int]=None
    violation_name: Optional[str]=None
    is_pending: bool
    violation_pending: Optional[str]=None


class ViolationFoundOut(ViolationFoundBase):
    mo: str
    fil_: str
    is_task: bool # True если нарушение найдено в рамках уведомления
    violation_found_id: int
    zone: str
    violation_name: str
    time_to_correct: dt.timedelta
    violation_detected: dt.datetime
    comm_mfc: Optional[str] = None
    photo_id_mfc: Optional[str] = None
    photo_id_mo: Optional[str] = None
    comm_mo: Optional[str] = None
    is_pending: Optional[bool]
    violation_pending: Optional[dt.datetime]

    def violation_card(self) -> str:
        result = f"""
<b>Зона:</b>
{self.zone}
<b>Нарушение:</b>
{self.violation_name}
<b>Время выявления нарушения:</b>
{to_moscow_time(self.violation_detected).strftime('%d.%m.%Y %H:%M')}

Комментарий: {self.comm_mfc if self.comm_mfc else 'отсутствует'}
Время на исправление: {format_timedelta(self.time_to_correct)}
        """
        return result

    def violation_card_pending(self) -> str:
        result = f"""
<b>Зона:</b>
{self.zone}
<b>Нарушение:</b>
{self.violation_name}
<b>Время выявления нарушения:</b>
{to_moscow_time(self.violation_detected).strftime('%d.%m.%Y %H:%M')}
<b>Время переноса нарушения:</b>
{to_moscow_time(self.violation_pending).strftime('%d.%m.%Y %H:%M')}

Комментарий: {self.comm_mfc if self.comm_mfc else 'отсутствует'}
Время на исправление: {format_timedelta(self.time_to_correct)}
        """
        return result

    class Config:
        from_attributes = True
