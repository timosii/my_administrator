import os
from pprint import pformat
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramServerError,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message, TelegramObject, User
from loguru import logger

from app.config import settings
from app.handlers.messages import ErrorMessages


class ErrorProcessMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.dev_id = settings.DEV_ID
        self.log_file = os.path.join('logs/debug.log')
        self.prev_lines_count = 10

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User = data.get('event_from_user')
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            await self.send_message_dev(text='TelegramBadRequest ERROR!')
            await self.error_process(user=user, e=e)
            await self.handle_error(update=event, error_message=ErrorMessages.bad_request)

        except TelegramNetworkError as e:
            await self.send_message_dev(text='TelegramNetworkError ERROR!')
            await self.error_process(user=user, e=e)
            await self.handle_error(update=event, error_message=ErrorMessages.network_error)

        except TelegramServerError as e:
            await self.send_message_dev(text='TelegramServerError ERROR!')
            await self.error_process(user=user, e=e)
            await self.handle_error(update=event, error_message=ErrorMessages.server_error)

        except TelegramAPIError as e:
            await self.send_message_dev(text='Another TelegramAPIError ERROR!')
            await self.error_process(user=user, e=e)
            await self.handle_error(update=event, error_message=ErrorMessages.tg_error)

        except AttributeError as e:
            await self.send_message_dev(text='Attribute ERROR!')
            await self.error_process(user=user, e=e)
            if "'NoneType' object has no attribute" in str(e):
                await self.handle_error(update=event, error_message=ErrorMessages.attribute_error_process)
            else:
                await self.send_message_dev(text='Неизвестная ошибка AttributeError, обрати внимание')
                raise e

        except Exception as e:
            await self.send_message_dev(text='Another ERROR!')
            await self.error_process(user=user, e=e)
            await self.send_message_dev(text='!!Необрабатываемая ошибка!!')
            raise e

    async def error_process(self, user: User, e: Exception):
        error_text = await self._form_error_message(user=user, e=e)
        await self.send_message_dev(text=error_text)

    async def _form_error_message(self, user: User, e: Exception):
        error_message = 'Error occurred for user {} ({}): {}'.format(
            user.id, user.username, e
        )
        logger.error(
            error_message
        )
        with open(self.log_file) as file:
            log_lines = file.readlines()
            prev_lines = ''.join(log_lines[-self.prev_lines_count:])

        message = f'#error\n<b>{error_message}</b>\n\nLast {self.prev_lines_count} lines of logs:\n{prev_lines}'
        return message

    async def send_message_dev(self, text: str):
        await self.bot.send_message(self.dev_id, text=text)

    async def handle_error(self,
                           update,
                           error_message: str):
        if isinstance(update.event, Message):
            await update.event.answer(error_message)
        elif isinstance(update.event, CallbackQuery):
            await update.event.answer(error_message, show_alert=True)
        else:
            await self.send_message_dev(text=f'Получил ошибку и необрабатываемый тип апдейта: {type(update.event)}')
            return


class FSMMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        fsm_context: FSMContext = data.get('state')
        user: User = data.get('event_from_user')

        if fsm_context:
            current_state: State = await fsm_context.get_state()
            logger.info(f'User: {user.id} Current state: {current_state}')

            result = await handler(event, data)

            new_state: State = await fsm_context.get_state()
            state_data: dict = await fsm_context.get_data()

            logger.info(f'User: {user.id} State changed to: {new_state}')
            logger.info(f'User: {user.id} FSM data:\n{pformat(state_data)}')

            return result

        return await handler(event, data)
