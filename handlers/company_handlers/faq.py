import logging
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from loader import dp, bot
from lang.get_message import get_message, get_keyboard, extract_language



router = Router()
dp.include_router(router)


# инструкция для получения бинг ключа
@router.message(Command('getbingkey'))
async def send_bing_key_instructions(message: Message):
    lang= extract_language(Message)
    msg = get_message(lang, "company", "get_bing_key_instructions")
    await message.answer(msg)