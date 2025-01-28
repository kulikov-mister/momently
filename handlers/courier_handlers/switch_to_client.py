from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.get_to_db import get_courier, get_user
from handlers.user_handlers import main_menu_user
from loader import bot, dp
from states.user_states import UserRegistrationState

router = Router()
dp.include_router(router)

@router.callback_query(F.data == 'switch_to_client')
async def process_callback_switch_to_passenger(call: CallbackQuery, state: FSMContext):
    await call.answer()
    user_id = call.from_user.id
    courier = await get_courier(user_id)

    if courier:
        courier.is_active = False
        courier.save()

    user = await get_user(user_id)
    if user:
        # если да, переходим в главное меню пассажиров
        await call.message.edit_text('🔀 Вы сменили роль на клиент. Добро пожаловать!')
        await main_menu_user.main_menu(call.message)
    else:
        # если нет, начинаем процесс регистрации пассажира
        await call.message.edit_text('🙋‍♂️Вам нужно пройти регистрацию клиента!\n\n'
                                    '🔆 Введите ваше имя:')
        await state.set_state(UserRegistrationState.name)
