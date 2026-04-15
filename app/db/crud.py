from sqlalchemy import select, delete, cast, Date, func, extract
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
from unicodedata import category
from datetime import datetime

from app.db.models import User, BankAccount, BankOperation, Type_Operation, Category, UserCategory, Budget, \
    CategoryAliases
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


async def create_bank_account(user_id: int, name: str, is_default: bool):
    async with async_session() as session:
        account = BankAccount(user_id=user_id, name=name, is_default=is_default)
        session.add(account)

        await session.commit()
        await session.refresh(account)
        return account


async def get_bank_account(id: int):
    async with async_session() as session:
        account = await session.execute(
            select(BankAccount).options(selectinload(BankAccount.user)).where(BankAccount.id == id)
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
            select(BankAccount).join(User).where(User.telegram_id == telegram_user_id).order_by(BankAccount.create_at)
        )

    return accounts.scalars().all()

async def get_bank_accounts_by_user_id(user_id: int):
    async with async_session() as session:
        accounts = await session.execute(
            select(BankAccount).where(BankAccount.user_id == user_id)
        )

        return accounts.scalars().all()

async def get_default_bank_account_by_user_id(user_id: int):
    async with async_session() as session:
        account = await session.execute(
            select(BankAccount).options(selectinload(BankAccount.user)).where(BankAccount.user_id == user_id, BankAccount.is_default == True)
        )

        return account.scalar_one_or_none()

async def update_bank_account(id: int, name: str = None, balance: float = None, is_default: bool = None):
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

        if not is_default is None:
            account.is_default = is_default

        await session.commit()
        await session.refresh(account)
        return account

async def delete_bank_account(account_id: int):
    async with async_session() as session:
        await session.execute(
            delete(BankAccount).where(BankAccount.id == account_id)
        )
        await session.commit()


async def create_bank_operation(
        account_id: int,
        type: Type_Operation,
        amount: float,
        balance_after: float,
        category: int
):
    async with async_session() as session:
        operation = BankOperation(account_id=account_id, type=type, amount=amount, balance_after=balance_after, category=category)

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

async def get_operation_by_date(date: datetime):
    async with async_session() as session:
        operations = await session.execute(
            select(BankOperation).where(
                cast(BankOperation.create_at, Date) == date.date()
            )
        )
        return operations.scalars().all()

async def get_total_operation_by_user_category(user_category_id: int):
    async with async_session() as session:
        result_uc = await session.execute(
            select(UserCategory).where(UserCategory.id == user_category_id)
        )
        user_category = result_uc.scalar_one_or_none()
        if not user_category:
            return None

        now = datetime.utcnow()

        result = await session.execute(
            select(func.sum(BankOperation.amount)).join(
                BankAccount, BankAccount.id == BankOperation.account_id
            ).where(
                BankAccount.user_id == user_category.user_id,
                BankOperation.category == user_category.category_id,
                extract("year", BankOperation.create_at) == now.year,
                extract("month", BankOperation.create_at) == now.month,
                BankOperation.type == Type_Operation.EXPENSE
            )
        )

        total = result.scalar()
        if total is not None:
            return total
        else:
            return 0

async def update_operation(id: int, type: Type_Operation = None, amount: float = None, balance_after: float = None,
                           description: str = None, category: str = None):
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


async def delete_bank_operation(id: int):
    async with async_session() as session:
        await session.execute(
            delete(BankOperation).where(BankOperation.id == id)
        )
        await session.commit()

async def create_category(name: str):
    async with async_session() as session:
        category = Category(name=name)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category


async def get_category(id: int):
    async with async_session() as session:
        category = await session.execute(
            select(Category).where(Category.id == id)
        )

        return category.scalar_one_or_none()


async def get_categories_all():
    async with async_session() as session:
        categories = await session.execute(
            select(Category)
        )

        return categories.scalars().all()


async def get_categories_all_by_user_id(user_id: int):
    async with async_session() as session:
        categories = await session.execute(
            select(Category).join(UserCategory).where(UserCategory.user_id == user_id)
        )

        return categories.scalars().all()



async def create_user_category(user_id, category_id):
    async with async_session() as session:
        user_category = UserCategory(user_id=user_id, category_id=category_id)
        session.add(user_category)
        await session.commit()
        await session.refresh(user_category)
        return user_category


