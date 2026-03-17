from aiogram.utils.keyboard import InlineKeyboardBuilder

async def register_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Register", callback_data="register")
    return kb.as_markup()

async def create_bank_account_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Create Account", callback_data="create_account")
    return kb.as_markup()