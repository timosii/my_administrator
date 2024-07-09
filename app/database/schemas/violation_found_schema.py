import datetime as dt

from pydantic import BaseModel

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
    photo_id_mfc: str | None = None
    comm_mfc: str | None = None
    mo_user_id: int | None = None
    photo_id_mo: str | None = None
    comm_mo: str | None = None
    violation_fixed: dt.datetime | None = None
    is_pending: bool | None = False
    violation_pending: dt.datetime | None = None


class ViolationFoundInDB(ViolationFoundBase):
    violation_found_id: int
    photo_id_mfc: str | None
    comm_mfc: str | None
    mo_user_id: int | None
    comm_mo: str | None
    violation_detected: dt.datetime
    violation_fixed: dt.datetime | None
    is_pending: bool
    violation_pending: dt.datetime | None

    class Config:
        from_attributes = True


class ViolationFoundDeleteMfc(BaseModel):
    violation_detected: None = None
    time_to_correct: None = None
    violation_found_id: None = None
    violation_name: None = None
    violation_dict_id: None = None
    photo_id_mfc: None = None
    comm_mfc: None = None


class ViolationFoundClearInfo(ViolationFoundDeleteMfc):
    check_id: None = None
    mfc_start: None = None
    violations_completed: list = []
    zone: None = None


class ViolationFoundClearData(BaseModel):
    violation_found_id: None = None
    photo_id_mo: None = None
    comm_mo: None = None
    comm_mfc: None = None
    is_take: None = None
    is_task: None = None
    photo_id_mfc: None = None
    time_to_correct: None = None
    violation_detected: None = None
    violation_dict_id: None = None
    violation_name: None = None
    zone: None = None
    is_pending: None = None
    violation_pending: None = None


class ViolationFoundOut(ViolationFoundBase):
    mo: str
    fil_: str
    is_task: bool  # True если нарушение найдено в рамках уведомления
    violation_found_id: int
    zone: str
    violation_name: str
    time_to_correct: dt.timedelta
    violation_detected: dt.datetime
    comm_mfc: str | None = None
    photo_id_mfc: str | None = None
    mo_user_id: int | None = None
    photo_id_mo: str | None = None
    comm_mo: str | None = None
    is_pending: bool
    violation_pending: dt.datetime | None

    def violation_card(self) -> str:
        result = f"""
<b>Зона:</b>
{self.zone}
<b>Нарушение:</b>
{self.violation_name}
<b>Время выявления нарушения:</b>
{to_moscow_time(self.violation_detected).strftime('%d.%m.%Y %H:%M')}

Комментарий <b>при выявлении</b>: {self.comm_mfc if self.comm_mfc else 'отсутствует'}
<b>Время на исправление</b>: {format_timedelta(self.time_to_correct)}
        """
        return result

    def violation_card_pending(self) -> str:
        comm_mo_format = self.comm_mo.split('\n')[-1] if self.comm_mo else None
        result = f"""
<b>Зона:</b>
{self.zone}
<b>Нарушение:</b>
{self.violation_name}
<b>Время выявления нарушения:</b>
{to_moscow_time(self.violation_detected).strftime('%d.%m.%Y %H:%M')}
<b>Время переноса нарушения:</b>
{to_moscow_time(self.violation_pending).strftime('%d.%m.%Y %H:%M') if self.violation_pending else 'отсутствует'}

Комментарий <b>при выявлении</b>: {self.comm_mfc if self.comm_mfc else 'отсутствует'}
Комментарий <b>при переносе</b>: {comm_mo_format if comm_mo_format else 'отсутствует'}
<b>Время на исправление</b>: {format_timedelta(self.time_to_correct)}
        """
        return result

    class Config:
        from_attributes = True
