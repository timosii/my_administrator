from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.handlers import default, dev
from app.handlers.admin import admin
from app.handlers.user.mo_part import mo_performer, mo_controler
from app.handlers.user.mfc_part import mfc_main, mfc_leader


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
    redis = Redis(host='localhost')
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    dp.include_routers(
        admin.router,
        default.router,
        dev.router,
        mfc_leader.router,
        mfc_main.router,
        mo_performer.router,
        mo_controler.router

    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

