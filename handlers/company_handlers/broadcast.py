from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config_data import config
from config_data.config import ADMIN_IDS
from database.get_to_db import get_all_unique_users
from loader import dp, bot
from states.admin_states import CompanyState

router = Router()
dp.include_router(router)

@router.callback_query(F.data == 'admin_broadcast')
async def admin_broadcast(call: CallbackQuery, state: FSMContext):
    await state.update_data(user_id=call.from_user.id)
    await call.message.answer("✍️ Введите сообщение для рассылки")
    await state.set_state(CompanyState.BROADCAST)


@router.message(CompanyState.BROADCAST)
async def process_broadcast_message(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        return
    broadcast_message = message.text
    unique_users = get_all_unique_users()
    for user_id in unique_users:
        if user_id not in ADMIN_IDS:  # пропускаем админа
            await bot.send_message(user_id, broadcast_message)  # отправляем сообщение каждому пользователю
    await message.answer("✅ Сообщения отправлены")

