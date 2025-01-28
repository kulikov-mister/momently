from typing import Union

from database.get_to_db import get_user, has_orders, get_active_orders_by_user_id, get_courier
from aiogram.types import Message, CallbackQuery
from keyboards.inline.orders_inline.user_order_inline.cancel_order import cancel_order_buttons
from keyboards.inline.user_inline.markup_main import markup_main
from utils.order_detail import calculate_order_details
from config_data.config import CURRENCY

async def main_menu(event: Union[Message, CallbackQuery]):
    # Определяем, откуда пришло событие
    if isinstance(event, Message):
        user_id = event.chat.id
        to_answer = event.answer
    elif isinstance(event, CallbackQuery):
        user_id = event.from_user.id
        to_answer = event.message.edit_text
        await event.answer()

    user = await get_user(user_id)

    if has_orders(user_id):
        # Если есть заказы, выводим информацию о заказе
        # Получаем информацию о заказах пользователя
        orders = await get_active_orders_by_user_id(user_id)
        for order in orders:
            courier = await get_courier(order.courier_id)
            first_address, second_address = await calculate_order_details(order)
            pro_status = " | PRO 🏅" if courier and courier.is_pro else ""
            cancel_order = cancel_order_buttons(order.id)
            link = f"<a href='tg://user?id={courier.user_id}'>Написать курьеру</a>" if courier else ''
            # Выводим информацию о каждом заказе
            await to_answer(f"📄 Информация о заказе №{order.id}:\n\n\n"
                                 f"👨 <b>Имя курьера:</b> {courier.name if courier else 'в поиске'}<b>{pro_status}</b>\n\n"
                                 f"📈 <b>Рейтинг курьера:</b> {courier.rating if courier else 'в поиске'}\n\n"
                                 f"📱 <b>Телефон курьера:</b> {courier.phone if courier else 'в поиске'}\n\n"
                                 f"🌆 <b>Расстояние:</b> {order.distance:.2f} км\n\n\n"
                                 f"🅰️ <b>Адрес отправления:</b> {first_address}\n\n"
                                 f"🅱️ <b>Адрес прибытия:</b> {second_address}\n\n\n"
                                 f"💰 <b>Стоимость:</b> {round(order.cost, 2)} {CURRENCY}\n\n"
                                 f"💭 Комментарий к заказу: <b>{order.comment}</b>\n\n\n"
                                 f"{link} ", reply_markup=cancel_order)
    else:
        # Если нет заказов, выводим приветственное сообщение
        await to_answer(f"👋 Привет, {user.name}!\n\n"
                        f"Пусть сегодня у вас все получится ❤️",
                        reply_markup=markup_main())