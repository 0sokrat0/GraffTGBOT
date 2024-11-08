import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

from core.config_data.config import load_config
from core.dialogs.start_dialog import start_dialog
from core.states import StartSG

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(
    level = logging.DEBUG,
    format = '[%(asctime)s] #%(levelname)-8s %(filename)s:'
             '%(lineno)d - %(name)s - %(message)s'
)

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)


async def main() -> None:
    # Загружаем конфигурацию
    config = load_config()

    storage = MemoryStorage()
    bot = Bot(
        token = config.tg_bot.token,
        default = DefaultBotProperties(parse_mode = ParseMode.HTML)
    )
    dp = Dispatcher(storage = storage)

    # Настройка диалогов
    setup_dialogs(dp)
    dp.include_router(start_dialog)

    try:
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == '__main__':
    asyncio.run(main())
