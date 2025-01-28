from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.get_to_db import get_order_by_id, get_sent_item_by_order, get_courier
from handlers.courier_handlers import main_menu_courier
from keyboards.inline.orders_inline.user_order_inline.rating import get_rating_keyboard
from keyboards.inline_builder import inline_builder
from loader import dp, bot
from states.order_states import OrderStatus

router = Router()
dp.include_router(router)

def get_end_trip_button(order_id):

    buttons_data = [
        {"text": "🟢 Посылка доставлена 🟢", "callback_data": f"order_end_trip_{order_id}"}
    ]

    return inline_builder(buttons_data)

@router.callback_query(F.data.startswith('order_end_trip_'))
async def process_order_end_trip(call: CallbackQuery, state: FSMContext):
    order_id = int(call.data.split("_")[3])
    order = get_order_by_id(order_id)
    courier_id = call.from_user.id


    if order is None:
        await bot.send_message(call.from_user.id, "Не удалось найти заказ.")
        return

    if order.status == "COMPLETED":
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text="⛔️"
        )
        return

    elif order.status == "CANCELED":
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text="⛔️ Заказ был отменен."
        )
        return

    order.status = OrderStatus.COMPLETED
    order.save()


    sent_item = await get_sent_item_by_order(order)

    # Удалить сообщение
    await bot.delete_message(chat_id=courier_id, message_id=sent_item.text_message_id)

    # Удалить вторую локацию
    await bot.delete_message(chat_id=courier_id, message_id=sent_item.end_location_message_id)

    await main_menu_courier.main_menu_courier(call.message)

    await bot.answer_callback_query(call.id, show_alert=True,
                                    text="✅ Посылка доставлена")

    await bot.send_message(
        chat_id=order.user_id,
        text="✅ Ваша посылка доставлена!\n\n\n"
             "🤗 Благодарим за использование нашего сервиса!\n"
             "Надеемся, что вам понравилось 😍\n\n"
             "🌠 Оцените пожалуйста работу курьера",
        reply_markup=get_rating_keyboard(order.id)
    )

