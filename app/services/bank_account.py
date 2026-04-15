import logging

from app.db import crud

logger = logging.getLogger(__name__)

async def create_account(user_id: int, name: str):
    bank_account = await crud.get_bank_accounts_by_user_id(user_id)
    if len(bank_account) == 0:
        default = True
    else:
        default = False

    logger.info("DB request create bank account user_id=%s", user_id)
    await crud.create_bank_account(user_id, name, default)
    logger.info("DB successful response create bank account user_id=%s", user_id)
    return True

async def get_bank_accounts(telegram_user_id: int):
    logger.info("DB request get bank account telegram_user_id=%s", telegram_user_id)
    accounts = await crud.get_bank_accounts_by_telegram_id(telegram_user_id)
    logger.info("DB successful response get bank account telegram_user_id=%s", telegram_user_id)

    return accounts

async def update_account(account_id: int, name: str = None, balance: float = None):
    logger.info("DB request update account account_id=%s", account_id)
    await crud.update_bank_account(account_id, name, balance)
    logger.info("DB successful response update account account_id=%s", account_id)


async def delete_account(account_id: int):
    logger.info("DB request delete account account_id=%s", account_id)
    await crud.delete_bank_account(account_id)
    logger.info("DB successful response delete account account_id=%s", account_id)


async def set_default(account_id: int):
    logger.info("DB request get account account_id=%s", account_id)
    account = await crud.get_bank_account(account_id)
    logger.info("DB successful response get account account_id=%s", account_id)
    user = account.user
    accounts = await crud.get_bank_accounts_by_user_id(user.id)

    for a in accounts:
        logger.info("DB request update account account_id=%s", a.id)
        await crud.update_bank_account(a.id, is_default=False)
        logger.info("DB successful response update account account_id=%s", a.id)

    logger.info("DB request update account account_id=%s", account_id)
    await crud.update_bank_account(account_id, is_default=True)
    logger.info("DB successful response update account account_id=%s", account_id)