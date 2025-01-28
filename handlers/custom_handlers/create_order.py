import time, logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from Filter.Filter import IsNotCommand, IsNotCommandInStates, IsStates
from geopy.distance import geodesic

from config_data.config import geolocator, cost_per_km, BING_MAPS_KEY
from database.add_to_db import create_order_in_db
from database.database import Location
from database.get_to_db import get_order_by_user_id
from handlers.default_handlers.start import start
from keyboards.inline.adresses import create_address_keyboard
from keyboards.inline.location_courier import create_location_keyboard
from keyboards.inline.orders_inline.user_order_inline.comment import comment_keyboard
from keyboards.inline.orders_inline.user_order_inline.payment_method import payment_keyboard
from keyboards.reply.orders_reply.send_location import send_location_keyboard
from keyboards.reply.reply_menu_user import get_main_menu_keyboard
from loader import dp, bot
from states.order_states import CourierOrderState
from utils import message_for_courier
from utils.get_adresses import get_sorted_address, search_address
from utils.get_distance import get_distance_and_duration_ms
from utils.order_detail import calculate_order_details
from utils.validate_data import validate_order_data

router = Router()
dp.include_router(router)

# создание нового ордера
@router.callback_query(F.data == 'order')
async def location_request(call: CallbackQuery, state: FSMContext):
    await state.update_data(user_id=call.from_user.id)
    locations = Location.select()
    locations_data = [(loc.name, loc.latitude, loc.longitude) for loc in locations]
    inline_kb = create_location_keyboard(locations_data, 1, "mainstart", call.data)

    await call.message.edit_text("Выберите свою локацию из списка ниже:", reply_markup=inline_kb)
    await state.set_state(CourierOrderState.LOCATION)

# полцесс выбора места для заказа
@router.callback_query(F.data.startswith('location:'), CourierOrderState.LOCATION)
async def process_callback_location(call: CallbackQuery, state: FSMContext):
    _, lat, lon = call.data.split(':')
    location = Location.get(Location.latitude == float(lat), Location.longitude == float(lon))

    # Устанавливаем значение в state напрямую
    await state.update_data(location_id=location.id)

    await call.answer()
    await call.message.delete()
    await call.message.answer(
        "📍📦 <b>Откуда забрать посылку?</b>\n\n"
        "Вы можете выбрать один из следующих вариантов:\n\n"
        "🔅 <b>Ввести адрес текстом и выбрать предложенный вариант</b> (Пример: Москва, Красная площадь, 1)\n\n"
        "🔅 <b>Отправить геолокацию места прибытия:</b>\n\n"
        "Для этого нажмите на иконку '📎' (Скрепка), затем выберите '📍' (Геопозиция) и укажите точку на карте.\n\n",
        reply_markup=send_location_keyboard()
    )
    await state.set_state(CourierOrderState.FIRST_LOCATION)

