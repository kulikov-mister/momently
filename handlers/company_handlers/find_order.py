from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from Filter.Filter import IsNotCommand, IsAdmin
from database.database import Order
from database.get_to_db import get_user, get_courier
from keyboards.inline.orders_inline.user_order_inline.cancel_order import cancel_order_buttons
from loader import dp
from states.admin_states import CompanyFindOrder
from utils.order_detail import calculate_order_details
from config_data.config import CURRENCY

router = Router()
dp.include_router(router)

@router.callback_query(F.data == 'find_order', IsAdmin())
async def admin_find_order(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(CompanyFindOrder.waiting_for_order_number)
    await call.message.answer("Введите номер заказа:")


@router.message(IsNotCommand(), CompanyFindOrder.waiting_for_order_number)
async def order_info(message: Message, state: FSMContext):
    order_id = message.text
    order = Order.get_or_none(Order.id == order_id)

    if order:
        user = await get_user(order.user_id)
        courier = await get_courier(order.courier_id)
        first_address, second_address = await calculate_order_details(order)
        cancel_order = cancel_order_buttons(order.id)
        order_info = f"❓ Информация о заказе №{order_id}:\n\n\n" \
                     f"👥 <b>Имя клиента:</b> {user.name}\n\n" \
                     f"📱 <b>Номер клиента:</b> {user.phone}\n\n\n" \
                     f"👨 <b>Имя курьера:</b> {courier.name if order.courier_id else 'Не определен'}\n\n" \
                     f"📍 <b>Откуда:</b> {first_address}\n\n" \
                     f"📍 <b>Куда:</b> {second_address}\n\n" \
                     f"🌆 <b>Расстояние:</b> {order.distance:.2f} км\n\n\n" \
                     f"💰 <b>Стоимость:</b> {order.cost} {CURRENCY}\n\n" \
                     f"🚦 <b>Статус:</b> {order.status}\n\n" \
                     f"💵 <b>Метод оплаты:</b> {order.payment_method}\n\n" \
                     f"💬 <b>Комментарий:</b> {order.comment}\n\n" \
                     f"⭐ <b>Рейтинг:</b> {order.rating}"

        if order.status == "CANCELED" or order.status == "COMPLETED":
            await message.answer(order_info)
        else:
            await message.answer(order_info, reply_markup=cancel_order)

    else:
        await message.answer("🤷‍♂️ Заказа с таким номером не найдено.")
