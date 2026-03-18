import logging

from app.db import crud

logger = logging.getLogger(__name__)

async def create_account(user_id: int, name: str):
    logger.info("DB request create bank account user_id=%s", user_id)
    await crud.create_bank_account(user_id, name)
    logger.info("DB successful response create bank account user_id=%s", user_id)
    return True

async def get_bank_accounts(telegram_user_id: int):
    logger.info("DB request get bank account telegram_user_id=%s", telegram_user_id)
    accounts = await crud.get_bank_accounts_by_telegram_id(telegram_user_id)
    logger.info("DB successful response get bank account telegram_user_id=%s", telegram_user_id)

    return accounts