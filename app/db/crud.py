from sys import winver

from sqlalchemy import select, update
from app.db.models import User, BankAccount, BankOperation
from app.db.database import async_session

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

async def get_user_all():
    async with async_session() as session:
        users = await session.execute(
            select(User)
        )
        return users.scalars().all()

async def update_user_is_active(id: int, is_active: bool):
    async with async_session() as session:
        result = session.execute(
            select(User).where(User.id == id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_active = is_active
        await session.commit()
        await session.refresh(user)
        return user

async def create_bunk_account(user_id: int, name: str):
    async with async_session() as session:
        account = BankAccount(user_id=user_id, name=name)
        session.add(account)

        await session.commit()
        await session.refresh(account)
        return account

async def get_bank_account(id: int):
    async with async_session() as session:
        account = session.execute(
            select(BankAccount).where(BankAccount.id == id)
        )

        return account.scalar_one_or_none

async def get_bank_account_all():
    async with async_session() as session:
        accounts = session.execute(
            select(BankAccount)
        )
        return accounts.scalar().all()

async def update_bank_account(id:int, name: str = None, balance: float = None):
    async with async_session() as session:
        result = session.execute(
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