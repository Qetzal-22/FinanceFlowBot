from sqlalchemy import select
from app.db.models import User, BankAccount, BankOperation, Type_Operation
from app.db.database import async_session

import asyncio

async def create_user(telegram_id: int):
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id
        )
        session.add(user)

        await session.commit()
        await session.refresh(user)
        return user

async def get_user(id: int):
    async with async_session() as session:
        user = await session.execute(
            select(User).where(User.id == id)
        )

        return user.scalar_one_or_none()

async def get_user_by_telegram_id(telegram_id: int):
    async with async_session() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )

        return user.scalar_one_or_none()

async def get_user_all():
    async with async_session() as session:
        users = await session.execute(
            select(User)
        )
        return users.scalars().all()

async def update_user_is_active(id: int, is_active: bool):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_active = is_active
        await session.commit()
        await session.refresh(user)
        return user

async def create_bank_account(user_id: int, name: str):
    async with async_session() as session:
        account = BankAccount(user_id=user_id, name=name)
        session.add(account)

        await session.commit()
        await session.refresh(account)
        return account

async def get_bank_account(id: int):
    async with async_session() as session:
        account = await session.execute(
            select(BankAccount).where(BankAccount.id == id)
        )

        return account.scalar_one_or_none()

async def get_bank_account_all():
    async with async_session() as session:
        accounts = await session.execute(
            select(BankAccount)
        )
        return accounts.scalars().all()

async def get_bank_accounts_by_telegram_id(telegram_user_id: int):
    async with async_session() as session:
        accounts = await session.execute(
            select(BankAccount).join(User).where(User.telegram_id==telegram_user_id)
        )

    return accounts.scalars().all()


async def update_bank_account(id:int, name: str = None, balance: float = None):
    async with async_session() as session:
        result = await session.execute(
            select(BankAccount).where(BankAccount.id == id)
        )
        account = result.scalar_one_or_none()
        if not account:
            return None

        if name:
            account.name = name

        if balance:
            account.balance = balance

        await session.commit()
        await session.refresh(account)
        return account

async def create_bank_operation(
                                account_id: int,
                                type: Type_Operation,
                                amount: float,
                                balance_after: float,
                                description: str,
                                category: str
                                ):
    async with async_session() as session:
        operation = BankOperation(account_id=account_id, type=type, amount=amount, description=description, category=category)

        session.add(operation)
        await session.commit()
        await session.refresh(operation)
        return operation

async def get_operation(id: int):
    async with async_session() as session:
        operation = await session.execute(
            select(BankOperation).where(BankOperation.id == id)
        )

        return operation.scalar_one_or_none()

async def get_operation_all():
    async with async_session() as session:
        operations = await session.execute(
            select(BankOperation)
        )

        return operations.scalars().all()

async def update_operation(id: int, type: Type_Operation = None, amount: float = None, balance_after: float = None, description: str = None, category: str = None):
    async with async_session() as session:
        result = await session.execute(
            select(BankOperation).where(BankOperation.id == id)
        )

        operation = result.scalar_one_or_none()
        if not operation:
            return None

        if type:
            operation.type = type

        if amount:
            operation.amount = amount

        if description:
            operation.description = description

        if category:
            operation.category = category

        if balance_after:
            operation.balance_after = balance_after

        await session.commit()
        await session.refresh(operation)
        return operation