# первая локация в виде местоположения
@router.message(CourierOrderState.FIRST_LOCATION, F.content_type.in_({'location', 'venue'}))
async def handle_first_location(message: Message, state: FSMContext):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
    elif message.venue:
        latitude = message.venue.location.latitude
        longitude = message.venue.location.longitude
    else:
        await message.answer("Не удалось получить локацию. Пожалуйста, попробуйте ещё раз.")
        return
    state_data = await state.get_data()
    state_data["first_latitude"] = latitude
    state_data["first_longitude"] = longitude
    await state.set_data(state_data)

    await message.answer("⛳️<b> Куда едем?</b>\n\n"
                         "Вы можете выбрать один из следующих вариантов:\n\n"
                         "🔅 <b>Ввести адрес текстом и выбрать предложенный вариант</b> (Пример: Москва, Красная площадь, 1)\n\n"
                         "🔅 <b>Отправить геолокацию места прибытия:</b>\n\n"
                         "Для этого нажмите на иконку '📎' (Скрепка), затем выберите '📍' (Геопозиция) и укажите точку на карте.\n\n",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(CourierOrderState.SECOND_LOCATION)

# втоая локация в виде местоположения
@router.message(CourierOrderState.SECOND_LOCATION, F.content_type.in_(['location', 'venue']))
async def handle_second_location(message: Message, state: FSMContext):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
    elif message.venue:
        latitude = message.venue.location.latitude
        longitude = message.venue.location.longitude
    else:
        await message.answer("Не удалось получить локацию. Пожалуйста, попробуйте ещё раз.")
        return
    state_data = await state.get_data()
    state_data["second_latitude"] = latitude
    state_data["second_longitude"] = longitude
    await state.set_data(state_data)
    print(state_data)
    await message.answer("💸 Выберите способ оплаты", reply_markup=payment_keyboard())
    await state.set_state(CourierOrderState.PAYMENT_METHOD)

    
# процесс выбора адреса в кнопке
@router.callback_query(F.data.startswith('location:'), IsStates([CourierOrderState.FIRST_LOCATION, CourierOrderState.SECOND_LOCATION]) )
async def handle_location_callback(call: CallbackQuery, state: FSMContext):
    _, lat, lon = call.data.split(":")
    latitude = float(lat)
    longitude = float(lon)
    current_state = await state.get_state()

    if current_state == CourierOrderState.FIRST_LOCATION:
        await state.update_data(first_latitude=latitude, first_longitude=longitude)
        msg = """⛳️ Куда едем?\n\n
          Вы можете выбрать один из следующих вариантов:
          🔅 <b>Ввести адрес текстом и выбрать предложенный вариант</b> (Пример: Москва, Красная площадь, 1)
          🔅 <b>Отправить геолокацию места прибытия:</b>
          Для этого нажмите на иконку '📎' (Скрепка), затем выберите '📍' (Геопозиция) и укажите точку на карте."""
        inline_kb = ReplyKeyboardRemove()
        
        try:
            await call.message.edit_text(msg, reply_markup=inline_kb)
        except:
            await call.message.delete()
            await call.message.answer(msg, reply_markup=inline_kb)
        await state.set_state(CourierOrderState.SECOND_LOCATION)
    
    elif current_state == CourierOrderState.SECOND_LOCATION:
        await state.update_data(second_latitude=latitude, second_longitude=longitude)
        msg = "💸 Выберите способ оплаты"
        inline_kb = payment_keyboard()
    
        try:
            await call.message.edit_text(msg, reply_markup=inline_kb)
        except:
            await call.message.delete()
            await call.message.answer(msg, reply_markup=inline_kb)
    
        await state.set_state(CourierOrderState.PAYMENT_METHOD)


# Процесс выбора локации из введенного текста
@router.message( IsNotCommandInStates([CourierOrderState.SECOND_LOCATION, CourierOrderState.FIRST_LOCATION]) )
async def handle_location_text(message: Message, state: FSMContext):
    locations_data = await search_address(message.text, BING_MAPS_KEY)
    print(locations_data)
    if not locations_data:
        await message.answer("Не удалось найти этот адрес. Пожалуйста, попробуйте ещё раз.")
        return
    
    await state.update_data({'locations_data': locations_data})
    inline_kb = create_address_keyboard(locations_data, 1, "mainstart", "LOCATION")
    await message.answer("Выберите правильный адрес из списка ниже:", reply_markup=inline_kb)

# процесс выбора метода платежа
@router.callback_query(F.data.in_(["cash", "transfer"]), CourierOrderState.PAYMENT_METHOD)
async def handle_payment(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    state_data["payment_method"] = call.data
    await state.set_data(state_data)

    await call.message.delete()
    await call.message.answer("✍️ Желаете оставить комментарий к заказу? :",
                              reply_markup=comment_keyboard())
    await state.set_state(CourierOrderState.COMMENT)

# завершение и создание заказа
@router.message(IsNotCommand(), CourierOrderState.COMMENT)
async def handle_comment(message: Message, state: FSMContext):
    if message.text.startswith('🏠 Главное меню'):
        await start(message, state)
        return

    state_data = await state.get_data()
    state_data["comment"] = message.text if message.text != "⛔️ Без комментариев" else "-"

    first_location = (state_data["first_latitude"], state_data["first_longitude"])
    second_location = (state_data["second_latitude"], state_data["second_longitude"])
    distance, duration = await get_distance_and_duration_ms(first_location, second_location, BING_MAPS_KEY)
    if distance is None or duration is None:
        await message.answer("Не удалось рассчитать расстояние и время. Пожалуйста, попробуйте ещё раз.")
        return


    cost = distance * cost_per_km

    state_data["distance"] = distance
    state_data["cost"] = cost

    await state.set_data(state_data)
    if not validate_order_data(state_data):
        return await message.answer("Данных не хватает! Начните сначала.")
    
    # создаем заказ в базе данных и получаем его
    create_order_in_db(state_data)
    user_id = message.chat.id
    order = get_order_by_user_id(user_id)

    if order:
        first_address, second_address = await calculate_order_details(order)
        if first_address and second_address:
            await message.answer("👍 Заказ создан!\n\n"
                                "Когда курьер примет заказ или предложит стоимость, мы вас оповестим!\n\n"
                                "Перейдите/обновите <b> 🏠 Главное меню </b> для просмотра актуальной информации о заказе!",
                                reply_markup=get_main_menu_keyboard())
            time.sleep(2)
            await message.answer("👀 Ищу для вас самого лучшего ")

            # вызываем функцию для оповещения водителей
            await message_for_courier.notify_couriers(order, first_address, second_address, distance, cost)
        
        else:
            await message.answer("Невозможно построить маршрут")
    else:
        await message.answer(
            "⚠️ Произошла ошибка при сохранении заказа. Пожалуйста, начните заказ заново.",
            reply_markup=get_main_menu_keyboard())
