from aiogram.fsm.middleware import BaseMiddleware
from app.db.database import async_session

class DBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with async_session() as db:
            data["db"] = db
            return await handler(event, data)