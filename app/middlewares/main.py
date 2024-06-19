import os
from aiogram import Dispatcher, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery, User
from loguru import logger
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from pprint import pformat
from app.config import settings
from aiogram.exceptions import TelegramAPIError


class ErrorProcessMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.dev_id = settings.DEV_ID
        self.log_file = os.path.join(("logs/debug.log"))
        self.prev_lines_count = 30

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        try:
            return await handler(event, data)
        # except TelegramAPIError as e:
        #     await self.handle_error(event, error_message=f"Telegram API Error: {e}")
        except Exception as e:
            error_message = "Error occurred for user {0} ({1}): {2}".format(
                    user.id, user.username, e)
            logger.error(
                error_message
            )
            with open(self.log_file, "r") as file:
                log_lines = file.readlines()
                prev_lines = "".join(log_lines[-self.prev_lines_count:])

            message = f"#error\n<b>{error_message}</b>\n\nLast {self.prev_lines_count} lines of logs:\n{prev_lines}"

            await self.bot.send_message(self.dev_id, message)
    #         await self.handle_error(event, error_message=f"Telegram API Error: {e}")
    #         # raise e
        
    # async def handle_error(self, event, error_message: str):
    #     if isinstance(event, Message):
    #         await event.answer(error_message)
    #     elif isinstance(event, CallbackQuery):
    #         await event.message.answer(error_message)


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
                
