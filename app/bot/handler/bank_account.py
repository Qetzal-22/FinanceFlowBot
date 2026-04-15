from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from app.bot.handler.user import main_menu, category, back_to_menu
from app.bot.keyboard import register_kb, choose_account_for_transaction_kb, choose_type_transaction_kb, \
    category_for_transaction_kb, main_bank_account_kb, create_bank_account_kb, choose_account_kb, control_account_kb, \
    confirmation_remove_kb, more_for_operation_kb
from app.bot.static import CreateBankAccount, CreateTransaction, RenameAccount
from app.db import crud
from app.db.crud import delete_bank_account
from app.db.models import Type_Operation
from app.services import bank_account, bank_operation
from app.services.bank_operation import create_operation, delete_operation
from app.services.user import check_register, get_categories, get_user_id
from app.services.bank_account import get_bank_accounts, update_account, set_default
from app.services.category_aliases import get_category_by_key_word_and_user_id, create_category_aliases
from app.domain.enums import EventOverflowBudget

account_router_bot = Router()

logger = logging.getLogger(__name__)

@account_router_bot.message(F.text.lower() == "создать счет")
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
async def record_transaction(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

    text = """
    Введи <b>сумму</b> 💸  
Можно сразу с <b>категорией</b>:

Примеры:
300 еда  
-1500 такси

Если категорию не указать — <b>выберешь дальше</b> 👇"""
    await state.set_state(CreateTransaction.amount)

    await message.answer(text, parse_mode="HTML")

@account_router_bot.message(CreateTransaction.amount)
async def create_transaction(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

    user_id = await get_user_id(telegram_user_id)

    message_text = message.text
    message_text = message_text.split()

    amount = message_text[0]
    logger.info("create transaction amount=%s", amount)
    if not amount.replace("-", "").isdigit():
        await message.answer("❗ Сумма должна быть числом")
        await state.set_state(CreateTransaction.amount)
        await message.answer("🔄 Попробуйсе еще раз:")
        return
    elif float(amount.replace("-", "")) == 0:
        await message.answer("❗ Сумма должна быть 0")
        await state.set_state(CreateTransaction.amount)
        await message.answer("🔄 Попробуйсе еще раз:")
        return

    logger.info("create transaction amount=%s", amount)
    if "-" in amount:
        amount = float(amount)

    else:
        amount = float(amount)
    logger.info("create transaction last transfor in float amount=%s", amount)

    type_operation = Type_Operation.INCOME if amount > 0 else Type_Operation.EXPENSE
    await state.update_data(amount=amount)
    await state.update_data(type_operation=type_operation)
    await state.update_data(key_word=None)

    if len(message_text) == 1:
        if amount > 0:
            result = await create_operation(user_id, type_operation, amount)
            operation = result[0]
            await message.answer("✅ Операция добавлена", reply_markup=await more_for_operation_kb(operation.id))
        else:
            categories = await get_categories(telegram_user_id)
            await message.answer("Выберите категорию 👇", reply_markup=await category_for_transaction_kb(categories))

    else:
        key_word = " ".join(message_text[1:])
        category = await get_category_by_key_word_and_user_id(user_id, key_word)
        if not category:
            categories = await get_categories(telegram_user_id)
            await state.update_data(key_word=key_word)
            await message.answer("Выберите категорию 👇", reply_markup=await category_for_transaction_kb(categories))
        else:
            result = await create_operation(user_id, type_operation, amount, category.id)
            operation = result[0]
            await message.answer("✅ Операция добавлена", reply_markup=await more_for_operation_kb(operation.id))


@account_router_bot.callback_query(F.data.startswith("transaction_category"))
async def get_category_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    user_id = await get_user_id(telegram_user_id)
    category_id = int(callback.data.split(":")[1])
    logger.info("get_category_transaction category_id=%s", category_id)

    data = await state.get_data()
    amount = data["amount"]
    type_operation = data["type_operation"]
    key_word = data["key_word"]

    result = await create_operation(user_id, type_operation, amount, category_id)
    operation = result[0]
    event = result[1]
    await callback.message.answer("✅ Операция добавлена", reply_markup=await more_for_operation_kb(operation.id))

    if key_word:
        await create_category_aliases(user_id, category_id, key_word)

    if event == EventOverflowBudget.NONE:
        return
    elif event == EventOverflowBudget.WARNING_80:
        await message.answer("⚠️ Внимание: от бюджета потрачено более 80% ⚠️")
    elif event == EventOverflowBudget.WARNING_90:
        await message.answer("⚠️ Внимание: от бюджета потрачено более 90% ⚠️")
    elif event == EventOverflowBudget.WARNING_100:
        await message.answer("⚠️ Вы вышли за рамки бюджета ⚠️")


@account_router_bot.callback_query(F.data.startswith("description_operation"))
async def add_description_for_operation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    operation_id = int(callback.data.split(":")[1])
    await state.update_data(operation_id=operation_id)
    await state.set_state(CreateTransaction.description)
    await callback.message.answer("✏️ Введите описание к операции:")

@account_router_bot.message(CreateTransaction.description)
async def get_description_transaction(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    operation_id = data["operation_id"]

    await state.clear()
    await bank_operation.add_description_for_operation(operation_id, description)
    await message.answer("✅ Описание добавлено")

@account_router_bot.callback_query(F.data.startswith("undo_operation"))
async def undo_for_operation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    operation_id = int(callback.data.split(":")[1])
    await delete_operation(operation_id)
    await callback.message.answer("🗑️ Операция отменена")

@account_router_bot.message(F.text.lower() == "счета")
async def main_menu_bank_account(message: Message):
    telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

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


@account_router_bot.message(F.text.lower() == "управление счетами")
async def choose_account_for_edit(message: Message):
    telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

    accounts = await get_bank_accounts(telegram_user_id)
    await message.answer("Выберите счёт для редактирования 👇", reply_markup=await choose_account_kb(accounts))

@account_router_bot.callback_query(F.data.startswith("account"))
async def edit_account_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = int(callback.data.split(":")[1])
    await state.update_data(account_id=account_id)
    await callback.message.answer("⚙️ Управление счётом:", reply_markup=await control_account_kb())

@account_router_bot.message(F.text.lower() == "сделать по умолчанию")
async def bank_account_set_default(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]
    await set_default(account_id)

    account = await crud.get_bank_account(account_id)
    await message.answer(f"✅ Счет {account.name} установлен как по умолчанию")

@account_router_bot.message(F.text.lower() == "переименовать")
async def rename_account(message: Message, state: FSMContext):
    telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

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
    telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

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