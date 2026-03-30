import logging

from app.db import crud

logger = logging.getLogger(__name__)

async def get_budget_by_user_category_id(user_category_id):
    logger.info("DB request get budget by user_category_id=%s", user_category_id)
    budget = await crud.get_budget_by_user_category_id(user_category_id)
    logger.info("DB successful response get budget by user_category_id=%s", user_category_id)
    return budget