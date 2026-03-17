import asyncio
from aiogram import Bot
from aiogram.filters.command import BotCommand

from app.bot.bot import bot, dp
from app.bot.handler.user import user_router_bot
from app.config.logging_config import setup_logging

from app.db.init_db import init_models

setup_logging()

async def set_commands(bot: Bot):
    command = [
        BotCommand(command="/start", description="Start bot"),
        BotCommand(command="/help", description="Bot Info")
    ]
    await bot.set_my_commands(command)
    return

async def start_bot():
    await init_models()

    await set_commands(bot)
    dp.include_router(user_router_bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())