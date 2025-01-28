from keyboards.inline_builder import inline_builder


# Данные для кнопок
buttons_data = [
    {"text": "❇️ Создать заказ", "callback_data": 'order'},
    {"text": "📖 Мои заказы", "callback_data": 'info'},
    {"text": "👥 Поддержка", "callback_data": 'support'},
    {"text": "💰 Стоимость поездок", "callback_data": 'price'}
    # {"text": "🏃‍♂️ Стать курьером", "callback_data": 'switch_to_courier'}
]

def markup_main():
    # Создаем разметку, используя функцию inline_builder и массив данных для кнопок
    return inline_builder(buttons_data)


