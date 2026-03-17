import asyncio

from app.bot.bot import bot, dp
from app.bot.handler.user import user_router_bot
from app.config.logging_config import setup_logging

from app.db.init_db import init_models

setup_logging()

async def start_bot():
    await init_models()

    dp.include_router(user_router_bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())