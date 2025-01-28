from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config_data.config import geolocator
from database.add_to_db import add_location_to_db
from Filter.Filter import IsNotCommand
from keyboards.inline.adresses import create_address_keyboard
from keyboards.reply.orders_reply.send_location import send_location_keyboard
from keyboards.reply.reply_menu_user import get_main_menu_keyboard
from loader import dp
from states.admin_states import CompanyState
from utils.get_adresses import get_sorted_address

router = Router()
dp.include_router(router)

# запрос локаций
@router.callback_query(F.data == 'add_location')
async def location_request(call: CallbackQuery, state: FSMContext):
    await state.update_data(admin_id=call.from_user.id)
    await call.message.answer("<b>Пожалуйста, введите название локации, которую вы хотите добавить:</b> \n\n"
                              "(Город, область, район итд)\n"
                              "Курьеры, прикрепленные к ней, будут получать заказы, при выборе данной локации пользователем!")
    await state.set_state(CompanyState.LOCATION_NAME)

# обработка названия локации из текста
@router.message(F.text, IsNotCommand(), CompanyState.LOCATION_NAME)
async def handle_location_name(message: Message, state: FSMContext):
    state_data = await state.get_data()
    state_data["name_location"] = message.text

    await state.set_data(state_data)
    await message.answer(
        "📍 Отправьте геолокацию для '{}' или введите адрес и выберите из предложенных вариантов.".format(message.text),
        reply_markup=send_location_keyboard())
    await state.set_state(CompanyState.LOCATION)

# прием локации из местоположения
@router.message(CompanyState.LOCATION, F.content_type.in_(['location', 'venue']))
async def handle_location(message: Message, state: FSMContext):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        state_data = await state.get_data()
        state_data["latitude"] = latitude
        state_data["longitude"] = longitude

        await state.set_data(state_data)
        add_location_to_db(state_data)
        await message.answer("✅ Локация успешно добавлена.")
    elif message.venue:
        latitude = message.venue.location.latitude
        longitude = message.venue.location.longitude

        state_data = await state.get_data()
        state_data["latitude"] = latitude
        state_data["longitude"] = longitude

        await state.set_data(state_data)
        add_location_to_db(state_data)
        await message.answer("✅ Локация успешно добавлена.")
    else:
        await handle_location_text(message, state)

# локация из списка
@router.message(IsNotCommand(), CompanyState.LOCATION)
async def handle_location_text(message: Message, state: FSMContext):
    location = await geolocator.geocode(message.text, exactly_one=False)
    if not location:
        await message.answer("Не удалось найти этот адрес. Пожалуйста, попробуйте ещё раз.")
        return

    locations_data = [
        (get_sorted_address(loc.address), loc.latitude, loc.longitude) for loc in location
    ]
    await state.set_data({'locations_data': locations_data})
    inline_kb = create_address_keyboard(locations_data, 1, "mainstart_company", "LOCATION")
    
    await message.answer("Выберите правильный адрес из списка ниже:", reply_markup=inline_kb)

# выбор локации из кнопок
@router.callback_query(F.data.startswith("location:"), CompanyState.LOCATION)
async def handle_location_callback_admin(call: CallbackQuery, state: FSMContext):
    _, lat, lon = call.data.split(":")
    latitude = float(lat)
    longitude = float(lon)

    state_data = await state.get_data()
    state_data["latitude"] = latitude
    state_data["longitude"] = longitude

    add_location_to_db(state_data)
    await call.message.edit_text(
        f"✅ Локация успешно добавлена.",
        reply_markup=get_main_menu_keyboard()
        )
