from aiogram import F, Router
from aiogram.types import CallbackQuery
from database.get_to_db import get_courier
from keyboards.inline.courier_inline.markup_main_courier import markup_main_courier
from loader import dp

router = Router()
dp.include_router(router)

@router.callback_query(F.data == 'toggle_active')
async def process_toggle_active_callback(call: CallbackQuery):
    user_id = call.from_user.id
    courier = await get_courier(user_id)
    if courier:
        courier.is_active = not courier.is_active
        courier.save()
        await call.answer(text=f"{'👷 За работу. Вы можете получать заказы' if courier.is_active else '🚬 На перекур. Вы не будете получать заказы'}", show_alert=True)
        await call.message.edit_reply_markup(reply_markup=markup_main_courier(courier))
    else:
        await call.answer("⚠️ Вы не являетесь курьером.")
