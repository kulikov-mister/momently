from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from Filter.Filter import IsNotCommandInStates, LinkNumberFilter
from database.delite_from_db import delete_sent_messages
from database.get_to_db import get_order_by_id, get_courier, get_sent_messages
from handlers.user_handlers import main_menu_user
from keyboards.inline.orders_inline.user_order_inline.comment import comment_keyboard
from keyboards.reply.reply_menu_courier import courier_main_menu_keyboard
from loader import dp, bot
from states.order_states import OrderStatus
from config_data.config import CURRENCY

router = Router()
dp.include_router(router)

# принятие цены и запрос комментария
@router.callback_query(F.data.startswith('acceptprice_'))
async def process_accept_price_callback(call: CallbackQuery):
    _, order_id, courier_id, price = call.data.split("_", 3)
    order_id = int(order_id)
    courier_id = int(courier_id)
    user_id = call.from_user.id

    order = get_order_by_id(order_id)
    if order is None:
        await call.message.answer( "😔 Не удалось найти заказ.")
        return

    courier = await get_courier(courier_id)
    if courier is None:
        await call.message.answer("⚠️ Ошибка: курьер не найден.")
        return

    order.courier_id = courier_id
    order.cost = price  # assign the proposed price to the order
    order.status = OrderStatus.ACCEPTED
    order.save()

    await call.message.edit_text(f"✅ Вы приняли предложение по цене {order.cost} {CURRENCY} от курьера {courier.name}!")

    await main_menu_user.main_menu(call.message)

    # отправляем уведомление курьеру
    await bot.send_message(
        courier_id, 
        f"🥳 Пользователь принял ваше предложение по цене {order.cost} {CURRENCY}!\n\n"
        f"Перейдите в главное меню для просмотра информации о заказе", 
        reply_markup=courier_main_menu_keyboard())

    sent_messages = get_sent_messages(order.id)
    for user_id, message_id in sent_messages:
        try:
            await bot.delete_message(user_id, message_id)
        except Exception as e:
            print(f"⚠️ Ошибка при удалении сообщения у пользователя {user_id}: {e}")
    delete_sent_messages(order.id)
    await call.answer()


# прием цены и запрос коментария
@router.callback_query(F.data.startswith('declineprice'))
async def process_request_coment_price_callback(call: CallbackQuery, state: FSMContext):
    _, order_id, courier_id, price = call.data.split("_", 3)

    await state.update_data(order_id=order_id, courier_id=courier_id, price=price)    
    await call.message.edit_reply_markup(reply_markup=ReplyKeyboardRemove()) #чистим клавиатуру
    await call.message.answer("✍️ Желаете оставить комментарий по поводу отклонения предложения? :",
                              reply_markup=comment_keyboard())
    await call.answer()
    await state.set_state(OrderStatus.PRICE_CANCELED)
    
# приянтие коментария и отправка сообщения курьеру
@router.message(IsNotCommandInStates(OrderStatus.PRICE_CANCELED), LinkNumberFilter())
async def process_decline_price_comment(message: Message, state: FSMContext):
    comment = message.text
    # Получите данные о заказе из состояния
    data = await state.get_data()
    order_id = data.get('order_id')
    courier_id = data.get('courier_id')
    price = data.get('price')
    
    order = get_order_by_id(order_id)
    if order is None:
        await message.answer("😔 Не удалось найти заказ.")
        return

    courier = await get_courier(courier_id)
    if courier is None:
        await message.answer("⚠️ Ошибка: курьер не найден.")
        return

    await message.answer(
        text=f'😤 Вы отклонили предложение курьера <b>{courier.name}</b> с ценой <b>{price} {CURRENCY}</b>.',
        reply_markup=None)

    await bot.send_message(
        courier_id,
        text=f'''😔 Ваше предложение c ценой <b>{price}</b> по заказу <b>{order_id}</b> было отклонено.\n\n
                 <b>Клиент указал комментарий:</b>.{comment}\n\n
                 Теперь вы можете принять заказ только на условиях клиента!''')
    
