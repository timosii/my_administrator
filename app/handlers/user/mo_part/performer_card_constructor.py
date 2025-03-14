from typing import Optional

from loguru import logger

from app.database.schemas.helpers import Reply
from app.database.schemas.violation_found_schema import ViolationFoundOut
from app.keyboards.mo_part import MoPerformerKeyboards


class MoPerformerCard:
    def __init__(self,
                 data: dict) -> None:
        self.data = data
        # self.violations_found_out_objects = [
        #     ViolationFoundOut(**v)
        #     for k, v in self.data.items()
        #     if (k.startswith('vio_') and v)
        # ]
        self.get_violations_out_lst_unsorted()

    def get_violations_out_lst_unsorted(self):
        self.violations_found_out_objects = [
            ViolationFoundOut(**v)
            for k, v in self.data.items()
            if (k.startswith('vio_') and v)
        ]

    async def is_pending(self, obj: ViolationFoundOut) -> bool:
        return obj.is_pending

    async def is_task(self, obj: ViolationFoundOut) -> bool:
        return (obj.is_task and not obj.is_pending)

    async def is_check_violation(self, obj: ViolationFoundOut) -> bool:
        result = (not obj.is_task and not obj.is_pending)
        logger.debug(f'IS_CHECK_V: {result}')
        return result

    async def get_sorted_violations(self, lst: list[ViolationFoundOut]):
        res = sorted(
            lst,
            key=lambda x: x.violation_dict_id,
        )
        return res

    async def get_pending_violations(self) -> list[ViolationFoundOut]:
        pending_violations = [
            violation
            for violation in self.violations_found_out_objects
            if await self.is_pending(violation)
        ]
        result = await self.get_sorted_violations(pending_violations)
        # result = await self.get_sorted_violations(
        #     list(filter(self.is_pending, self.violations_found_out_objects))
        # )
        return result

    async def get_task_violations(self) -> list[ViolationFoundOut]:
        task_violations = [
            violation
            for violation in self.violations_found_out_objects
            if await self.is_task(violation)
        ]
        result = await self.get_sorted_violations(task_violations)
        # result = await self.get_sorted_violations(
        #     list(filter(self.is_task, self.violations_found_out_objects))
        # )
        return result

    async def get_check_violations(self) -> list[ViolationFoundOut]:
        check_violations = [
            violation
            for violation in self.violations_found_out_objects
            if await self.is_check_violation(violation)
        ]
        result = await self.get_sorted_violations(check_violations)
        # result = await self.get_sorted_violations(
        #     list(filter(self.is_check_violation, self.violations_found_out_objects))
        # )
        return result

    async def get_current_check_violations(self,
                                           check_id: str) -> list[ViolationFoundOut]:
        current_check_violations = [
            violation
            for violation in self.violations_found_out_objects
            if await self.is_check_violation(violation)
        ]
        result = await self.get_sorted_violations(current_check_violations)
        # result = await self.get_sorted_violations(
        #     list(filter(self.is_check_violation, self.violations_found_out_objects))
        # )
        result_ = [el for el in result if el.check_id == check_id]
        return result_

    async def all_violations_pending_start(self) -> Reply | None:
        pending_violations_found = await self.get_pending_violations()
        if not pending_violations_found:
            return None
        result = await self.form_reply(
            violations_out=pending_violations_found,
            order=0,
            is_pending=True
        )
        return result

    async def all_violations_check_start(self) -> Reply | None:
        check_violations = await self.get_check_violations()
        if not check_violations:
            return None
        result = await self.form_reply(
            violations_out=check_violations,
            order=0,
            is_pending=False
        )
        return result

    async def all_violations_task_start(self) -> Reply | None:
        violations_out = await self.get_task_violations()
        if not violations_out:
            return None
        result = await self.form_reply(
            violations_out=await self.get_task_violations(),
            order=0,
            is_pending=False
        )
        return result

    async def form_reply(self,
                         violations_out: list[ViolationFoundOut],
                         order: int,
                         is_pending: bool) -> Reply:
        if is_pending:
            text_mes_func = violations_out[order].violation_card_pending
            kb_func = MoPerformerKeyboards().get_violation_pending_menu
        else:
            text_mes_func = violations_out[order].violation_card
            kb_func = MoPerformerKeyboards().get_violation_menu

        photo_id = violations_out[order].photo_id_mfc[0] if violations_out[order].photo_id_mfc else None  # type: ignore
        text_mes = text_mes_func()
        prev_order = order - 1
        next_order = order + 1
        keyboard = await kb_func(
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

    async def get_index_violation_found(self,
                                        violation_found_out: ViolationFoundOut) -> Optional[int]:
        # получаем индекс нарушения в отсортированном списке нарушений
        violation_found_out_lst = await self.get_violation_found_out_objects(
            violation_found_out=violation_found_out
        )
        if not violation_found_out_lst:
            return None
        for index, obj in enumerate(violation_found_out_lst):
            if obj.violation_found_id == violation_found_out.violation_found_id:
                return index
        return None

    async def _get_index_violation_found(self,
                                         violation_found_out_lst: list[ViolationFoundOut],
                                         violation_found_id: str) -> int:
        for index, obj in enumerate(violation_found_out_lst):
            if obj.violation_found_id == violation_found_id:
                return index
        return 0

    async def get_violation_found_out_objects(self,
                                              violation_found_out: ViolationFoundOut
                                              ) -> Optional[list[ViolationFoundOut]]:
        is_task = violation_found_out.is_task
        is_pending = violation_found_out.is_pending

        if is_pending:
            violation_found_out_lst = await self.get_pending_violations()
        elif is_task:
            violation_found_out_lst = await self.get_task_violations()
        else:  # is_check_violation
            violation_found_out_lst = await self.get_check_violations()

        if not violation_found_out_lst:
            return None

        return violation_found_out_lst

    async def get_pending_process(self,
                                  order: int,
                                  violation_found_out: ViolationFoundOut
                                  ):

        violation_found_out_lst = await self.get_violation_found_out_objects(
            violation_found_out=violation_found_out
        )

        if not violation_found_out_lst:
            return None

        reply_obj = await self.form_reply(
            violations_out=violation_found_out_lst,
            order=order if order <= (len(violation_found_out_lst) - 1) else 0,
            is_pending=False
        )
        return reply_obj

    async def get_next_prev_reply(self,
                                  violation_found_out: ViolationFoundOut,
                                  ) -> Optional[Reply]:
        violations_found_out_lst = await self.get_violation_found_out_objects(
            violation_found_out=violation_found_out,
        )
        if not violations_found_out_lst:
            return None

        if len(violations_found_out_lst) == 1:
            return None

        order = await self._get_index_violation_found(
            violation_found_out_lst=violations_found_out_lst,
            violation_found_id=violation_found_out.violation_found_id
        )
        reply_obj = await self.form_reply(
            violations_out=violations_found_out_lst,
            order=order,
            is_pending=violation_found_out.is_pending
        )

        return reply_obj

    async def cancel_process(self,
                             violation_found_out: ViolationFoundOut,
                             ):
        is_pending = violation_found_out.is_pending
        is_task = violation_found_out.is_task

        if is_pending:
            violation_found_out_lst = await self.get_pending_violations()

        elif is_task:
            violation_found_out_lst = await self.get_task_violations()

        else:
            violation_found_out_lst = await self.get_check_violations()

        if len(violation_found_out_lst) == 0:
            return None

        order = await self._get_index_violation_found(
            violation_found_out_lst=violation_found_out_lst,
            violation_found_id=violation_found_out.violation_found_id
        )
        reply_obj = await self.form_reply(
            violations_out=violation_found_out_lst,
            order=order,
            is_pending=violation_found_out.is_pending
        )

        return reply_obj
