from typing import Union

from aiogram.types import Message, CallbackQuery
from database.add_to_db import create_sent_item
from database.get_to_db import get_user, get_courier, get_order_by_courier_id, get_address_from_coordinates
from database.update_to_db import update_sent_item
from keyboards.inline.courier_inline.markup_main_courier import markup_main_courier
from keyboards.inline.orders_inline.courier_order_inline.expectation_order import get_expectation_button
from keyboards.inline.orders_inline.courier_order_inline.start_trip import get_start_trip_button
from states.order_states import OrderStatus
from utils.order_detail import calculate_order_details
from config_data.config import CURRENCY
from loader import dp, bot

async def main_menu_courier(event: Union[Message, CallbackQuery]):
    if isinstance(event, Message):
        courier_id = event.chat.id
        to_answer = event.answer
        to_answer_location = event.answer_location
    elif isinstance(event, CallbackQuery):
        courier_id = event.from_user.id
        to_answer = event.message.edit_text
        to_answer_location = event.message.answer_location
        await event.answer()
    
    courier = await get_courier(courier_id)

    # Поиск заказа для данного курьера
    order = get_order_by_courier_id(courier_id)

    if order:
        user = await get_user(order.user_id)
        first_address, second_address = await calculate_order_details(order)
        link = f"<a href='tg://user?id={order.user_id}'>Написать клиенту</a>"

        # Вывод информации о заказе
        if order.status == OrderStatus.ACCEPTED:
            expectation_button = get_expectation_button(order.id)
            button = expectation_button
        elif order.status in [OrderStatus.EXPECTATION, OrderStatus.TRIP]:
            start_trip_button = get_start_trip_button(order.id)
            button = start_trip_button
        else:
            button = None

        response = await to_answer(f"📄 Информация о заказе № {order.id}:\n\n\n"
                             f"🅰️ <b>Адрес отправления:</b> {first_address}\n\n"
                             f"🅱️ <b>Адрес прибытия:</b> {second_address}\n\n\n"
                             f"🙋‍♂️ <b>Имя клиента:</b> {user.name}\n\n"
                             f"📱 <b>Номер телефона клиента:</b> {user.phone}\n\n\n"
                             f"🌆 <b>Расстояние:</b> {order.distance:.2f} км\n\n"
                             f"💰 <b>Стоимость:</b> {round(order.cost, 2)} {CURRENCY}\n\n"
                             f"💵 <b>Оплата:</b> {order.payment_method}\n\n\n"
                             f"💭 Комментарий к заказу: <b>{order.comment}</b>\n\n\n"
                             f"{link}", reply_markup=button)
        
        sent_item = await create_sent_item(order)
        await update_sent_item(sent_item, text_message_id=response.message_id)

        if order.status == OrderStatus.ACCEPTED:
            first_location_msg = await bot.send_location(chat_id=order.courier_id, latitude=order.first_latitude,
                                                         longitude=order.first_longitude)
            await update_sent_item(sent_item, start_location_message_id=first_location_msg.message_id)
        
        # Если статус заказа EXPECTATION или TRIP, отправляем вторую геолокацию
        elif order.status in [OrderStatus.EXPECTATION, OrderStatus.TRIP]:
            second_location_msg = await bot.send_location(chat_id=order.courier_id, 
                latitude=order.second_latitude, longitude=order.second_longitude)
            await update_sent_item(sent_item, end_location_message_id=second_location_msg.message_id)
    
    else:
        # Если нет заказов, выводим приветственное сообщение
        
        if courier.admin_deactivated:
            await to_answer("❌ Ваша учетная запись деактивирована!")
            return

        location_address = await get_address_from_coordinates(courier.location.latitude, courier.location.longitude)
        pro_status = " | PRO 🏅" if courier.is_pro else ""
        
        if isinstance(event, Message):
            await to_answer_location(latitude=courier.location.latitude, longitude=courier.location.longitude)       

        await to_answer(f"👋 Привет, {courier.name}<b>{pro_status}</b>!\n\n"
                        f"Удачи сегодня в работе! 🤗\n\n\n"
                        f"📈 <b>Ваш рейтинг:</b> {courier.rating}\n\n"
                        f"📍 <b>Ваша локация:</b> {location_address}\n\n",
                        reply_markup=markup_main_courier(courier))
        

