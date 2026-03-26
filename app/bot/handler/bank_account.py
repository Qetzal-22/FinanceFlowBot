from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from app.bot.handler.user import main_menu, category
from app.bot.keyboard import register_kb, choose_account_for_transaction_kb, choose_type_transaction_kb, \
    category_for_transaction_kb, main_bank_account_kb, create_bank_account_kb
from app.bot.static import CreateBankAccount, CreateTransaction
from app.db import crud
from app.db.models import Type_Operation
from app.services import bank_account
from app.services.bank_operation import create_operation
from app.services.user import check_register, get_categories
from app.services.bank_account import get_bank_accounts

account_router_bot = Router()

logger = logging.getLogger(__name__)

@account_router_bot.message(F.text.lower() == "create new account")
async def create_account(message: Message, state: FSMContext, telegram_user_id: int = None):
    if not telegram_user_id:
        telegram_user_id = message.from_user.id

    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("You are not registered.\nRegister 👇", reply_markup=await register_kb())
        return

    await message.answer("Enter name your new bank account:")
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

    await main_menu(message)

@account_router_bot.message(F.text.lower() == "record transaction")
async def record_transaction(message: Message):
    telegram_user_id = message.from_user.id
    accounts = await get_bank_accounts(telegram_user_id)
    await message.answer("Choose bank account for operation", reply_markup=await choose_account_for_transaction_kb(accounts))

@account_router_bot.callback_query(F.data.startswith("transaction_account"))
async def create_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = callback.data.split(":")[1]

    await state.update_data(account_id=account_id)

    await callback.message.answer("Choose type operation 👇", reply_markup=await choose_type_transaction_kb())

@account_router_bot.callback_query(F.data.startswith("type_transaction"))
async def get_type_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    type_operation = Type_Operation(callback.data.split(":")[1])

    await state.update_data(type=type_operation)
    await state.set_state(CreateTransaction.amount)

    await callback.message.answer("Enter amount operation: ")

@account_router_bot.message(CreateTransaction.amount)
async def get_amount_transaction(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    amount = message.text

    if not amount.isdigit():
        await message.answer("Amount should be Integer")
        await state.set_state(CreateTransaction.amount)
        await message.answer("Enter amount operation: ")
        return

    amount = float(amount)
    await state.update_data(amount=amount)

    data = await state.get_data()
    type_transaction = data["type"]

    if type_transaction == "expense":
        categories = await get_categories(telegram_user_id)

        await message.answer("Choose category 👇", reply_markup=await category_for_transaction_kb(categories))
    else:
        await message.answer("Write description for transaction: ")
        await state.set_state(CreateTransaction.description)

@account_router_bot.callback_query(F.data.startswith("transaction_category"))
async def get_category_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split(":")[1]
    await state.update_data(category=category)

    await callback.message.answer("Write description for transaction: ")
    await state.set_state(CreateTransaction.description)

@account_router_bot.message(CreateTransaction.description)
async def get_description_transaction(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    account_id = data["account_id"]
    type_transaction = data["type"]
    amount = data["amount"]
    category = data["category"]

    await create_operation(account_id, type_transaction, amount, description,  category)

    await message.answer("Bank operation recorded")

@account_router_bot.message(F.text.lower() == "bank account")
async def main_menu_bank_account(message: Message):
    telegram_user_id = message.from_user.id
    accounts = await get_bank_accounts(telegram_user_id)
    logger.info("View account get accounts telegram_user_id=%s length_accounts=%s", telegram_user_id, len(accounts))

    text = "<b>BANK ACCOUNT</b>\n━━━━━━━━━━━━━━━━━━\n"

    if len(accounts) == 0:
        text += "You haven`t bank account\n━━━━━━━━━━━━━━━━━━\n"
        await message.answer(text, parse_mode="HTML", reply_markup=await main_bank_account_kb())
        await message.answer("Create your virtual bank account 👇", parse_mode="HTML", reply_markup=await create_bank_account_kb())

    else:
        for account in accounts:
            account_name = account.name
            account_balance = account.balance
            text += f"\n<b>{account_name}</b>\nBalance: {account_balance}\n"
        text += "━━━━━━━━━━━━━━━━━━"

        await message.answer(text, parse_mode="HTML", reply_markup=await main_bank_account_kb())

@account_router_bot.callback_query(F.data.startswith("create_account"))
async def create_account_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    return await create_account(callback.message, state, telegram_user_id=callback.from_user.id)