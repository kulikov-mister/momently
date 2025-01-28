# keyboards/cb_pagination.py
import logging
from loader import dp
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.database import Order, Location
from keyboards.inline.adresses import create_address_keyboard
from keyboards.inline_builder import get_paginated_keyboard, get_inline_orders
from keyboards.inline.location_courier import create_location_keyboard


router = Router()
dp.include_router(router)


# хендлер на переключение страниц на всех функциях
@router.callback_query(F.data.startswith("page:"))
async def query_page_navigation(call: CallbackQuery, state: FSMContext):
    logging.info(call.data)
    user_id = call.from_user.id
    parts = call.data.split(":")
    cb_prefix = parts[1]
    page = int(parts[-1])

    # data = await state.get_data()
    # current_level = data.get("current_level", 1)


    if cb_prefix == "u_orders":
        # Обновление текущей страницы в состоянии
        await state.update_data({"current_page": page})
        orders = Order.select().where(Order.user_id == user_id)
        markup = get_paginated_keyboard(get_inline_orders(orders), page, 'mainstart', cb_prefix)

    elif cb_prefix == "с_orders":
        # Обновление текущей страницы в состоянии
        await state.update_data({"current_page": page})
        orders = Order.select().where(Order.courier_id == user_id)
        markup = get_paginated_keyboard(get_inline_orders(orders), page, 'mainstart', cb_prefix)
        
    elif cb_prefix == "order":
        # перелистывание при новом заказе
        locations = Location.select()
        locations_data = [(loc.name, loc.latitude, loc.longitude) for loc in locations]
        markup = create_location_keyboard(locations_data, page, "mainstart", cb_prefix)
        
    elif cb_prefix == "LOCATION":
        # Обновление текущей страницы в состоянии
        state_data = await state.get_data()
        
        locations_data = state_data.get('locations_data')
        if not locations_data:
            await call.message.edit_text("Нет данных")
            return
        await state.update_data({"current_page": page})
        markup = create_address_keyboard(locations_data, page, "mainstart", cb_prefix)
        
    if markup:
        await call.message.edit_reply_markup(reply_markup=markup)
        await call.answer(f"Страница {page}")
    else:
        await call.answer("Ошибка в навигации по страницам.")
    return
