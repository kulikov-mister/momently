from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline_builder import inline_builder
from database.get_to_db import get_order_by_id, get_sent_item_by_order
from handlers.courier_handlers import main_menu_courier
from loader import dp, bot
from states.order_states import OrderStatus

router = Router()
dp.include_router(router)

def get_expectation_button(order_id):
    buttons_data = [
        {"text": "🟡 Я на месте 🟡", "callback_data": f"order_expectation_{order_id}"}
    ]

    return inline_builder(buttons_data)


@router.callback_query(F.data.startswith('order_expectation_'))
async def process_order_expectation(call: CallbackQuery, state: FSMContext):
    order_id = int(call.data.split("_")[2])
    courier_id = call.from_user.id

    order = get_order_by_id(order_id)
    if order is None:
        await bot.send_message(courier_id, "Не удалось найти заказ.")
        return

    if order.courier_id != courier_id:
        await bot.send_message(courier_id, "Этот заказ не принадлежит вам.")
        return

    elif order.status == "CANCELED":
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text="⛔️ Заказ был отменен."
        )
        return

    order.status = OrderStatus.EXPECTATION
    order.save()

    sent_item = await get_sent_item_by_order(order)

    # Удалить сообщение
    await bot.delete_message(chat_id=courier_id, message_id=sent_item.text_message_id)

    # Удалить первую локацию
    await bot.delete_message(chat_id=courier_id, message_id=sent_item.start_location_message_id)

    await main_menu_courier.main_menu_courier(call.message)

    await bot.answer_callback_query(call.id, show_alert=True,
                                    text="✅ Вы прибыли к точке назначения\n\n")

    await bot.send_message(
        chat_id=order.user_id,
        text=f"🚚 Курьер на месте"
    )

    await call.answer()
