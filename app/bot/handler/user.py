from datetime import datetime, date, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio
import logging


from app.bot.keyboard import register_kb, create_bank_account_kb, main_menu_kb, choose_account_for_transaction_kb, \
    categories_kb, category_menu_kb, add_category_kb, main_bank_account_kb, kalendar_kb, history_kb, budget_menu_kb, \
    user_category_for_budget_kb, budget_remove_kb, budget_control_menu_kb, budget_edit_kb
from app.bot.static import AddCategory, CreateBudget, EditBudget
from app.db.crud import get_user_category
from app.db.models import Type_Operation
from app.services.user import create_user, check_register, get_categories, create_user_category, create_category, delete_category, \
    get_user_categories_by_telegram_id, get_category, get_category_with_budget
from app.services.bank_account import get_bank_accounts
from app.services.bank_operation import get_bank_operation_by_date
from app.services.budget import get_budget_by_user_category_id_now
from app import services
from app.db import crud
from app.utils.time import create_new_date, count_day_in_month

user_router_bot = Router()
logger = logging.getLogger(__name__)

@user_router_bot.message(Command("start"))
async def command_start(message: Message):
    text = """
💰 <b>Finance Flow Bot</b>

Бот для учёта доходов и расходов
"""
    await message.answer(text, reply_markup=await register_kb(), parse_mode="HTML")

@user_router_bot.message(Command("help"))
async def command_help(message: Message):
    text = """
ℹ️ <b>Помощь</b>

Этот бот помогает учитывать ваши доходы и расходы,
управлять счетами и категориями.
"""
    await message.answer(text, parse_mode="HTML")

@user_router_bot.message(Command("register"))
async def command_register(message: Message):
    text = """
📝 <b>Регистрация</b>

Нажмите кнопку ниже, чтобы зарегистрироваться
"""
    await message.answer(text, reply_markup=await register_kb())

@user_router_bot.callback_query(F.data.startswith("register"))
async def register(callback: CallbackQuery):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    if user:
        await callback.message.answer("✅ Вы уже зарегистрированы")
        return

    await create_user(telegram_user_id)
    await callback.message.answer("🎉 Регистрация успешно завершена")

    await asyncio.sleep(1)
    return await welcome_message(callback.message)

async def welcome_message(message: Message):
    welcome_text = """
👋 Добро пожаловать!

Этот бот поможет вам:
• отслеживать доходы и расходы  
• управлять финансами  

📌 Для начала создайте виртуальный банковский счёт 👇
"""
    await message.answer(welcome_text, reply_markup=await create_bank_account_kb())

@user_router_bot.message(Command("main"))
async def main_menu(message: Message, telegram_user_id: int = None):
    if not telegram_user_id:
        telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("❌ Вы не зарегистрированы.\nНажмите кнопку ниже 👇", reply_markup=await register_kb())
        return

    await message.answer("📋 Главное меню:", reply_markup=await main_menu_kb())

@user_router_bot.message(F.text.lower() == "назад в меню")
async def back_to_menu(message: Message):
    return await main_menu(message)

# @user_router_bot.message(F.text.lower() == "профиль")
# async def view_profile(message: Message):
#     telegram_user_id = message.from_user.id
#     accounts = await get_bank_accounts(telegram_user_id)
#     logger.info("view account get accounts telegram_user_id=%s length_accounts=%s", telegram_user_id, len(accounts))
#
#     text = "👤 <b>ПРОФИЛЬ</b>\n━━━━━━━━━━━━━━━━━━\n"
#
#     if len(accounts) == 0:
#         text += "У вас пока нет банковских счетов\n━━━━━━━━━━━━━━━━━━\n"
#         await message.answer(text, parse_mode="HTML", reply_markup=await profile_kb())
#         await message.answer("➕ Создайте свой первый счёт 👇", parse_mode="HTML", reply_markup=await create_bank_account_kb())
#
#     else:
#         for account in accounts:
#             account_name = account.name
#             account_balance = account.balance
#             text += f"\n<b>{account_name}</b>\nБаланс: {account_balance}\n"
#         text += "━━━━━━━━━━━━━━━━━━"
#
#         await message.answer(text, parse_mode="HTML", reply_markup=await profile_kb())

