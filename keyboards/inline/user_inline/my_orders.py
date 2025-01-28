from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
from keyboards.inline_builder import get_paginated_keyboard, get_inline_orders
from keyboards.inline.inlline_back import back_keyboard
from database.database import Order
from database.get_to_db import get_courier
from loader import dp
from states.order_states import OrderStatus
from utils.order_detail import calculate_order_details
from config_data.config import CURRENCY


router = Router()
dp.include_router(router)

# Нажатие на кнопку "Мои заказы"
@router.callback_query(or_f(F.data == 'info', F.data.startswith('info:')))
async def my_trips(call: CallbackQuery, state: FSMContext):
    split_data = call.data.split(":")
    current_page = split_data[1] if len(split_data) > 1 else None
    page = 1 if current_page is None else current_page
    user_id = call.from_user.id
    orders = Order.select().where(Order.user_id == user_id)
    call.answer()
    
    if orders:
        if call.data == 'info':
            await state.update_data({"current_page": 1})
        inline_orders = get_inline_orders(orders, 1)
        markup = get_paginated_keyboard(inline_orders, int(page), 'mainstart', 'u_orders')
        await call.message.edit_text("📖 Ваши заказы:", reply_markup=markup)
        
    else:
        markup = back_keyboard("mainstart")
        await call.message.edit_text("🙃 У вас еще не было заказов.",
                                     reply_markup=markup)



# Нажатие на кнопку с конкретным заказом
@router.callback_query(F.data.startswith('order_info_'))
async def order_info(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    current_page = state_data.get("current_page")
    order_id = int(call.data.split("_")[2])
    order = Order.get_by_id(order_id)

    first_address, second_address = await calculate_order_details(order)

    page = current_page if current_page else 1

    if order:
        courier = await get_courier(order.courier_id)
        callback_data = f"info:{page}"
        markup = back_keyboard(callback_data)
        message = f"📄 Информация о заказе №{order.id}:\n\n\n" \
                  f"👨 <b>Курьер:</b> {courier.name if order.courier_id else 'Не определен'}\n\n" \
                  f"🅰️ <b>Адрес отправления:</b> {first_address}\n" \
                  f"🅱️ <b>Адрес прибытия:</b> {second_address}\n" \
                  f"💰 <b>Стоимость:</b> {round(order.cost)} {CURRENCY}\n\n" \
                  f"💫 <b>Статус:</b> {'Выполнен' if order.status == OrderStatus.COMPLETED else 'Не выполнен'}\n\n" \
                  f"💥 <b>Оценка:</b> {order.rating if order.rating else '-'}\n\n"
                  
        await call.message.edit_text(message, reply_markup=markup)
        
    else:
        markup = back_keyboard("info")
        await call.message.edit_text("🤷‍♂️ Не удалось найти информацию о заказе.", reply_markup=markup)
