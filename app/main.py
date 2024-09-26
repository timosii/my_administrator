from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from loguru import logger

from app.config import settings
from app.database.repositories.cache_config import caches
from app.handlers import additional, dev
from app.handlers.admin import admin, authorization
from app.handlers.user.avail import mfc_avail
from app.handlers.user.common import vacation_logic
from app.handlers.user.mfc_part import mfc_leader, mfc_main
from app.handlers.user.mo_part import (
    mo_controler,
    mo_performer,
    pending_process,
    take_process,
)
from app.handlers.user.vacation import vacation
from app.middlewares.main import ErrorProcessMiddleware, FSMMiddleware

WEBHOOK_HOST = settings.WEBHOOK_HOST
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = settings.NGROK_HOST
WEBAPP_PORT = 8080


async def set_main(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Начать'),
        BotCommand(command='/docs',
                   description='Документация'),
        BotCommand(command='/feedback',
                   description='Обратная связь'),
        BotCommand(command='/changelog',
                   description='Что нового?')
    ]
    await bot.set_my_commands(main_menu_commands)
    if not settings.IS_TEST:
        await bot.set_webhook(WEBHOOK_URL)
    logger.info('bot started')
    await bot.send_message(settings.DEV_ID, 'Bot is started!')


async def on_shutdown(bot: Bot) -> None:
    logger.info('bot stopped')
    cache = caches.get('default')
    await cache.close()
    await bot.send_message(settings.DEV_ID, 'Bot is stopped!')


def all_register():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    redis = Redis(host=settings.REDIS_HOST)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    dp.include_routers(
        admin.router,
        additional.router,
        dev.router,
        vacation.router,
        vacation_logic.router,
        mfc_avail.router,
        mfc_leader.router,
        mfc_main.router,
        pending_process.router,
        take_process.router,
        mo_performer.router,
        mo_controler.router,
        authorization.router
    )
    dp.update.middleware(FSMMiddleware())
    dp.update.middleware(ErrorProcessMiddleware(bot=bot))
    dp.startup.register(set_main)
    dp.shutdown.register(on_shutdown)
    return bot, dp


@logger.catch
def start_bot() -> None:
    bot, dp = all_register()
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
    bot, dp = all_register()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
