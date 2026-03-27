from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime, timedelta, date

from app.db.models import BankAccount, Category, UserCategory
from app.db import crud
from app.utils.time import create_new_date


async def register_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Register", callback_data="register")
    return kb.as_markup()

async def create_bank_account_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Create Account", callback_data="create_account")
    return kb.as_markup()

async def main_menu_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Record Transaction")
    kb.button(text="Bank Account")
    kb.button(text="Profile")
    kb.adjust(1, 2)
    return kb.as_markup(resize_keyboard=True)

async def profile_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="My category")
    kb.button(text="View history")
    kb.button(text="Back to menu")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

async def category_menu_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Add category")
    kb.button(text="Remove category")
    kb.button(text="Back to menu")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

async def categories_kb(categories: list[Category]):
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=f"{category.name}", callback_data=f"category_rm:{category.id}")
    kb.adjust(1)
    return kb.as_markup()

async def choose_type_transaction_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Income", callback_data="type_transaction:income")
    kb.button(text="Expense", callback_data="type_transaction:expense")
    return kb.as_markup()

async def main_bank_account_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Create new account")
    kb.button(text="Edit account")
    kb.button(text="Back to menu")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

async def choose_account_kb(accounts: list[BankAccount]):
    kb = InlineKeyboardBuilder()
    for account in accounts:
        kb.button(text=f"{account.name}", callback_data=f"account:{account.id}")
    kb.adjust(1)
    return kb.as_markup()

async def choose_account_for_transaction_kb(accounts: list[BankAccount]):
    kb = InlineKeyboardBuilder()
    for account in accounts:
        kb.button(text=f"{account.name}", callback_data=f"transaction_account:{account.id}")
    kb.adjust(1)
    return kb.as_markup()

async def edit_account_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Record transaction")
    kb.button(text="Rename")
    kb.button(text="Remove")
    kb.button(text="Back to menu")
    kb.adjust(1, 2, 1)
    return kb.as_markup(resize_keyboard=True)

async def add_category_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Add category", callback_data="category_add")
    return kb.as_markup()

async def category_for_transaction_kb(categories: list[Category]):
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=f"{category.name}", callback_data=f"transaction_category:{category.id}")
    kb.adjust(1)
    return kb.as_markup()

async def confirmation_remove_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Remove", callback_data="conf_remove_account:remove")
    kb.button(text="Cancel", callback_data="conf_remove_account:cancel")
    return kb.as_markup()

async def kalendar_kb(date_now: datetime, count_day: int):
    kb = InlineKeyboardBuilder()
    back_date = await create_new_date(date_now, -1)
    next_date = await create_new_date(date_now, +1)
    kb.button(text="Back", callback_data=f"kalendar_move:{back_date.year}_{back_date.month}")
    kb.button(text="Next", callback_data=f"kalendar_move:{next_date.year}_{next_date.month}")
    for i in range(1, 36):
        if i <= count_day:
            kb.button(text=f"{i}", callback_data=f"calendar_day:{i}.{date_now.month}.{date_now.year}")
        else:
            kb.button(text=".", callback_data="stud")
    kb.adjust(2, 7)
    return kb.as_markup()