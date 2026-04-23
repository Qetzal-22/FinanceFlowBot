from aiogram.fsm.middleware import BaseMiddleware
from app.db.database import async_session
from aiogram.types import Message, CallbackQuery
from app.services.user import check_register
from app.bot.keyboard import register_kb

import logging

logger = logging.getLogger(__name__)

class DBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with async_session() as db:
            data["db"] = db
            return await handler(event, data)

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)
        logger.info("AuthMiddleware user.id=%s", user.id)
        if not await check_register(user.id):
            if isinstance(event, Message):
                await event.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
            elif isinstance(event, CallbackQuery):
                await event.message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
            return

        return await handler(event, data)

