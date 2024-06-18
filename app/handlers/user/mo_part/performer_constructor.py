import time
import json
import datetime as dt
from typing import Optional
from loguru import logger
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mo_part import MoPerformerKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import MoPerformerMessages, DefaultMessages
from app.handlers.states import MoPerformerStates
from app.filters.mo_filters import MoPerformerFilter
from app.filters.default import not_constants
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService
from app.database.services.users import UserService
from app.view.cards import FormCards
from app.database.schemas.check_schema import CheckOut, CheckUpdate
from app.database.schemas.violation_found_schema import (
    ViolationFoundOut,
    ViolationFoundUpdate,
    ViolationFoundPendingMo
)
from app.utils.utils import get_index_by_violation_id
from dataclasses import dataclass
from aiogram.types import InlineKeyboardMarkup


@dataclass
class Reply:
    photo: str
    caption: str
    reply_markup: InlineKeyboardMarkup

@dataclass
class Category:
    is_task: bool
    is_pending: bool
    

class DataMoPerformerConstructor:
    def __init__(self, violation_found_id) -> None:
        self.violation_found_id = violation_found_id

    def pending_violation():
        pass

    def get_violations_out_lst_unsorted(self, data: dict):
        self.violation_out_objects = [
            ViolationFoundOut(**v)
            for k, v in data.items()
            if (k.startswith("vio_") and v)
            ]

    def is_pending(self, obj: ViolationFoundOut) -> bool:
        return obj.is_pending
    
    def is_task(self, obj: ViolationFoundOut) -> bool:
        return obj.is_task & (not obj.is_pending)
    
    def is_check_violation(self, obj: ViolationFoundOut) -> bool:
        result = (not obj.is_task) & (not obj.is_pending)
        return result

    def get_sorted_violations(self, lst: list[ViolationFoundOut]):
        res = sorted(
            lst,
            key=lambda x: x.violation_dict_id,
        )
        return res
    
    def get_pending_violations(self) -> list[ViolationFoundOut]:
        result = self.get_sorted_violations(
            list(filter(self.is_pending, self.violation_out_objects))
            )
        return result

    def get_task_violations(self) -> list[ViolationFoundOut]:
        result = self.get_sorted_violations(
            list(filter(self.is_task, self.violation_out_objects))
        )
        return result
    
    def get_check_violations(self, current_check_id: Optional[int]) -> list[ViolationFoundOut]:
        result = self.get_sorted_violations(
            list(filter(self.is_check_violation, self.violation_out_objects))
            )
        if current_check_id:
            result = [el for el in result if el.check_id == current_check_id]
        return result
    
    def form_reply(self,
                   violations_out: list[ViolationFoundOut],
                   order: int,
                   is_pending: bool) -> Reply:
        if is_pending:
            text_mes_func = violations_out[order].violation_card_pending
            kb_func = MoPerformerKeyboards().get_violation_pending_menu
        else:
            text_mes_func = violations_out[order].violation_card()
            kb_func = MoPerformerKeyboards().get_violation_menu
        
        photo_id = violations_out[order].photo_id_mfc
        text_mes = text_mes_func()
        prev_order = order - 1
        next_order = order + 1
        keyboard = kb_func(
            prev_violation_id=violations_out[prev_order].violation_found_id,
            violation_id=violations_out[order].violation_found_id,
            next_violation_id=(
                violations_out[next_order].violation_found_id
                if order != (len(violations_out) - 1)
                else violations_out[0].violation_found_id
            ),
        )
        return Reply(
            photo=photo_id,
            caption=text_mes,
            reply_markup=keyboard
        )

    def all_violations_pending_start(self) -> Reply:
        result = self.form_reply(
            violations_out=self.get_pending_violations(),
            order=0,
            is_pending=True
        )
        return result
    
    def all_violations_check_start(self, current_check_id: Optional[int]) -> Reply:
        result = self.form_reply(
            violations_out=self.get_check_violations(current_check_id=current_check_id),
            order=0,
            is_pending=False
        )
        return result
    
    def all_violations_task_start(self) -> Reply:
        result = self.form_reply(
            violations_out=self.get_task_violations(),
            order=0,
            is_pending=False
        )
        return result


    def get_index_by_violation_id(self,
                                  violations_found_out: list[ViolationFoundOut],
                                  violation_found_id: int) -> int:
        for index, obj in enumerate(violations_found_out):
            if obj.violation_found_id == violation_found_id:
                return index
        return 0
    
    def get_kb_after_violation_found_pending_process(self,
                                violation_found_out: ViolationFoundOut):
        
        # определение порядка должно быть ДО изменения данных состояния
        # тогда мы получим порядок нарушения до его удаления
        order = self.get_index_by_violation_id(
            violations_found_out=violation_out_objects,
            violation_found_id=self.violation_found_id
        )

        is_task = violation_found_out.is_task
        if is_task:
            violation_out_objects = self.get_task_violations()
        else: # is_check_violation
            violation_out_objects = self.get_check_violations()
        
        if not violation_out_objects:
            # удалить сообщение, выйти из меню
            pass
            # await callback.message.delete()
            # return
        
        reply_obj = self.form_reply(
            violations_out=violation_out_objects,
            # order=order + 1 if len(violation_out_objects) > 1 else 0,
            order=order if order != (len(violation_out_objects) - 1) else 0,
            is_pending=False
        )
        return reply_obj

    def get_next_prev_reply(self,
                            violation_found_out: ViolationFoundOut,
                            violation_found_id: int):
        is_pending = violation_found_out.is_pending
        is_task = violation_found_out.is_task
        if is_pending:
            violation_out_objects = self.get_pending_violations()

        elif is_task:
            violation_out_objects = self.get_task_violations()

        else:
            violation_out_objects = self.get_check_violations()

        # if len(violation_out_objects) == 1:
        #     await callback.answer(text=MoPerformerMessages.no_violations_buttons)
        #     return

        order = self.get_index_by_violation_id(
            violations_found_out=violation_out_objects,
            violation_found_id=violation_found_id
        )
        reply_obj = self.form_reply(
            violations_out=violation_out_objects,
            order=order,
            is_pending=is_pending
        )            

        return reply_obj
        # await callback.message.edit_media(
        #     media=InputMediaPhoto(media=photo_id, caption=text_mes), reply_markup=keyboard
        # )
        # await callback.answer()



    def process_cancel_correct(self,
                               violation_found_out: ViolationFoundOut,
                               violation_found_id: int):
        is_pending = violation_found_out.is_pending
        is_task = violation_found_out.is_task

        if is_pending:
            violation_out_objects = self.get_pending_violations()

        elif is_task:
            violation_out_objects = self.get_task_violations()

        else:
            violation_out_objects = self.get_check_violations()


        # if len(violation_out_objects) == 0:
        #     await callback.answer(text=MoPerformerMessages.no_violations_buttons)
        #     return

        order = self.get_index_by_violation_id(
            violations_found_out=violation_out_objects,
            violation_found_id=violation_found_id
        )
        reply_obj = self.form_reply(
            violations_out=violation_out_objects,
            order=order,
            is_pending=is_pending
        )    

        return reply_obj



    def cancel_before_save(self,
                           violation_found_out: ViolationFoundOut,
                           violation_found_id: int):
        is_pending = violation_found_out.is_pending
        is_task = violation_found_out.is_task

        if is_pending:
            violation_out_objects = self.get_pending_violations()


        elif is_task:
            violation_out_objects = self.get_task_violations()


        else:
            violation_out_objects = self.get_check_violations()

        # if len(violation_out_objects) == 0:
        #     await callback.answer(text=MoPerformerMessages.no_violations_buttons)
        #     return

        order = self.get_index_by_violation_id(
            violations_found_out=violation_out_objects,violation_found_id=violation_found_id
        )
        reply_obj = self.form_reply(
            violations_out=violation_out_objects,
            order=order,
            is_pending=is_pending
        )

        return reply_obj

    def current_check_active_violations(self,
                                        check_id: int):
        # violation_out_objects = self.get_check_violations(current_check_id=check_id)
        # if not violation_out_objects:
        #     await message.answer(
        #         text=MoPerformerMessages.no_violations,
        #         reply_markup=MoPerformerKeyboards().check_finished(),
        #     )
        # по сути вот такого достаточно
        # но надо предусмотреть условие выше
        # возможно лучше это сделать в функции all_violations_check_start
        reply_obj = self.all_violations_check_start(current_check_id=check_id)
        return reply_obj

    def continue_check_process(self, check_id: int):
        # if not violation_out_objects:
        #     await message.answer(
        #         text=MoPerformerMessages.no_violations,
        #         reply_markup=MoPerformerKeyboards().check_finished(),
        #     )
        reply_obj = self.all_violations_check_start(current_check_id=check_id)
        return reply_obj
 

    def finish_check_process(self, check_id: int):
        violation_out_objects = self.get_check_violations(current_check_id=check_id)
        # не забыть предусмотреть это условие
        # if violation_out_objects:
        #     await message.answer(
        #         text=MoPerformerMessages.cant_finish, reply_markup=message.reply_markup
        #     )
        #     return


    def back_from_correct_violation(self,
                                    violation_found_out: ViolationFoundOut,
                                    violation_found_id: int):

        is_pending = violation_found_out.is_pending
        is_task = violation_found_out.is_task

        if is_pending:
            violation_out_objects = violation_out_objects = self.get_pending_violations()


        elif is_task:
            violation_out_objects = self.get_task_violations()

        else:
            violation_out_objects = self.get_check_violations()
        order = self.get_index_by_violation_id(
            violations_found_out=violation_out_objects,
            violation_found_id=violation_found_id
        )
        reply_obj = self.form_reply(
            violations_out=violation_out_objects,
            order=order,
            is_pending=is_pending
        )    

        return reply_obj