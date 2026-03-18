from app.db import crud
import logging


logger = logging.getLogger(__name__)

async def create_user(telegram_user_id: int):
    logger.info("DB request create user telegram_user_id=%s", telegram_user_id)
    await crud.create_user(telegram_user_id)
    logger.info("DB successful response create user telegram_user_id=%s", telegram_user_id)
    return True

async def check_register(telegram_user_id: int) -> bool:
    """True - is register | False - isn`t register"""
    logger.info("DB request get user telegram_user_id=%s", telegram_user_id)
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    logger.info("DB successful response get user telegram_user_id=%s", telegram_user_id)
    if not user:
        return False
    return True

async def get_user_categories(telegram_user_id):
    logger.info("DB request get categoty telegram_user_id=%s", telegram_user_id)
    categories = crud.get_user_categories_by_telegram_user_id(telegram_user_id)
    logger.info("DB successful response get categoty telegram_user_id=%s", telegram_user_id)
    return categories