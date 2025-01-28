from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from Filter.Filter import IsNotCommand, LinkNumberFilter
from database.add_to_db import save_sent_messages
from database.get_to_db import get_order_by_id, get_courier
from handlers.default_handlers.start import start
from keyboards.inline.orders_inline.user_order_inline.comment import comment_keyboard
from keyboards.inline.courier_inline.accept_the_order import order_acceptance_keyboard_without_propose_price
from keyboards.inline.orders_inline.user_order_inline.accept_or_decline_price import accept_or_decline_price_keyboard
from loader import dp, bot
from states.order_states import ProposePriceState
from config_data.config import CURRENCY

router = Router()
dp.include_router(router)

# кнопка предложить цену
@router.callback_query(F.data.startswith('order_propose_price'))
async def process_propose_price_callback(call: CallbackQuery, state: FSMContext):
    order_id = call.data.split('_')[-1]
    await state.set_state(ProposePriceState.price)
    await state.update_data(order_id=order_id)

    order = get_order_by_id(order_id)
    
    keyboard = order_acceptance_keyboard_without_propose_price(order)
    await call.message.edit_reply_markup(reply_markup=keyboard)

    await bot.send_message(call.from_user.id, '💰 Введите вашу цену:')
    await call.answer()


# предложение цены
@router.message(IsNotCommand(), ProposePriceState.price)
async def process_propose_price_request_coment(message: Message, state: FSMContext):
    message_text = message.text
    if message_text.startswith('🏠 Главное меню'):
        await start(message, state)
        return

    if message_text.replace('.', '', 1).isdigit() and message_text.count('.') <= 1:
        price = float(message_text)
        if price <= 0:
            await message.answer("Цена должна быть положительным числом.")
            return
        # Далее обработка корректной цены
    else:
        await message.answer("Пожалуйста, введите допустимое числовое значение для цены.")
        return
    
    await state.update_data(price=price)
    await message.answer("✍️ Желаете оставить комментарий по поводу Вашего предложения? \n\n<i>Желательно обосновать своё предложение - это повысит шансы на согласие.</i>",
                         reply_markup=comment_keyboard())
    await state.set_state(ProposePriceState.coment)

# предлжение оставить коментарий к цене
@router.message(IsNotCommand(), ProposePriceState.coment, LinkNumberFilter())
async def process_propose_price(message: Message, state: FSMContext):
    courier_id = message.from_user.id
    coment = message.text
    
    # Получаем данные из state
    data = await state.get_data()
    order_id = data.get('order_id')
    price = str(data.get('price'))
    
    order = get_order_by_id(order_id)
    courier = await get_courier(courier_id)
    pro_status = " | PRO 🏅" if courier.is_pro else ""
    
    if courier is None:
        await message.answer("⚠️ Ошибка: курьер не найден.")
        return
    
    await bot.send_message(message.from_user.id, f"✅ Предложение цены {price} {CURRENCY} с комментарием:\n<i>{coment}</i>\n\nотправлено клиенту")
    message = await bot.send_message(order.user_id, f'🔔 Курьер <b>{courier.name}{pro_status}</b> предлагает цену <b>{price}</b>{CURRENCY} за ваш заказ',
                           reply_markup=accept_or_decline_price_keyboard(order, courier_id, price))

    # Сохраняем отправленное сообщение
    save_sent_messages(order.id, [(order.user_id, message.message_id)])
