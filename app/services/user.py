from app.db import crud
import logging

logger = logging.getLogger(__name__)

async def create_user(telegram_user_id: int):
    logger.info("DB request create user telegram_user_id=%s", telegram_user_id)
    await crud.create_user(telegram_user_id)
    logger.info("DB successful response create user telegram_user_id=%s", telegram_user_id)
    return True