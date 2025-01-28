from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_builder import inline_builder
from config_data.config import ADMIN_IDS
from database.delite_from_db import delete_sent_messages
from database.get_to_db import get_order_by_id, get_sent_messages
from loader import dp, bot
from states.order_states import OrderStatus

router = Router()
dp.include_router(router)

def cancel_order_buttons(order_id: int) -> InlineKeyboardMarkup:
    buttons_data = [{"text": "❌ Отменить заказ ❌", "callback_data": f"cancel_order_{order_id}"}]
    return inline_builder(buttons_data)


@router.callback_query(F.data.startswith('cancel_order_'))
async def cancel_order(call: CallbackQuery, state: FSMContext):
    order_id = int(call.data.split("_")[2])
    order = get_order_by_id(order_id)
    if order is None:
        await bot.send_message(call.from_user.id, "Не удалось найти заказ.")
        return

    if call.from_user.id not in ADMIN_IDS and order.status not in ['ACCEPTED', 'GENERATED']:
        await bot.answer_callback_query(call.id, show_alert=True,
                                        text="❗ Извините, но вы не можете отменить этот заказ в текущем статусе, обратитесь в службу поддержки: @wei_outsourcing.")
        return

    order.status = OrderStatus.CANCELED
    order.save()

    user_id = order.user_id
    courier = order.courier_id

    # Удаляем сообщения у всех курьеров
    sent_messages = get_sent_messages(order.id)
    for courier_id, message_id in sent_messages:
        if courier_id != courier:
            try:
                await bot.delete_message(chat_id=courier_id, message_id=message_id)
            except Exception as e:
                print(f"⚠️ Ошибка при удалении сообщения у пользователя {courier_id}: {e}")

    delete_sent_messages(order.id)

    if call.from_user.id in ADMIN_IDS:
        await call.answer(show_alert=True, text="✅ Заказ отменён ")

    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                text="😔 Ваш заказ был отменен.")

    if courier:
        await bot.send_message(courier, f"😒 Заказ № {order.id} был отменен.")

