from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.db.models import BankAccount, Category


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
    return kb.as_markup(resize_keyboard=True)

