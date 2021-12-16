import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config_reader import load_config
from app.handlers.admin import register_hendler_admin
from app.handlers.cmd import register_handlers_cmd
from app.handlers.subscriber import register_handlers_subscriber
from app.handlers.day import register_handlers_day
from app.handlers.week import register_handlers_week
from app.handlers.settings import register_handlers_settings
from app.handlers.link import register_handlers_link
from app.handlers.moderator import register_handlers_moderator

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/day", description="розклад на сьогодні"),
        BotCommand(command="/week", description="розклад на тиждень"),
        BotCommand(command="/settings", description="налаштування"),
        BotCommand(command="/change_group", description="змінити групу"),
        BotCommand(command="/help", description="інформація щодо користування"),
    ]
    await bot.set_my_commands(commands)


async def main():
    # Налаштування логування у stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Парсинг файлу конфігурації
    config = load_config("config/bot.ini")

    # Оголошення та ініціалізація об'єктів бота та диспетчера
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Реєстрація хендлерів
    register_handlers_cmd(dp)
    register_handlers_day(dp)
    register_handlers_week(dp)
    register_hendler_admin(dp, config.tg_bot.admin_id)
    register_handlers_settings(dp)
    register_handlers_link(dp)
    register_handlers_moderator(dp)
    register_handlers_subscriber(dp)

    # Встановлення команд бота
    await set_commands(bot)

    # Запуск полінгу
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
