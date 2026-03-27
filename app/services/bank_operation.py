from unicodedata import category
import logging
from datetime import datetime

from app.db import crud
from app.db.models import Type_Operation, BankOperation

logger = logging.getLogger(__name__)

async def create_operation(account_id: int, type_operation: Type_Operation, amount: float, description: str, category: str = None):
    account = await crud.get_bank_account(account_id)
    balance = account.balance
    logger.info("create_operation balance=%s amount=%s type_operation=%s", balance, amount, type_operation)
    if type_operation == Type_Operation.INCOME:
        balance_after = balance + amount
    else:
        balance_after = balance - amount
    logger.info("create_operation balance_after=%s", balance_after)
    await crud.update_bank_account(account_id, balance=balance_after)
    await crud.create_bank_operation(account_id, type_operation, amount, balance_after, description, category)

async def get_bank_operation_by_date(date: datetime) -> list[BankOperation]:
    logger.info("DB request get bank operations by date date=%s", date)
    bank_operations = await crud.get_operation_by_date(date)
    logger.info("DB successful response get bank operation by date date=%s", date)
    return bank_operations