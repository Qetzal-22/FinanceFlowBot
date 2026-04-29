from aiogram.fsm.middleware import BaseMiddleware
from app.db.database import async_session
from aiogram.types import Message, CallbackQuery, Update
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
        logger.info("ENTER IN MIDDLEWARE CHECK REGISTER")
        user = getattr(event, "user", None)
        logger.info("MIDDLEWARE - user=%s", user)
        if not user:
            return await handler(event, data)

        logger.info("AuthMiddleware user.id=%s", user.id)
        if not await check_register(user.id):
            message = None
            callback = None
            if isinstance(event, Update):
                message = event.message
                callback = event.callback_query
            logger.info("MIDDLEWARE - user dont register type_event=%s", type(event))
            if message:
                logger.info("MIDDLEWARE - type_event=Message event.text=%s", message.text)
                if message.text.startswith("/start"):
                    logger.info("MIDDLEWARE - user typing=/start")
                    return await handler(event, data)
                await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
            elif callback:
                await callback.message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
            logger.info("Middleware user not register - block handler")
            return

        return await handler(event, data)