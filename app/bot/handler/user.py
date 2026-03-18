from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import asyncio

from app.bot.keyboard import register_kb, create_bank_account_kb
from app.services.user import create_user
from app.db import crud

user_router_bot = Router()

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
