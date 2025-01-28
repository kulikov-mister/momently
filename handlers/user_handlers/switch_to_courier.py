from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.get_to_db import get_courier
from handlers.courier_handlers import main_menu_courier
from loader import bot, dp
from states.courier_states import CourierRegistrationState

router = Router()
dp.include_router(router)

# кнопка переключения ролией: курьер/пользователь
@router.callback_query(F.data == 'switch_to_courier')
async def process_callback_switch_to_taxi(call: CallbackQuery, state: FSMContext):
    await call.answer()
    user_id = call.from_user.id
    courier = await get_courier(user_id)

    if courier:
        if not courier.admin_deactivated:
            courier.is_active = True  # активируем таксиста
            courier.save()

            await call.message.edit_text('🔀 Вы сменили роль на курьера. Добро пожаловать!')
            await main_menu_courier.main_menu_courier(call)  # передаем call вместо message
        else:
            await call.message.edit_text('🚫 Ваш аккаунт курьера деактивирован администратором.')
    else:
        await call.message.edit_text(
            '🚖 Мы рады, что вы решили стать частью нашей команды! 🎉\n\n'
            '👨 Вам нужно зарегистрироваться в качестве курьера\n\n'
            '🔆 Введите ваше имя:')
        await state.set_state(CourierRegistrationState.name)