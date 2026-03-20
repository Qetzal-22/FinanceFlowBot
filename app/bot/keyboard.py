from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.db.models import BankAccount, Category, UserCategory
from app.db import crud


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
    kb.button(text="Back to menu")
    kb.adjust(1, 1)
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

async def category_for_transaction(categories: list[Category]):
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=f"{category.name}", callback_data=f"transaction_category:{category.id}")
    return kb.as_markup()