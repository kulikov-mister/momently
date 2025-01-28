from keyboards.inline_builder import inline_builder

# Определяем данные для кнопок
buttons_data = [
    {"text": "💵 Наличные", "callback_data": "cash"},
    {"text": "💳 Перевод", "callback_data": "transfer"}
]

def payment_keyboard():
    # Создаем клавиатуру с помощью inline_builder
    return inline_builder(buttons_data)
