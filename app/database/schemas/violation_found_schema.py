import datetime as dt

from pydantic import BaseModel, ConfigDict
from pydantic.types import UUID

from app.utils.utils import format_timedelta, to_moscow_time


class ViolationFoundBase(BaseModel):
    check_id: UUID
    violation_dict_id: int


class ViolationFoundCreate(ViolationFoundBase):
    pass


class ViolationFoundTestCreate(ViolationFoundCreate):
    violation_dict_id: int
    violation_detected: dt.datetime
    photo_id_mfc: list[str]
    comm_mfc: str


class ViolationFoundUpdate(BaseModel):
    photo_id_mfc: list[str] | None = None
    comm_mfc: str | None = None
    mo_user_id: int | None = None
    photo_id_mo: str | None = None
    comm_mo: str | None = None
    violation_fixed: dt.datetime | None = None
    is_pending: bool | None = False
    violation_pending: dt.datetime | None = None
    pending_period: dt.datetime | None = None


class ViolationFoundInDB(ViolationFoundBase):
    violation_found_id: UUID
    photo_id_mfc: list[str] | None = None
    comm_mfc: str | None = None
    mo_user_id: int | None = None
    comm_mo: str | None = None
    violation_detected: dt.datetime
    violation_fixed: dt.datetime | None = None
    is_pending: bool
    violation_pending: dt.datetime | None = None
    pending_period: dt.datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ViolationFoundDeleteMfc(BaseModel):
    violation_detected: None = None
    time_to_correct: None = None
    violation_found_id: None = None
    # violation_name: None = None
    problem: None = None
    violation_dict_id: None = None
    photo_id_mfc: None = None
    comm_mfc: None = None


class ViolationFoundClearInfo(ViolationFoundDeleteMfc):
    check_id: None = None
    mfc_start: None = None
    violations_completed: dict = {}
    zone: None = None
    violation_name: None = None


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
    problem: None = None
    zone: None = None
    is_pending: None = None
    violation_pending: None = None
    pending_period: None = None


class ViolationFoundOut(BaseModel):
    mo: str
    fil_: str
    check_id: str
    violation_dict_id: int
    is_task: bool  # True если нарушение найдено в рамках уведомления
    violation_found_id: str
    zone: str
    violation_name: str
    problem: str
    time_to_correct: dt.timedelta
    violation_detected: dt.datetime
    comm_mfc: str | None = None
    photo_id_mfc: list[str] | None = None
    mo_user_id: int | None = None
    photo_id_mo: str | None = None
    comm_mo: str | None = None
    is_pending: bool
    violation_pending: dt.datetime | None = None
    pending_period: dt.datetime | None = None

    def violation_card(self) -> str:
        result = f"""
<b>Категория:</b>
{self.zone}
<b>Нарушение:</b>
{self.violation_name}
<b>Проблема:</b>
{self.problem}
<b>Время выявления нарушения:</b>
{to_moscow_time(self.violation_detected).strftime('%d.%m.%Y %H:%M')}

Комментарий <b>при выявлении</b>: {self.comm_mfc if self.comm_mfc else 'отсутствует'}
<b>Время на исправление</b>: {format_timedelta(self.time_to_correct)}
        """
        return result

    def violation_card_pending(self) -> str:
        comm_mo_format = self.comm_mo.split('\n')[-1] if self.comm_mo else None
        result = f"""
<b>Категория:</b>
{self.zone}
<b>Нарушение:</b>
{self.violation_name}
<b>Проблема:</b>
{self.problem}
<b>Время выявления нарушения:</b>
{to_moscow_time(self.violation_detected).strftime('%d.%m.%Y %H:%M')}
<b>Время переноса нарушения:</b>
{to_moscow_time(self.violation_pending).strftime('%d.%m.%Y %H:%M') if self.violation_pending else 'отсутствует'}
<b>Срок переноса нарушения:</b>
{to_moscow_time(self.pending_period).strftime('%d.%m.%Y') if self.pending_period else 'отсутствует'}

Комментарий <b>при выявлении</b>: {self.comm_mfc if self.comm_mfc else 'отсутствует'}
Комментарий <b>при переносе</b>: {comm_mo_format if comm_mo_format else 'отсутствует'}
<b>Время на исправление</b>: {format_timedelta(self.time_to_correct)}
        """
        return result
    model_config = ConfigDict(from_attributes=True)
