# keyboards/reply/sent_contact.py
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

def create_contact_keyboard(button_text: str):
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=button_text, request_contact=True)
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
