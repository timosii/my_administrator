from aiogram import Dispatcher
from aiogram.types import TelegramObject, Message, CallbackQuery, User
from loguru import logger
from typing import Callable, Dict, Any, Awaitable
import logging
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from pprint import pformat


class ErrorLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(
                "Error occurred for user {0} ({1}): {2}".format(
                    user.id, user.username, e
                )
            )
            raise e


class FSMMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        fsm_context: FSMContext = data.get("state")
        user: User = data.get("event_from_user")

        if fsm_context:
            current_state: State = await fsm_context.get_state()
            logger.info(f"User: {user.id} Current state: {current_state}")

            result = await handler(event, data)

            new_state: State = await fsm_context.get_state()
            state_data: dict = await fsm_context.get_data()

            logger.info(f"User: {user.id} State changed to: {new_state}")
            logger.info(f"User: {user.id} FSM data:\n{pformat(state_data)}")

            return result

        return await handler(event, data)


# class UnexpectedBehaviorMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any],
#     ) -> Any:
#         result = await handler(event, data)
#         if not result:
#             if isinstance(event, CallbackQuery):
#                 event.answer(text='Сейчас не лучшее время для этого ...')
#             if isinstance(event, Message):
#                 event.answer(text='Что-то пошло не так. Попробуйте ещё раз или начните сначала /start')
#         return result
                
