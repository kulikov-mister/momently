from keyboards.inline_builder import inline_builder

def accept_or_decline_price_keyboard(order, courier_id, price):
    buttons_data = [
        {"text": "✅ Принять", "callback_data": f"acceptprice_{order.id}_{courier_id}_{price}"},
        {"text": "❌ Отклонить", "callback_data": f"declineprice_{order.id}_{courier_id}_{price}"}
    ]

    return inline_builder(buttons_data)