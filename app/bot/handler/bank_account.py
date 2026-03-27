from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from app.bot.handler.user import main_menu, category, back_to_menu
from app.bot.keyboard import register_kb, choose_account_for_transaction_kb, choose_type_transaction_kb, \
    category_for_transaction_kb, main_bank_account_kb, create_bank_account_kb, choose_account_kb, edit_account_kb, \
    confirmation_remove_kb
from app.bot.static import CreateBankAccount, CreateTransaction, RenameAccount
from app.db import crud
from app.db.crud import delete_bank_account
from app.db.models import Type_Operation
from app.services import bank_account
from app.services.bank_operation import create_operation
from app.services.user import check_register, get_categories
from app.services.bank_account import get_bank_accounts, update_account

account_router_bot = Router()

logger = logging.getLogger(__name__)

@account_router_bot.message(F.text.lower() == "создать новый счёт")
async def create_account(message: Message, state: FSMContext, telegram_user_id: int = None):
    if not telegram_user_id:
        telegram_user_id = message.from_user.id

    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

    await message.answer("✏️ Введите название нового счёта:")
    await state.set_state(CreateBankAccount.name)

@account_router_bot.message(CreateBankAccount.name)
async def get_name_account(message: Message, state: FSMContext):
    name_account = message.text
    await state.clear()

    telegram_user_id = message.from_user.id
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    user_id = user.id

    await bank_account.create_account(user_id, name_account)
    await message.answer(f"✅ Счёт «{name_account}» создан")

    await main_menu(message)

@account_router_bot.message(F.text.lower() == "добавить операцию")
async def record_transaction(message: Message):
    telegram_user_id = message.from_user.id
    accounts = await get_bank_accounts(telegram_user_id)
    await message.answer("Выберите счёт для операции 👇", reply_markup=await choose_account_for_transaction_kb(accounts))

@account_router_bot.callback_query(F.data.startswith("transaction_account"))
async def create_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = int(callback.data.split(":")[1])

    await state.update_data(account_id=account_id)

    await callback.message.answer("Выберите тип операции 👇", reply_markup=await choose_type_transaction_kb())

@account_router_bot.callback_query(F.data.startswith("type_transaction"))
async def get_type_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    type_operation = Type_Operation(callback.data.split(":")[1])

    await state.update_data(type=type_operation)
    await state.set_state(CreateTransaction.amount)

    await callback.message.answer("💰 Введите сумму:")

@account_router_bot.message(CreateTransaction.amount)
async def get_amount_transaction(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    amount = message.text

    if not amount.isdigit():
        await message.answer("❗ Сумма должна быть числом")
        await state.set_state(CreateTransaction.amount)
        await message.answer("💰 Введите сумму:")
        return

    amount = float(amount)
    await state.update_data(amount=amount)

    data = await state.get_data()
    type_transaction = data["type"]

    if type_transaction == Type_Operation.EXPENSE:
        categories = await get_categories(telegram_user_id)

        await message.answer("Выберите категорию 👇", reply_markup=await category_for_transaction_kb(categories))
    else:
        await message.answer("✏️ Введите описание операции:")
        await state.set_state(CreateTransaction.description)

@account_router_bot.callback_query(F.data.startswith("transaction_category"))
async def get_category_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split(":")[1]
    logger.info("get_category_transaction category=%s", category)
    await state.update_data(category=category)

    await callback.message.answer("✏️ Введите описание операции:")
    await state.set_state(CreateTransaction.description)

@account_router_bot.message(CreateTransaction.description)
async def get_description_transaction(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    account_id = data["account_id"]
    type_transaction = data["type"]
    amount = data["amount"]
    if type_transaction == Type_Operation.EXPENSE:
        category = data["category"]
        await create_operation(account_id, type_transaction, amount, description,  category)
    else:
        await create_operation(account_id, type_transaction, amount, description)

    await state.clear()
    await message.answer("✅ Операция успешно добавлена")

@account_router_bot.message(F.text.lower() == "банковский счёт")
async def main_menu_bank_account(message: Message):
    telegram_user_id = message.from_user.id
    accounts = await get_bank_accounts(telegram_user_id)
    logger.info("View account get accounts telegram_user_id=%s length_accounts=%s", telegram_user_id, len(accounts))

    text = "<b>БАНКОВСКИЕ СЧЕТА</b>\n━━━━━━━━━━━━━━━━━━\n"

    if len(accounts) == 0:
        text += "У вас пока нет счетов\n━━━━━━━━━━━━━━━━━━\n"
        await message.answer(text, parse_mode="HTML", reply_markup=await main_bank_account_kb())
        await message.answer("➕ Создайте счёт 👇", parse_mode="HTML", reply_markup=await create_bank_account_kb())

    else:
        for account in accounts:
            account_name = account.name
            account_balance = account.balance
            text += f"\n<b>{account_name}</b>\nБаланс: {account_balance}\n"
        text += "━━━━━━━━━━━━━━━━━━"

        await message.answer(text, parse_mode="HTML", reply_markup=await main_bank_account_kb())


@account_router_bot.message(F.text.lower() == "редактировать счёт")
async def choose_account_for_edit(message: Message):
    telegram_user_id = message.from_user.id
    accounts = await get_bank_accounts(telegram_user_id)
    await message.answer("Выберите счёт для редактирования 👇", reply_markup=await choose_account_kb(accounts))

@account_router_bot.callback_query(F.data.startswith("account"))
async def edit_account_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = int(callback.data.split(":")[1])
    await state.update_data(account_id=account_id)
    await callback.message.answer("⚙️ Управление счётом:", reply_markup=await edit_account_kb())


@account_router_bot.message(F.text.lower() == "переименовать")
async def rename_account(message: Message, state: FSMContext):
    await message.answer("✏️ Введите новое название:")
    await state.set_state(RenameAccount.name)

@account_router_bot.message(RenameAccount.name)
async def get_new_name(message: Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    account_id = data["account_id"]
    await update_account(account_id, name=new_name)
    await message.answer("✅ Название счёта обновлено")

    await state.clear()


@account_router_bot.message(F.text.lower() == "удалить счёт")
async def confirmation_remove(message: Message):
    await message.answer("❗ Вы уверены, что хотите удалить счёт?", reply_markup=await confirmation_remove_kb())

@account_router_bot.callback_query(F.data.startswith("conf_remove_account"))
async def response_confirmation_remove(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    response = callback.data.split(":")[1]
    if response == "remove":
        data = await state.get_data()
        account_id = data["account_id"]
        await delete_bank_account(account_id)
        await callback.message.answer("🗑️ Счёт удалён", reply_markup=await main_bank_account_kb())
    else:
        await main_menu(callback.message, callback.from_user.id)

    await state.clear()


@account_router_bot.callback_query(F.data.startswith("create_account"))
async def create_account_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    return await create_account(callback.message, state, telegram_user_id=callback.from_user.id)