from keyboards.inline_builder import inline_builder

def order_acceptance_keyboard(order):
    buttons_data = [
        {"text": "✅ Принять заказ", "callback_data": f"order_acceptance_{order.id}"},
        {"text": "💰 Предложить цену", "callback_data": f"order_propose_price_{order.id}"}
        ]
    return inline_builder(buttons_data)

def order_acceptance_keyboard_without_propose_price(order):
    buttons_data = [{"text": "✅ Принять заказ", "callback_data": f"order_acceptance_{order.id}"}]
    return inline_builder(buttons_data)