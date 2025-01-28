from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.inline_builder import inline_builder
from database.database import Order
from database.get_to_db import get_courier
from handlers.user_handlers import main_menu_user
from loader import bot, dp
from states.order_states import OrderStatus

router = Router()
dp.include_router(router)

def get_rating_keyboard(order_id):
    buttons_data = [
        {"text": emoji, "callback_data": f"rate_{order_id}_{rating}"}
        for rating, emoji in zip(range(1, 6), ["🤬", "😒", "😐", "😁", "🤩"])
    ]

    return inline_builder(buttons_data, 5)



@router.callback_query(F.data.startswith('rate'))
async def rate_order(call: CallbackQuery):
    _, order_id, rating = call.data.split("_", 2)
    order_id, rating = int(order_id), int(rating)

    order = Order.get_by_id(order_id)
    order.rating = rating
    order.save()

    courier = await get_courier(order.courier_id)
    orders = Order.select().where(Order.courier_id == courier.user_id, Order.status != OrderStatus.CANCELED)
    rated_orders = [order for order in orders if order.rating is not None]
    if rated_orders:
        total_rating = sum([order.rating for order in rated_orders])
        courier.rating = round(total_rating / len(rated_orders), 2)
    else:
        courier.rating = rating
    courier.save()

    await call.answer()
    await bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        text="😊 Спасибо за оценку!"
    )

    await main_menu_user.main_menu(call.message)
    await bot.send_message(courier.user_id,
                           f"📄 Заказ №<b>{order_id}</b> был оценен. Вы получили оценку: <b>{rating}</b>\n\n"
                           f"📈 Ваш рейтинг обновлен!")
