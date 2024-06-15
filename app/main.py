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
from aiogram.client.bot import DefaultBotProperties
from aiohttp import web
import asyncio

WEBHOOK_HOST = 'https://ample-infinitely-crow.ngrok-free.app' 
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = settings.NGROK_HOST
WEBAPP_PORT = 8080


async def set_main(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Начать'),
        BotCommand(command='/feedback',
                   description='Обратная связь'),
        BotCommand(command='/changelog',
                   description='Что нового?')
    ]
    await bot.set_my_commands(main_menu_commands)
    if not settings.IS_TEST:
        await bot.set_webhook(WEBHOOK_URL)
    logger.info('bot started')

async def on_shutdown() -> None:
    logger.info('bot stopped')

@logger.catch
def start_bot() -> None:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    redis = Redis(host=settings.REDIS_HOST)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    dp.include_routers(
        admin.router,
        dev.router,
        mfc_leader.router,
        mfc_main.router,
        mo_performer.router,
        mo_controler.router,
        default.router,
    )
    dp.update.middleware(FSMMiddleware())
    dp.update.middleware(ErrorLoggingMiddleware())
    dp.startup.register(set_main)
    dp.shutdown.register(on_shutdown)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

@logger.catch
async def start_local() -> None:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    redis = Redis(host=settings.REDIS_HOST)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    dp.include_routers(
        admin.router,
        dev.router,
        mfc_leader.router,
        mfc_main.router,
        mo_performer.router,
        mo_controler.router,
        default.router,
    )
    await bot.delete_webhook(drop_pending_updates=True)
    dp.update.middleware(FSMMiddleware())
    dp.update.middleware(ErrorLoggingMiddleware())
    dp.startup.register(set_main)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)
