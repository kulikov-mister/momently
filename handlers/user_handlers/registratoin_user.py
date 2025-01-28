from aiogram import Router, F
from aiogram.types import Message, KeyboardButton
from aiogram.fsm.context import FSMContext
from Filter.Filter import IsNotCommand
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.add_to_db import add_user
from handlers.user_handlers import main_menu_user
from keyboards.reply import reply_menu_user
from loader import dp
from states.user_states import UserRegistrationState

router = Router()
dp.include_router(router)


@router.message(IsNotCommand(), UserRegistrationState.name)
async def process_name_step(message: Message, state: FSMContext):
    # Сохраняем имя пользователя
    await state.update_data(name=message.text)

    await state.set_state(UserRegistrationState.phone)

    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='📩 Отправить контактные данные', request_contact=True)
    )
    kb = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    await message.answer('📲 Пожалуйста, поделитесь своим контактом\n\n'
                         'Для этого нажмите кнопку <b>📩 Отправить контактные данные 📩</b>\n'
                         '🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽', reply_markup=kb)


@router.message(F.contact, UserRegistrationState.phone)
async def process_phone_step(message: Message, state: FSMContext):
    # Получаем сохраненное имя пользователя
    data = await state.get_data()
    user_name = data.get('name')

    # Получаем номер телефона из контакта
    user_phone = message.contact.phone_number
    user_id = message.from_user.id

    add_user(user_id, user_name, user_phone)

    await message.answer('✅ Регистрация успешна!', reply_markup=reply_menu_user.get_main_menu_keyboard())
    await main_menu_user.main_menu(message)
