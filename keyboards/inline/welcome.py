from keyboards.inline_builder import inline_builder

def generate_welcome_keyboard():
    buttons_data = [
        {"text": "👨‍💻 Пользователь", "callback_data": "user"},
        {"text": "🥷 Курьер", "callback_data": "courier"},
        {"text": "👨‍🔧 Компания", "callback_data": "company"},
        {"text": "💰 Стоимость услуг", "callback_data": "price"},
        {"text": "👥 Связаться с поддержкой", "callback_data": "support"}
    ]

    return inline_builder(buttons_data)