@user_router_bot.message(F.text.lower() == "категории")
async def category(message: Message):
    telegram_user_id = message.from_user.id
    categories = await get_categories(telegram_user_id)

    text = "<b>КАТЕГОРИИ</b>\n━━━━━━━━━━━━━━━━━━\n"

    if len(categories) == 0:
        text += "\nУ вас пока нет категорий\n━━━━━━━━━━━━━━━━━━"
    else:
        for category in categories:
            text += f"\n{category.name}\n"
        text += "━━━━━━━━━━━━━━━━━━"

    await message.answer(text, parse_mode="HTML", reply_markup=await category_menu_kb())
    if len(categories) == 0:
        await message.answer("➕ Добавьте первую категорию 👇", reply_markup=await add_category_kb())

@user_router_bot.callback_query(F.data.startswith("category_add"))
async def add_category_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    return await add_category(callback.message, state)

@user_router_bot.message(F.text.lower() == "добавить категорию")
async def add_category(message: Message, state: FSMContext):
    await state.set_state(AddCategory.name)
    await message.answer("✏️ Введите название новой категории:")

@user_router_bot.message(AddCategory.name)
async def get_category_name(message: Message, state: FSMContext):
    await state.clear()
    telegram_user_id = message.from_user.id
    name = message.text
    category_all = await crud.get_categories_all()
    for category in category_all:
        if name == category.name:
            await create_user_category(telegram_user_id, category.id)
            await message.answer("✅ Категория добавлена")
            return

    category = await create_category(name)
    await create_user_category(telegram_user_id, category.id)
    await message.answer("✅ Категория добавлена")
    return

@user_router_bot.message(F.text.lower() == "удалить категорию")
async def remove_category(message: Message):
    telegram_user_id = message.from_user.id
    categories = await get_categories(telegram_user_id)
    await message.answer("Выберите категорию для удаления 👇", reply_markup=await categories_kb(categories))

@user_router_bot.callback_query(F.data.startswith("category_rm"))
async def get_category_for_rm(callback: CallbackQuery):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    category_id = int(callback.data.split(":")[1])

    await delete_category(telegram_user_id, category_id)
    await callback.message.answer("🗑️ Категория удалена")

@user_router_bot.message(F.text.lower() == "бюджеты")
async def budget(message: Message):
    telegram_user_id = message.from_user.id
    user_categories = await get_user_categories_by_telegram_id(telegram_user_id)
    logger.info("budget length_user_categories=%s", len(user_categories))
    text = "<b>БЮДЖЕТЫ</b>\n━━━━━━━━━━━━━━━━━━"
    for user_category in user_categories:
        logger.info("budget iter for user_categories telegram_user_id=%s user_category_id=%s", telegram_user_id, user_category.id)
        category = await get_category(user_category.category_id)
        budget = await get_budget_by_user_category_id_now(user_category.id)
        if budget is None:
            continue
        text += f"\n• {category.name}\n💸 <b>{budget.spend}</b> / {budget.amount}\n"

    text += "\n━━━━━━━━━━━━━━━━━━"
    await message.answer(text, parse_mode="HTML", reply_markup=await budget_menu_kb())


@user_router_bot.message(F.text.lower() == "создать бюджет")
async def create_budget(message: Message):
    telegram_user_id = message.from_user.id
    user_categories = await get_user_categories_by_telegram_id(telegram_user_id)
    await message.answer("Выбери для какой категории нужно установить бюджет 👇", reply_markup=await user_category_for_budget_kb(user_categories))

