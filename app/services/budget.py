import logging
from datetime import datetime

from app.db import crud

logger = logging.getLogger(__name__)

async def get_budget_by_user_category_id_now(user_category_id):
    now = datetime.now()
    year = now.year
    month = now.month

    logger.info("DB request get budget by user_category_id=%s", user_category_id)
    budgets = await crud.get_budget_by_user_category_id_now(year, month, user_category_id)
    logger.info("DB successful response get budget by user_category_id=%s", user_category_id)
    if len(budgets) == 0:
        return None
    return budgets[0]

async def create_budget(user_category_id: int, amount: float):
    now = datetime.now()
    year = now.year
    month = now.month

    logger.info("DB request create budget user_category_id=%s year=%s month=%s", user_category_id, year, month)
    await crud.upsert_budget(user_category_id, amount, year, month)
    logger.info("DB successful response create budget user_category_id=%s year=%s month=%s", user_category_id, year, month)