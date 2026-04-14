import logging
from datetime import datetime, timedelta

from app.db import crud

logger = logging.getLogger(__name__)


async def get_budget_by_user_category_id_now(user_category_id):
    now = datetime.now()
    year = now.year
    month = now.month

    logger.info("DB request get budget by user_category_id=%s", user_category_id)
    budgets = await crud.get_budget_by_user_category_id_to_date(year, month, user_category_id)
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
    logger.info(
        "DB successful response create budget user_category_id=%s year=%s month=%s",
        user_category_id,
        year,
        month
    )


async def update_budget_new_month():
    now = datetime.now()
    year = now.year
    month = now.month

    if month == 1:
        last_month = 12
        last_year = year - 1
    else:
        last_month = month - 1
        last_year = year

    logger.info("DB request get budgets to date year=%s month=%s", last_year, last_month)
    budgets_last_month = await crud.get_budget_to_date(last_year, last_month)
    logger.info("DB successful response get budgets to date year=%s month=%s", last_year, last_month)

    for budget_last_month in budgets_last_month:
        await create_budget(budget_last_month.user_category_id, budget_last_month.amount)

async def edit_budget(user_category_id: int, amount: float) -> None:
    now = datetime.now()
    year = now.year
    month = now.month

    budget_id = (await crud.get_budget_by_user_category_id_to_date(year, month, user_category_id))[0].id
    await crud.edit_budget(budget_id, amount)

async def remove_budget(user_category_id: int) -> None:
    now = datetime.now()
    year = now.year
    month = now.month

    budget_id = (await crud.get_budget_by_user_category_id_to_date(year, month, user_category_id))[0].id
    logger.info("remove budget budget_id=%s", budget_id)

    await crud.delete_budget(budget_id)