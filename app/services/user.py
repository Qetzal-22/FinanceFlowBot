from app.db import crud
import logging
from datetime import datetime
from app.db.models import UserCategory

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

async def get_categories(telegram_user_id):
    logger.info("DB request get user telegram_user_id=%s", telegram_user_id)
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    logger.info("DB successful response get user telegram_user_id=%s", telegram_user_id)
    user_id = user.id

    logger.info("DB request get categoty telegram_user_id=%s", telegram_user_id)
    categories = await crud.get_categories_all_by_user_id(user_id)
    logger.info("DB successful response get categoty telegram_user_id=%s", telegram_user_id)
    return categories

async def get_user_id(telegram_user_id: int):
    logger.info("DB request get user telegram_user_id=%s", telegram_user_id)
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    logger.info("DB successful response get user telegram_user_id=%s", telegram_user_id)
    return user.id

async def create_user_category(telegram_user_id, category_id):
    logger.info("DB request get user telegram_user_id=%s", telegram_user_id)
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    logger.info("DB successful response get user telegram_user_id=%s", telegram_user_id)
    user_id = user.id

    logger.info("DB request create user_category telegram_user_id=%s category_id=%S", telegram_user_id, category_id)
    await crud.create_user_category(user_id, category_id)
    logger.info("DB successful response create user_category telegram_user_id=%s category_id=%S", telegram_user_id, category_id)

async def create_category(name: str):
    logger.info("DB request create category name=%s", name)
    category = await crud.create_category(name)
    logger.info("DB successful response create category name=%s", name)
    return category


async def delete_category(telegram_user_id: int, category_id: int):
    logger.info("DB request get user telegram_user_id=%s", telegram_user_id)
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    logger.info("DB successful response get user telegram_user_id=%s", telegram_user_id)
    user_id = user.id

    logger.info("DB request delete user category user_id=%s category_id=%s", user_id, category_id)
    await crud.delete_user_category(user_id, category_id)
    logger.info("DB successful delete user category user_id=%s category_id=%s", user_id, category_id)

async def get_user_categories_by_telegram_id(telegram_user_id: int):
    logger.info("DB request get user_categories by telegram_user_id=%s", telegram_user_id)
    user_categories = await crud.get_user_categories_by_telegram_user_id(telegram_user_id)
    logger.info("DB successful response get user_categories by telegram_user_id=%s", telegram_user_id)
    return user_categories

async def get_category(category_id: int):
    logger.info("DB request get category category_id=%s", category_id)
    category = await crud.get_category(category_id)
    logger.info("DB successful response get category category_id=%s", category_id)
    return category

async def get_category_with_budget(telegram_user_id: int) -> list[UserCategory]:
    user_id = (await crud.get_user_by_telegram_id(telegram_user_id)).id

    now = datetime.now()
    year = now.year
    month = now.month

    logger.info("DB request get category_with_budget telegram_user_id=%s", telegram_user_id)
    user_categories = await crud.get_user_categories_by_user_id(user_id)

    categories_with_budget = []

    for user_category in user_categories:

        user_category_id = user_category.id
        budget = await crud.get_budget_by_user_category_id_to_date(year, month, user_category_id)

        if budget:
            categories_with_budget.append(user_category)

    return categories_with_budget