from keyboards.inline_builder import inline_builder

def markup_main_courier(courier):
    courier_is_active = courier.is_active if courier else False

    # Определяем данные для кнопок
    buttons_data = [
        {"text": "📖 Мои заказы", "callback_data": 'courier_info'},
        {"text": "👥 Поддержка", "callback_data": 'support'},
        {"text": "💰 Стоимость", "callback_data": 'price'},
        # {"text": "🙋‍♂️ Стать клиентом", "callback_data": 'switch_to_client'},
        {"text": "🚬 На перекур" if courier_is_active else "👷 За работу", "callback_data": 'toggle_active'},
        {"text": "🔄 Изменение локации", "callback_data": 'change_location'}
    ]

    # Создаем разметку, используя функцию inline_builder и массив данных для кнопок
    return inline_builder(buttons_data)