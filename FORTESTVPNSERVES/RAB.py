import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from config import API_TOKEN
from database import init_db
from handlers import register_handlers

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация бота
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

if __name__ == '__main__':
    init_db()  # Инициализация базы данных
    register_handlers(dp)  # Регистрация обработчиков
    executor.start_polling(dp, skip_updates=True)