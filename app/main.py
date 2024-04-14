from loguru import logger
from aiogram import Bot, Dispatcher, executor
from aiogram.fsm.storage.redis import RedisStorage, Redis
from app.config import settings


async def __on_start_up(dp: Dispatcher) -> None:
    logger.info('Bot starts')

    register_models()
    register_all_filters(dp)
    register_all_handlers(dp)

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



def start_bot() -> None:
    bot = Bot(token=settings.BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=RedisStorage(redis=Redis(host='localhost')))
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)

