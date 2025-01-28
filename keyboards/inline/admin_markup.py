from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_builder import inline_builder


# Данные кнопок для разметки администратора
admin_buttons_data = [
    {"text": "📨 Рассылка", "callback_data": 'admin_broadcast'},
    {"text": "🗂 Информация о курьерах", "callback_data": 'toggle_driver'},
    {"text": "🔍 Найти заказ", "callback_data": 'find_order'},
    {"text": "📍 Добавить локацию", "callback_data": 'add_location'},  # New button
    {"text": "🗑 Удалить локацию", "callback_data": 'delete_location'}
]

def markup_admin():
    return inline_builder(admin_buttons_data)