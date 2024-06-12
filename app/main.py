from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from app.config import settings
from app.handlers import default, dev
from app.handlers.admin import admin
from app.handlers.user.mo_part import mo_controler, mo_performer
from app.handlers.user.mfc_part import mfc_main, mfc_leader
from aiogram.types import BotCommand
from app.middlewares.logging_mw import ErrorLoggingMiddleware, FSMMiddleware
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import nest_asyncio

nest_asyncio.apply()

WEBHOOK_HOST = 'https://ample-infinitely-crow.ngrok-free.app' 
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = 8080


async def set_main(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Начать'),
    ]
    await bot.set_my_commands(main_menu_commands)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info('bot started')


async def on_shutdown(bot: Bot) -> None:
    logger.info('bot stopped')
    # await bot.delete_webhook(drop_pending_updates=True)

@logger.catch
def start_bot() -> None:
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
    # await bot.delete_webhook(drop_pending_updates=True)
    dp.update.middleware(FSMMiddleware())
    dp.update.middleware(ErrorLoggingMiddleware())
    dp.startup.register(set_main)
    dp.shutdown.register(on_shutdown)
    bot = Bot(token=settings.BOT_TOKEN, parse_mode='HTML')
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    
    # await dp.start_polling(bot)