@user_router_bot.callback_query(F.data.startswith("budget_category"))
async def get_category_for_create_budget(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_category_id = int(callback.data.split(":")[1])
    await state.update_data(user_category_id=user_category_id)

    user_category = await get_user_category(user_category_id)
    category = await get_category(user_category.category_id)

    await callback.message.answer(f"✏️ Введите сумму бюджета для категории {category.name}: ")
    await state.set_state(CreateBudget.amount)


@user_router_bot.message(CreateBudget.amount)
async def get_amount_for_create_budget(message: Message, state: FSMContext):
    amount_res = message.text
    if not amount_res.isdigit():
        await message.answer("❌ Вы ввели неверный формат данных. Сумма бюджета должна быть числом.")
        await message.answer("🔄 Попробуйсе еще раз:")
        await state.set_state(CreateBudget.amount)
        return

    amount = float(amount_res)

    data = await state.get_data()
    user_category_id = data["user_category_id"]
    logger.info("get_amount_for_create_budget user_category_id=%s type user_category_id=%s", user_category_id, type(user_category_id))
    await services.budget.create_budget(user_category_id, amount)

    await state.clear()

    user_category = await get_user_category(user_category_id)
    category = await get_category(user_category.category_id)
    await message.answer(f"✅ Новый бюджет создан для категории {category.name}")

@user_router_bot.message(F.text.lower() == "управление бюджетами")
async def control_budgets(message: Message):
    await message.answer("⚙️ Управление категориями: ", reply_markup=await budget_control_menu_kb())

@user_router_bot.message(F.text.lower() == "изменить бюджет")
async def choose_edit_budget(message: Message):
    telegram_user_id = message.from_user.id
    category_with_budget = await get_category_with_budget(telegram_user_id)

    await message.answer("Выберете категорию для редактирования бюджета 👇", reply_markup=await budget_edit_kb(category_with_budget))


@user_router_bot.callback_query(F.data.startswith("edit_budget"))
async def edit_budget(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_category_id = int(callback.data.split(":")[1])
    await state.update_data(user_category_id=user_category_id)
    await state.set_state(EditBudget.amount)
    await callback.message.answer("✏️ Введите сумму нового бюджета: ")


@user_router_bot.message(EditBudget.amount)
async def get_amount_edit_budget(message: Message, state: FSMContext):
    amount = message.text
    if not amount.isdigit():
        await state.set_state(EditBudget.amount)
        await message.answer("❌ Вы ввели неверный формат данных. Сумма бюджета должна быть числом.")
        await message.answer("🔄 Попробуйсе еще раз:")
        return
    amount = float(amount)
    data = await state.get_data()
    user_category_id = data["user_category_id"]

    await services.budget.edit_budget(user_category_id, amount)
    await state.clear()
    category = await crud.get_category(user_category_id)
    await message.answer(f"✅ Бюджет {category.name} отредактирован!")




@user_router_bot.message(F.text.lower() == "удалить бюджет")
async def choose_remove_budget(message: Message):
    telegram_user_id = message.from_user.id
    category_with_budget = await get_category_with_budget(telegram_user_id)

    await message.answer("Выберете категорию для удаления бюджета 👇", reply_markup=await budget_remove_kb(category_with_budget))

@user_router_bot.callback_query(F.data.startswith("remove_budget"))
async def remove_budget(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_category_id = int(callback.data.split(":")[1])
    await services.budget.remove_budget(user_category_id)
    await callback.message.answer("🗑️ Бюджет удален")



@user_router_bot.message(F.text.lower() == "мои бюджеты")
async def view_budget(message: Message):
    telegram_user_id = message.from_user.id
    categories_with_budget = await get_category_with_budget(telegram_user_id)

    def make_bar(spend, total, length=10):
        if total == 0:
            return "░" * length
        filled = int((spend / total) * length)
        filled = min(filled, length)
        return "█" * filled + "░" * (length - filled)

    text = "<b>📊 БЮДЖЕТЫ</b>\n"
    text += "━━━━━━━━━━━━━━━━━━\n"
    total_spend = 0
    total_budget = 0
    for user_category in categories_with_budget:
        category = await crud.get_category(user_category.category_id)
        budget = await services.budget.get_budget_by_user_category_id_now(user_category.id)

        spend = budget.spend
        total = budget.amount

        total_spend += spend
        total_budget += total

        percent = int((spend / total) * 100) if total else 0
        bar = make_bar(spend, total)

        # статус
        if spend > total:
            status = "🔴 ПЕРЕРАСХОД"
        elif percent > 80:
            status = "🟠 ПОЧТИ ЛИМИТ"
        else:
            status = "🟢 ОК"

        text += (
            f"<b>{category.name}</b>  {status}\n"
            f"{bar} {percent}%\n"
            f"💸 <b>{spend}</b> / {total}\n"
        )

        if spend > total:
            text += "⚠️ Превышен бюджет!\n"

        text += "\n"

    percent = int((total_spend / total_budget) * 100) if total_budget else 0
    bar = make_bar(total_spend, total_budget)

    # статус
    if total_spend > total_budget:
        status = "🔴 ПЕРЕРАСХОД"
    elif percent > 80:
        status = "🟠 ПОЧТИ ЛИМИТ"
    else:
        status = "🟢 ОК"
    text += (
        f"<b>Общий бюджет</b>  {status}\n"
        f"{bar} {percent}%\n"
        f"💸 <b>{total_spend}</b> / {total_budget}\n"
    )

    text += "━━━━━━━━━━━━━━━━━━"

    await message.answer(text, parse_mode="HTML")



@user_router_bot.message(F.text.lower() == "история")
async def history(message: Message, state: FSMContext):
    await message.answer("Выберети нужную опцию 👇", reply_markup=await history_kb())


@user_router_bot.callback_query(F.data.startswith("history_calendar"))
async def calendar(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    date_now = datetime.utcnow()
    count_days = await count_day_in_month(date_now)

    msg = await callback.message.answer(
        f"📅 Дата: 1.{date_now.month}.{date_now.year}\nВыберите день 👇",
        reply_markup=await kalendar_kb(date_now, count_days)
    )
    message_id = msg.message_id
    await state.update_data(message_id=message_id)

@user_router_bot.callback_query(F.data.startswith("history_7"))
async def history_7(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("⚠️Еще не готово (history_7)⚠️")

@user_router_bot.callback_query(F.data.startswith("history_30"))
async def history_30(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("⚠️Еще не готово (history_30)⚠️")

@user_router_bot.callback_query(F.data.startswith("kalendar_move"))
async def calendar_move(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    callback_data = callback.data.split(":")[1]
    new_year = int(callback_data.split("_")[0])
    new_month = int(callback_data.split("_")[1])
    new_date = datetime(new_year, new_month, 1)
    count_days = await count_day_in_month(new_date)

    data = await state.get_data()
    message_id = int(data["message_id"])
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        text=f"📅 Дата: 1.{new_date.month}.{new_date.year}\nВыберите день 👇"
    )
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        reply_markup=await kalendar_kb(new_date, count_days)
    )

@user_router_bot.callback_query(F.data.startswith("calendar_day"))
async def view_history_in_day(callback: CallbackQuery):
    await callback.answer()
    callback_data = callback.data.split(":")[1]
    logger.info("view_history_in_day callback_data=%s", callback_data)
    day = int(callback_data.split(".")[0])
    month = int(callback_data.split(".")[1])
    year = int(callback_data.split(".")[2])

    date_operation = datetime(year, month, day)
    operations = await get_bank_operation_by_date(date_operation)
    logger.info("view_history_in_day operation_lenght=%s", len(operations))
    for operation in operations:
        time = str(operation.create_at.time()).split('.')[0]
        good_time = operation.create_at.strftime("%H:%M")
        text = (f"━━━━━━━━━━━━━━━━━━\n")
        if operation.type == Type_Operation.INCOME:
            text += "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩\n"
        else:
            text += "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥\n"

        text += (
            f"💰 Сумма: {operation.amount}\n\n"
            f"📂 Категория: {operation.category}\n"
            f"📝 Описание: {operation.description}\n\n"
            f"⏰ Время: {good_time}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        logger.info("view_history_in_day send text")
        await callback.message.answer(text)


@user_router_bot.callback_query(F.data.startswith("stud"))
async def callback_stud(callback: CallbackQuery):
    await callback.answer()