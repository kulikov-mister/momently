from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.delite_from_db import delete_sent_messages
from database.get_to_db import get_order_by_id, get_sent_messages
from handlers.courier_handlers.main_menu_courier import main_menu_courier
from keyboards.reply import reply_menu_user
from loader import bot, dp
from states.order_states import OrderStatus

router = Router()
dp.include_router(router)

@router.callback_query(F.data.startswith('order_acceptance_'))
async def process_order_acceptance(call: CallbackQuery, state: FSMContext):
    order_id = int(call.data.split("_")[2])
    courier_id = call.from_user.id

    order = get_order_by_id(order_id)
    if order is None:
        await bot.send_message(courier_id, "😔 Не удалось найти заказ.")
        return

    if order.courier_id is not None:
        await call.message.edit_text(text="🤷‍♂️ Заказ уже был принят другим курьером.")
        return

    elif order.status == "CANCELED":
        await call.message.edit_text(text="⛔️ Заказ был отменен.")
        return

    order.courier_id = courier_id
    order.status = OrderStatus.ACCEPTED
    order.save()

    # Удаляем сообщения у всех таксистов
    sent_messages = get_sent_messages(order.id)
    for user_id, message_id in sent_messages:
        if user_id != courier_id:
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
            except Exception as e:
                print(f"⚠️ Ошибка при удалении сообщения у пользователя {user_id}: {e}")

    delete_sent_messages(order.id)

    # Изменение текста сообщения
    await call.message.edit_text(text="✅ Вы приняли заказ!")

    await main_menu_courier(call.message)

    await bot.send_message(
        chat_id=order.user_id,
        text=f"🥳 Курьер принял Ваш заказ и уже направляется к вам!\n\n"
             f"Перейдите/обновите <b> 🏠 Главное меню </b> для просмотра актуальной информации о заказе!", reply_markup=reply_menu_user.get_main_menu_keyboard())

    await call.answer()
