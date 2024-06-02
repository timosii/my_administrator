from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.handlers import default, dev
from app.handlers.admin import admin
from app.handlers.user.mo_part import mo_controler, mo_performer
from app.handlers.user.mfc_part import mfc_main, mfc_leader
from aiogram.types import BotCommand
from app.logger_config import Logger
from app.middlewares.logging_errors import ErrorLoggingMiddleware



async def set_main(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Начать взаимодействие'),
    ]
    await bot.set_my_commands(main_menu_commands)
    # bot_info = await bot.get_me()

    # logger.info(f"Name     - {bot_info.full_name}")
    # logger.info(f"Username - @{bot_info.username}")
    # logger.info(f"ID       - {bot_info.id}")

    Logger().start


async def on_shutdown() -> None:
    Logger().stop


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
    dp.update.middleware(ErrorLoggingMiddleware(bot=bot))
    dp.startup.register(set_main)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)

