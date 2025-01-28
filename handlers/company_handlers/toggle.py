from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from keyboards.inline_builder import inline_builder
from database.database import Courier
from database.get_to_db import get_all_couriers
from loader import bot, dp

router = Router()
dp.include_router(router)

def generate_keyboard():
    couriers = get_all_couriers()
    buttons_data = [
        {"text": f"{'🟥' if courier.admin_deactivated else '🟩'} {courier.name}", 
         "callback_data": f"toggle_{courier.user_id}"}
        for courier in couriers
    ]

    return inline_builder(buttons_data)

def generate_courier_info_keyboard(courier_id: int, admin_deactivated: bool, is_pro: bool) -> InlineKeyboardMarkup:
    buttons_data = []

    if admin_deactivated:
        buttons_data.append({"text": "✳️ Активировать", "callback_data": f"activate_{courier_id}"})
    else:
        buttons_data.append({"text": "❌ Деактивировать", "callback_data": f"deactivate_{courier_id}"})

    # Пример для добавления кнопки PRO, если она требуется
    # if is_pro:
    #     buttons_data.append({"text": "🚫 Снять статус PRO", "callback_data": f"unpro_{courier_id}"})
    # else:
    #     buttons_data.append({"text": "🏅 Назначить PRO", "callback_data": f"pro_{courier_id}"})

    return inline_builder(buttons_data)


@router.callback_query(F.data == 'toggle_driver')
async def toggle_driver_activation(call: CallbackQuery):
    await call.answer()
    keyboard = generate_keyboard()
    await call.message.answer("Выберите курьера для деактивации/активации:",
                           reply_markup=keyboard)


@router.callback_query(F.data.startswith('toggle_'))
async def process_courier_toggle(call: CallbackQuery):
    """Выводит информацию о курьере и клавиатуру с кнопками активации/деактивации."""
    await call.answer()
    courier_id = int(call.data.split('_')[1])
    courier = Courier.get(Courier.user_id == courier_id)

    courier_info = generate_courier_info(courier)
    keyboard = generate_courier_info_keyboard(courier_id, courier.admin_deactivated, courier.is_pro)

    await call.message.edit_text(text=courier_info,
                                 reply_markup=keyboard)


@router.callback_query(F.data.startswith('activate_'))
async def process_courier_activation(call: CallbackQuery):
    """Активирует курьера."""
    await call.answer()
    courier_id = int(call.data.split('_')[1])
    courier = Courier.get(Courier.user_id == courier_id)
    courier.admin_deactivated = False
    courier.save()

    courier_info = generate_courier_info(courier)
    keyboard = generate_courier_info_keyboard(courier_id, courier.admin_deactivated, courier.is_pro)

    await call.message.edit_text(text=courier_info, reply_markup=keyboard)
    await bot.send_message(courier_id, "🥳 Ваша учетная запись активирована администратором!\n\n"
                                       "Теперь вы снова можете продолжать работу")




@router.callback_query(F.data.startswith('deactivate_'))
async def process_courier_deactivation(call: CallbackQuery):
    """Деактивирует курьера."""
    await call.answer()
    courier_id = int(call.data.split('_')[1])
    courier = Courier.get(Courier.user_id == courier_id)
    courier.admin_deactivated = True
    courier.save()

    courier_info = generate_courier_info(courier)
    keyboard = generate_courier_info_keyboard(courier_id, courier.admin_deactivated, courier.is_pro)

    await call.message.edit_text(text=courier_info,
                                 reply_markup=keyboard)

    await bot.send_message(courier_id, "❌ Ваша учетная запись деактивирована администратором!\n\n"
                                       "Вы больше не можете продолжать работу")


@router.callback_query(F.data.startswith('pro_'))
async def give_pro_status(call: CallbackQuery):
    """Назначает курьеру статус PRO."""
    await call.answer()
    courier_id = int(call.data.split('_')[1])
    courier = Courier.get(Courier.user_id == courier_id)
    courier.is_pro = True
    courier.save()

    courier_info = generate_courier_info(courier)
    keyboard = generate_courier_info_keyboard(courier_id, courier.admin_deactivated, courier.is_pro)

    await call.message.edit_text(text=courier_info,
                                 reply_markup=keyboard)
    await bot.send_message(courier_id, '🥳 Поздравляем! Вам присвоен статус 🏅 <b>PRO</b>')


@router.callback_query(F.data.startswith('unpro_'))
async def remove_pro_status(call: CallbackQuery):
    """Убирает у курьера статус PRO."""
    await call.answer()
    courier_id = int(call.data.split('_')[1])
    courier = Courier.get(Courier.user_id == courier_id)
    courier.is_pro = False
    courier.save()

    courier_info = generate_courier_info(courier)
    keyboard = generate_courier_info_keyboard(courier_id, courier.admin_deactivated, courier.is_pro)

    await call.message.edit_text(text=courier_info,
                                reply_markup=keyboard)

    await bot.send_message(courier_id, '😔 Ваш статус 🏅 <b>PRO</b> отключён')


def generate_courier_info(courier: Courier) -> str:
    # pro_status = "🏅 PRO" if courier.is_pro else "Стандартный"
    taxi_status = "🟥" if courier.admin_deactivated else "🟩"
    info_text = (f"👤 <b>Имя:</b> {courier.name}\n\n"
                 f"📞 <b>Телефон:</b> {courier.phone}\n\n"
                 f"⭐️ <b>Рейтинг:</b> {courier.rating}\n\n"
                 # f"🏅 <b>Статус:</b> {pro_status}\n\n"
                 f"{taxi_status} <b>Статус активации:</b> {'Активирован' if not courier.admin_deactivated else 'Деактивирован'}")
    return info_text
