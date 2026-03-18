from unicodedata import category

from app.db import crud
from app.db.models import Type_Operation


async def create_operation(account_id: int, type_operation: Type_Operation, amount: float, description: str, category: str):
    account = await crud.get_bank_account(account_id)
    balance = account.balance
    if type_operation == "income":
        balance_after = balance + amount
    else:
        balance_after = balance - amount

    await crud.create_bank_operation(account_id, type_operation, amount, balance_after, description, category)