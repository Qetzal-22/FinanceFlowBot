import logging

from app.db import crud

logger = logging.getLogger(__name__)

async def create_account(user_id: int, name: str):
    logger.info("DB request create bank account user_id=%s", user_id)
    await crud.create_bank_account(user_id, name)
    logger.info("DB successful response create bank account user_id=%s", user_id)
    return True