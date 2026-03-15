from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

user_router_bot = Router()

@user_router_bot.message(Command("start"))
async def command_start(message: Message):
    text = """
    Finance Flow Bot"""
    await message.answer(text)