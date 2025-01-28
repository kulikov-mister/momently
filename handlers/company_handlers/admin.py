from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from Filter.Filter import IsAdmin
from handlers.user_handlers import main_menu_user
from keyboards.inline.admin_markup import markup_admin
from loader import dp


router = Router()
dp.include_router(router)


# команда admin
@router.message(Command('admin'))
async def admin(message: Message):
    await message.answer('🔑 Вы авторизованы как Админ',
        reply_markup=markup_admin())


# кнопка назад из админки
@router.callback_query(F.data==('mainstart_company'))
async def mainstart_company(call: CallbackQuery):
    await call.message.edit_text('🔑 Вы авторизованы как Админ',
        reply_markup=markup_admin())


# обычная кнопка назад
@router.callback_query(F.data==('mainstart'))
async def mainstart(call: CallbackQuery):
    await main_menu_user.main_menu(call)