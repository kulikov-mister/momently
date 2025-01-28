from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from Filter.Filter import IsNotCommand
from database.get_to_db import get_user, get_courier
from handlers.courier_handlers import main_menu_courier
from handlers.user_handlers import main_menu_user
from keyboards.inline.welcome import generate_welcome_keyboard
from keyboards.inline.inlline_back import back_keyboard
from loader import dp
from utils.set_bot_commands import set_default_commands
from states.courier_states import CourierRegistrationState
from states.user_states import UserRegistrationState

router = Router()
dp.include_router(router)


# команда старт
@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await set_default_commands(user_id)
    await state.clear()
    user = await get_user(user_id)
    courier = await get_courier(user_id)

    if user and courier:
        if courier.is_active:
            await main_menu_courier.main_menu_courier(message)
        else:
            await main_menu_user.main_menu(message)
    
    elif user:
        await main_menu_user.main_menu(message)
    
    elif courier:
        await main_menu_courier.main_menu_courier(message)
    
    else:
        welcome_message = "🎉 Добро пожаловать в <b>Курьер бота</b>! 🎉\n\n" \
                          "🚀 Мы рады, что Вы доверяете нам 🥰.\n\n" \
                          "🙃 В каком статусе хотите присоединиться к нам?"
        await message.reply(welcome_message, reply_markup=generate_welcome_keyboard(), reply=False)


# кнопка назад
@router.callback_query( F.data==('mainstart') )
async def start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    await state.clear()
    user = await get_user(user_id)
    courier = await get_courier(user_id)
    
    if user and courier: # если как пользователь и курьер одновременно
        if courier.is_active:
            await main_menu_courier.main_menu_courier(call)
        else:
            await main_menu_user.main_menu(call)
    
    elif courier: # если как курьер
        await main_menu_courier.main_menu_courier(call)
    
    elif user: # если как пользователь
        await main_menu_user.main_menu(call)
    
    else: # если не зарегистрирован
        welcome_message = "🎉 Добро пожаловать в <b>Курьер бота</b>! 🎉\n\n" \
                          "🚀 Мы рады, что Вы доверяете нам 🥰.\n\n" \
                          "🙃 В каком статусе хотите присоединиться к нам?"
        await call.message.edit_text(welcome_message, reply_markup=generate_welcome_keyboard())


# регистрация юзера
@router.callback_query(F.data == 'user')
async def process_callback_user(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text('🔆 Введите ваше имя:')
    await state.set_state(UserRegistrationState.name)


# регистрация курьера
@router.callback_query(F.data == 'courier')
async def process_callback_courier(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text('🔆 Введите ваше имя:')
    await state.set_state(CourierRegistrationState.name)
