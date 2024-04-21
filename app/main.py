from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.handlers.user import mfc_part, mo_part


# async def __on_start_up(dp: Dispatcher) -> None:
#     logger.info('Bot starts')

#     register_models()
#     register_all_filters(dp)
#     register_all_handlers(dp)

    # users = get_users_with_sessions()
    # count = 0

    # if not users:
    #     return

    # for user in users:
    #     with suppress(ChatNotFound, BotBlocked):
    #         if user.session.enable:
    #             start_process_if_sessions_exists(user.telegram_id)
    #         await dp.bot.send_message(user.telegram_id, "Бот обновлен!",
    #                                   reply_markup=get_main_keyboard(user.telegram_id))
    #         count += 1

    # logger.info(f"Было совершено {count} рассылок")


async def start_bot() -> None:
    bot = Bot(token=settings.BOT_TOKEN, parse_mode='HTML')
    # redis = Redis(host='localhost', port=6379)
    # storage = RedisStorage(redis=redis)
    storage = MemoryStorage() # при использовании MemoryStorage
    dp = Dispatcher(storage=storage)
    dp.include_routers(
        mfc_part.router,
        mo_part.router
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
