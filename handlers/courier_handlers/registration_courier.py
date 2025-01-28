from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from Filter.Filter import IsNotCommand
from database.add_to_db import add_courier
from database.database import Location
from handlers.courier_handlers import main_menu_courier
from keyboards.inline.location_courier import create_location_keyboard
from keyboards.reply.sent_contact import create_contact_keyboard
from loader import dp, bot
from states.courier_states import CourierRegistrationState

router = Router()
dp.include_router(router)

@router.message(IsNotCommand(), CourierRegistrationState.name)
async def process_name_step(message: Message, state: FSMContext):
    await state.update_data(name=message.text, user_id=message.from_user.id)

    await state.set_state(CourierRegistrationState.phone)

    contact_keyboard = create_contact_keyboard('📩 Отправить контактные данные')
    await message.answer('📲 Пожалуйста, поделитесь своим контактом\n\n'
                         'Для этого нажмите кнопку <b>📩 Отправить контактные данные 📩</b>\n'
                         '🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽', reply_markup=contact_keyboard)


@router.message(F.contact, CourierRegistrationState.phone)
async def process_phone_step(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)

    await state.set_state(CourierRegistrationState.location)

    locations = Location.select()
    locations_data = [(loc.name, loc.latitude, loc.longitude) for loc in locations]
    inline_kb = create_location_keyboard(locations_data)

    await message.answer("Выберите свою локацию из списка ниже:", reply_markup=inline_kb)


@router.callback_query(F.data.startswith('location:'), CourierRegistrationState.location)
async def process_callback_location(call: CallbackQuery, state: FSMContext):
    _, lat, lon = call.data.split(':')
    location = Location.get(Location.latitude == float(lat), Location.longitude == float(lon))
    
    # Получаем данные из состояния
    data = await state.get_data()
    user_id = data.get('user_id')
    user_name = data.get('name')
    user_phone = data.get('phone')

    await call.answer()

    add_courier(user_id, user_name, user_phone, location)

    await call.message.edit_text(f"✅ Добро пожаловать в нашу команду!")

    await main_menu_courier.main_menu_courier(call.message)
