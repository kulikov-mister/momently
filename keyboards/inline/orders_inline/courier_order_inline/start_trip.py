from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.get_to_db import get_order_by_id
from keyboards.inline.orders_inline.courier_order_inline.end_trip import get_end_trip_button
from keyboards.inline_builder import inline_builder
from loader import bot, dp
from states.order_states import OrderStatus

router = Router()
dp.include_router(router)

def get_start_trip_button(order_id):
    buttons_data = [
        {"text": "🔴 В путь 🔴", "callback_data": f"order_start_trip_{order_id}"}
    ]

    return inline_builder(buttons_data)


@router.callback_query(F.data.startswith('order_start_trip_'))
async def process_start_trip(call: CallbackQuery, state: FSMContext):
    order_id = int(call.data.split("_")[3])
    courier_id = call.from_user.id

    order = get_order_by_id(order_id)
    if order is None:
        await bot.send_message(courier_id, "Не удалось найти заказ.")
        return

    if order.courier_id != courier_id:
        await bot.send_message(courier_id, "Этот заказ не принадлежит вам.")
        return

    if order.status == OrderStatus.CANCELED or order.status == OrderStatus.COMPLETED:
        await bot.send_message(call.from_user.id, "Заказ уже был отменен или завершен.")
        return

    elif order.status == "CANCELED":
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text="⛔️ Заказ был отменен."
        )
        return

    order.status = OrderStatus.TRIP
    order.save()

    await bot.answer_callback_query(call.id, show_alert=True,
                                    text="✅ Вперед и с песней")

    await bot.send_message(
        chat_id=order.user_id,
        text=f"🚚💨 Курьер уже мчит к адресу прибытия"
    )

    await bot.edit_message_reply_markup(
        chat_id=courier_id,
        message_id=call.message.message_id,
        reply_markup=get_end_trip_button(order_id)
    )

    await call.answer()
