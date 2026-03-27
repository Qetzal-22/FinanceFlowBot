from datetime import datetime, date, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio
import logging


from app.bot.keyboard import register_kb, create_bank_account_kb, main_menu_kb, choose_account_for_transaction_kb, \
    categories_kb, category_menu_kb, profile_kb, add_category_kb, main_bank_account_kb, kalendar_kb
from app.bot.static import AddCategory
from app.db.crud import get_user_category
from app.services.user import create_user, check_register, get_categories, create_user_category, create_category, delete_category
from app.services.bank_account import get_bank_accounts
from app.db import crud
from app.utils.time import create_new_date, count_day_in_month

user_router_bot = Router()
logger = logging.getLogger(__name__)

@user_router_bot.message(Command("start"))
async def command_start(message: Message):
    text = """
    Finance Flow Bot"""
    await message.answer(text, reply_markup=await register_kb())

@user_router_bot.message(Command("help"))
async def command_help(message: Message):
    text = """
    help command"""
    await message.answer(text)

@user_router_bot.message(Command("register"))
async def command_register(message: Message):
    text = """
    Register:"""
    await message.answer(text, reply_markup=await register_kb())

@user_router_bot.callback_query(F.data.startswith("register"))
async def register(callback: CallbackQuery):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    user = await crud.get_user_by_telegram_id(telegram_user_id)
    if user:
        await callback.message.answer("You are registered yet")
        return

    await create_user(telegram_user_id)
    await callback.message.answer("You are registered")

    await asyncio.sleep(1)
    return await welcome_message(callback.message)

async def welcome_message(message: Message):
    welcome_text = """
    Hello, this bot help you controlling your expanded and income
    
Create your virtual bank account for start use bot 👇"""

    await message.answer(welcome_text, reply_markup=await create_bank_account_kb())

@user_router_bot.message(Command("main"))
async def main_menu(message: Message):
    telegram_user_id = message.from_user.id
    check_user = await check_register(telegram_user_id)
    if not check_user:
        await message.answer("You are not registered.\nRegister 👇", reply_markup=await register_kb())
        return

    await message.answer("Menu: ", reply_markup=await main_menu_kb())

@user_router_bot.message(F.text.lower() == "back to menu")
async def back_to_menu(message: Message):
    return await main_menu(message)

@user_router_bot.message(F.text.lower() == "profile")
async def view_profile(message: Message):
    telegram_user_id = message.from_user.id
    accounts = await get_bank_accounts(telegram_user_id)
    logger.info("view account get accounts telegram_user_id=%s length_accounts=%s", telegram_user_id, len(accounts))

    text = "👤 <b>PROFILE</b>\n━━━━━━━━━━━━━━━━━━\n"

    if len(accounts) == 0:
        text += "You haven`t bank account\n━━━━━━━━━━━━━━━━━━\n"
        await message.answer(text, parse_mode="HTML", reply_markup=await profile_kb())
        await message.answer("Create your virtual bank account 👇", parse_mode="HTML", reply_markup=await create_bank_account_kb())

    else:
        for account in accounts:
            account_name = account.name
            account_balance = account.balance
            text += f"\n<b>{account_name}</b>\nBalance: {account_balance}\n"
        text += "━━━━━━━━━━━━━━━━━━"

        await message.answer(text, parse_mode="HTML", reply_markup=await profile_kb())

@user_router_bot.message(F.text.lower() == "my category")
async def category(message: Message):
    telegram_user_id = message.from_user.id
    categories = await get_categories(telegram_user_id)

    text = "<b>CATEGORIES</b>\n━━━━━━━━━━━━━━━━━━\n"

    if len(categories) == 0:
        text += "\nYou haven`t your category\n━━━━━━━━━━━━━━━━━━"
    else:
        for category in categories:
            text += f"\n{category.name}\n"
        text += "━━━━━━━━━━━━━━━━━━"

    await message.answer(text, parse_mode="HTML", reply_markup=await category_menu_kb())
    if len(categories) == 0:
        await message.answer("Add new category 👇", reply_markup=await add_category_kb())

@user_router_bot.callback_query(F.data.startswith("category_add"))
async def add_category_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    return await add_category(callback.message, state)

@user_router_bot.message(F.text.lower() == "add category")
async def add_category(message: Message, state: FSMContext):
    await state.set_state(AddCategory.name)
    await message.answer("Enter name new category: ")

@user_router_bot.message(AddCategory.name)
async def get_category_name(message: Message, state: FSMContext):
    await state.clear()
    telegram_user_id = message.from_user.id
    name = message.text
    category_all = await crud.get_categories_all()
    for category in category_all:
        if name == category.name:
            await create_user_category(telegram_user_id, category.id)
            await message.answer("Category will added")
            return

    category = await create_category(name)
    await create_user_category(telegram_user_id, category.id)
    await message.answer("Category will added")
    return

@user_router_bot.message(F.text.lower() == "remove category")
async def remove_category(message: Message):
    telegram_user_id = message.from_user.id
    categories = await get_categories(telegram_user_id)
    await message.answer("Choose category for remove 👇", reply_markup=await categories_kb(categories))

@user_router_bot.callback_query(F.data.startswith("category_rm"))
async def get_category_for_rm(callback: CallbackQuery):
    await callback.answer()
    telegram_user_id = callback.from_user.id
    category_id = int(callback.data.split(":")[1])

    await delete_category(telegram_user_id, category_id)
    await callback.message.answer("Category will removed")

@user_router_bot.message(F.text.lower() == "view history")
async def choose_date(message: Message, state: FSMContext):
    date_now = datetime.utcnow()
    count_days = await count_day_in_month(date_now)

    msg = await message.answer(f"Date: 1.{date_now.month}.{date_now.year}\nChoose day month 👇", reply_markup=await kalendar_kb(date_now, count_days))
    message_id = msg.message_id
    await state.update_data(message_id=message_id)

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
        text=f"Date: 1.{new_date.month}.{new_date.year}\nChoose day month 👇"
    )
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        reply_markup=await kalendar_kb(new_date, count_days)
    )

@user_router_bot.callback_query(F.data.startswith("stud"))
async def callback_stud(callback: CallbackQuery):
    await callback.answer()