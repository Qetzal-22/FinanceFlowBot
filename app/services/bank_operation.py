import logging
from datetime import datetime

from app.services.budget import get_budget_by_user_category_id_now, check_overflow_budget
from app.db import crud
from app.db.models import Type_Operation, BankOperation

logger = logging.getLogger(__name__)

async def create_operation(user_id: int, type_operation: Type_Operation, amount: float, category_id: int = None, account_id: int = None):
    if not account_id:
        account = await crud.get_default_bank_account_by_user_id(user_id)
    else:
        account = await crud.get_bank_account(account_id)

    user = account.user
    logger.info("create_operation user_id=%s, category_id=%s", user.id, category_id)
    user_category = await crud.get_user_category_by_user_id_and_category_id(user.id, category_id)
    balance = account.balance

    logger.info("create_operation balance=%s amount=%s type_operation=%s", balance, amount, type_operation)
    if type_operation == Type_Operation.INCOME:
        balance_after = balance + amount
        event = None
    else:
        balance_after = balance + amount # когда type_operation == Type_Operation.EXPENSE то amount<0 => чтоб уменишть баланс нужно balance + amount
        budget = await get_budget_by_user_category_id_now(user_category.id)
        if not budget is None:
            await crud.edit_budget_add_spend(budget.id, (amount*-1))
            event = await check_overflow_budget(budget.amount, budget.spend-amount) # потраченные деньги в бюджете должны увеличиватся, поэтому spend - -amount (amount<0)
        else:
            event = None

    logger.info("create_operation balance_after=%s", balance_after)
    await crud.update_bank_account(account.id, balance=balance_after)
    operation = await crud.create_bank_operation(account.id, type_operation, amount, balance_after, category_id)

    return operation, event

async def get_bank_operation_by_date(date: datetime) -> list[BankOperation]:
    logger.info("DB request get bank operations by date date=%s", date)
    bank_operations = await crud.get_operation_by_date(date)
    logger.info("DB successful response get bank operation by date date=%s", date)
    return bank_operations

async def add_description_for_operation(operation_id: int, description: str) -> None:
    await crud.update_operation(operation_id, description=description)

async def delete_operation(operation_id: int) -> None:
    await crud.delete_bank_operation(operation_id)