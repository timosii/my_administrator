from pydantic import BaseModel
from typing import Optional
import datetime as dt
from app.utils.utils import format_timedelta


class ViolationFoundBase(BaseModel):
    check_id: int
    violation_dict_id: int

class ViolationFoundCreate(ViolationFoundBase):
    pass
    # violation_detected: dt.datetime

class ViolationFoundUpdate(BaseModel):
    # violation_found_id: int
    photo_id_mfc: Optional[str] = None
    comm_mfc: Optional[str] = None
    photo_id_mo: Optional[str] = None
    comm_mo: Optional[str] = None
    violation_fixed: Optional[dt.datetime] = None

class ViolationFoundInDB(ViolationFoundBase):
    violation_found_id: int
    photo_id_mfc: Optional[str] = None
    comm_mfc: Optional[str] = None
    violation_detected: dt.datetime
    violation_fixed: Optional[dt.datetime] = None

    class Config:
        from_attributes = True

class ViolationFoundOut(ViolationFoundBase):
    mo: str
    fil_: str
    is_task: bool # найдено нарушение в рамках уведомления или в рамках проверки
    violation_found_id: int
    zone: str
    violation_name: str
    time_to_correct: dt.timedelta
    violation_detected: dt.datetime
    comm_mfc: Optional[str] = None
    photo_id_mfc: Optional[str] = None
    photo_id_mo: Optional[str] = None
    comm_mo: Optional[str] = None

    def violation_card(self) -> str:
        result = f"""
<b>Зона:</b>
{self.zone}
<b>Нарушение:</b>
{self.violation_name}
<b>Время выявления нарушения:</b>
{self.violation_detected.strftime('%d.%m.%Y %H:%M')}

Комментарий: {self.comm_mfc if self.comm_mfc else 'отсутствует'}
Время на исправление: {format_timedelta(self.time_to_correct)}
        """
        return result

    class Config:
        from_attributes = True