async def get_user_category(id: int):
    async with async_session() as session:
        user_category = await session.execute(
            select(UserCategory).where(UserCategory.id == id)
        )

        return user_category.scalar_one_or_none()


async def get_user_categories_by_user_id(user_id: int):
    async with async_session() as session:
        user_categories = await session.execute(
            select(UserCategory).where(UserCategory.user_id == user_id)
        )

        return user_categories.scalars().all()

async def get_user_category_by_user_id_and_category_id(user_id: int, category_id: int):
    async with async_session() as session:
        user_category = await session.execute(
            select(UserCategory).where(UserCategory.user_id == user_id, UserCategory.category_id == category_id)
        )

        return user_category.scalar_one_or_none()


async def get_user_categories_by_telegram_user_id(telegram_user_id: int):
    async with async_session() as session:
        user_categories = await session.execute(
            select(UserCategory).join(User).where(User.telegram_id == telegram_user_id)
        )

        return user_categories.scalars().all()


async def delete_user_category(user_id: int, category_id: int):
    async with async_session() as session:
        await session.execute(
            delete(UserCategory).where(
                UserCategory.user_id == user_id,
                UserCategory.category_id == category_id
            )
        )

        await session.commit()


async def upsert_budget(user_category_id: int, amount: float, spend: float, year: int, month: int):
    async with async_session() as session:
        stmt = insert(Budget).values(
            user_category_id=user_category_id,
            amount=amount,
            spend=spend,
            year=year,
            month=month
        )

        stmt = stmt.on_conflict_do_update(
            constraint = "uniq_budget_period",
            set_={"amount": amount},
        ).returning(Budget)

        result = await session.execute(stmt)
        budget = result.scalar_one()
        await session.commit()
        return budget

async def upsert_budget_for_update_new_month(user_category_id: int, amount: float, spend: float, year: int, month: int):
    async with async_session() as session:
        stmt = insert(Budget).values(
            user_category_id=user_category_id,
            amount=amount,
            spend=spend,
            year=year,
            month=month
        )

        stmt = stmt.on_conflict_do_nothing(
            constraint = "uniq_budget_period",
        ).returning(Budget)

        result = await session.execute(stmt)
        budget = result.scalar_one_or_none()
        await session.commit()
        return budget

async def get_budget_by_user_category_id_to_date(year: int, month: int, user_category_id: int):
    async with async_session() as session:
        budgets = await session.execute(
            select(Budget).where(
                (Budget.user_category_id == user_category_id),
                (Budget.year==year),
                (Budget.month==month)
            )
        )
        return budgets.scalars().all()

async def get_budget_to_date(year: int, month: int):
    async with async_session() as session:
        budgets = await session.execute(
            select(Budget).where(
                (Budget.year==year),
                (Budget.month==month)
            )
        )
        return budgets.scalars().all()

async def edit_budget(budget_id: int, amount: float):
    async with async_session() as session:
        budget = await session.execute(
            select(Budget).where(Budget.id == budget_id)
        )
        budget = budget.scalar_one_or_none()

        if not budget:
            return None

        budget.amount = amount
        await session.commit()
        await session.refresh(budget)
        return budget

async def edit_budget_add_spend(budget_id: int, spend: float):
    async with async_session() as session:
        result_b = await session.execute(
            select(Budget).where(Budget.id == budget_id)
        )
        budget = result_b.scalar_one_or_none()
        if not budget:
            return None

        budget.spend += spend
        await session.commit()
        await session.refresh(budget)
        return budget

async def delete_budget(budget_id: int):
    async with async_session() as session:
        await session.execute(
            delete(Budget).where(Budget.id == budget_id)
        )
        await session.commit()


async def create_category_aliases(user_id: int, category_id: int, key_word: str):
    async with async_session() as session:
        category_aliases = CategoryAliases(user_id=user_id, category_id=category_id, key_word=key_word)
        session.add(category_aliases)
        await session.commit()
        await session.refresh(category_aliases)
        return category_aliases

async def get_category_aliases_by_key_word_and_user_id(user_id: int, key_word: str):
    async with async_session() as session:
        category_aliases = await session.execute(
            select(CategoryAliases).where(CategoryAliases.key_word == key_word, CategoryAliases.user_id == user_id)
        )

        return category_aliases.scalar_one_or_none()