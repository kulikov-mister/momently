from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def comment_keyboard(lang_texts):
    builder = ReplyKeyboardBuilder()
    for text in lang_texts:
        builder.row(KeyboardButton(text=text))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)