from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline_builder import inline_builder
from keyboards.inline.inlline_back import back_keyboard
from database.database import Location, Courier
from handlers.courier_handlers import main_menu_courier
from loader import dp

router = Router()
dp.include_router(router)

@router.callback_query(F.data == 'change_location')
async def change_location_request(call: CallbackQuery):
    locations = Location.select()

    buttons_data = [
        {"text": location.name, "callback_data": f"set_location_{location.name}"}
        for location in locations
    ]
    inline_kb = inline_builder(buttons_data)

    await call.message.edit_text("💫 Выберите новую локацию.", reply_markup=inline_kb)


@router.callback_query(F.data.startswith('set_location_'))
async def set_location(call: CallbackQuery):
    location_name = call.data.split("_")[2]
    location = Location.get(name=location_name)

    courier = Courier.get(user_id=call.from_user.id)
    courier.location = location
    courier.save()

    await call.message.edit_text(f"✅ Ваша новая локация: <b>{location_name}</b>.",
                                 reply_markup=back_keyboard("mainstart"))
    await main_menu_courier.main_menu_courier(call)
