from pydantic import BaseModel
from typing import Optional
import datetime as dt
from app.utils.utils import format_timedelta

class CheckBase(BaseModel):
    fil_: str
    mfc_user_id: int
    is_task: bool

class CheckCreate(CheckBase):
    pass

class CheckUpdate(BaseModel):
    mo_user_id: Optional[int] = None
    mfc_finish: Optional[dt.datetime] = None
    mo_start: Optional[dt.datetime] = None
    mo_finish: Optional[dt.datetime] = None

class CheckInDB(CheckBase):
    check_id: int
    mfc_start: dt.datetime
    mfc_finish: Optional[dt.datetime] = None
    mo_start: Optional[dt.datetime] = None
    mo_finish: Optional[dt.datetime] = None
    
    class Config:
        from_attributes = True

class CheckOut(BaseModel):
    check_id: int
    fil_: str
    mfc_start: dt.datetime
    mfc_finish: dt.datetime
    violations_count: int

    def form_card_check_out(self) -> str:
        result = f"""
<b>Филиал:</b>
{self.fil_}
<b>Дата начала проверки:</b>
{self.mfc_start.strftime('%d.%m.%Y %H:%M')}
<b>Дата завершения проверки:</b>
{self.mfc_finish.strftime('%d.%m.%Y %H:%M')}
<b>Проверка заняла: {format_timedelta(self.mfc_finish - self.mfc_start)} </b>
<b>Количество нарушений:</b>
{self.violations_count}
        """
        return result

    class Config:
        from_attributes = True

class CheckOutUnfinished(BaseModel):
    fil_: str
    mfc_start: dt.datetime
    violations_count: int

    def form_card_unfinished_out(self):
        result = f"""
<b>Филиал:</b>
{self.fil_}
<b>Дата начала проверки:</b>
{self.mfc_start.strftime('%d.%m.%Y %H:%M')}
<b>Количество выявленных нарушений:</b>
{self.violations_count}
        """
        return result

    class Config:
        from_attributes = True


