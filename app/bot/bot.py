from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

from app.bot.middleware import DBMiddleware

load_dotenv()

bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
dp.update.middleware(DBMiddleware())