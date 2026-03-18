from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.keyboard import register_kb
from app.bot.static import CreateBankAccount
from app.db import crud
from app.services import bank_account

account_router_bot = Router()

@account_router_bot.callback_query(F.data.startswith("create_account"))
async def create_account(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    if not user:
        await callback.message.answer("You are not registered.\nRegister 👇", reply_markup=await register_kb())
        return

    await callback.message.answer("Enter name your new bank account:")
    await state.set_state(CreateBankAccount.name)

@account_router_bot.message(CreateBankAccount.name)
async def get_name_account(message: Message, state: FSMContext):
    name_account = message.text
    await state.clear()

    telegram_user_id = message.from_user.id
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    user_id = user.id

    await bank_account.create_account(user_id, name_account)
    await message.answer(f"'{name_account}' bank account created")