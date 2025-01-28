from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message, KeyboardButton
from database.get_to_db import get_user, get_courier
from handlers.courier_handlers import main_menu_courier
from handlers.user_handlers import main_menu_user
from loader import dp

router = Router()
dp.include_router(router)

def get_main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🏠 Главное меню"),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)



@router.message(F.text == '🏠 Главное меню')
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
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