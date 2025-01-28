from aiogram import Router, F
from aiogram.types import CallbackQuery
from loader import dp
from keyboards.inline.inlline_back import back_keyboard

router = Router()
dp.include_router(router)


# кнопка поддержки
@router.callback_query(F.data == 'support')
async def support_callback_handler(call: CallbackQuery):
    support_message = f'🤝 В <b>Курьер боте</b> мы ценим каждого клиента и стараемся обеспечить вам лучший возможный опыт использования нашего сервиса.\n\n' \
                      f'Если у вас возникнут вопросы или проблемы, наши сотрудники поддержки всегда на связи в Telegram.\n\n' \
                      f'🔷 Технические вопросы: \n\n' \
                      f'🔷 Вопросы по доставке или курьерам: \n\n' \
                      f'Мы всегда рады помочь вам и готовы ответить на любые ваши вопросы.\n\n' \
                      f'Спасибо за выбор <b>Курьер бота</b>! ❤️'

    await call.message.edit_text(text=support_message,
                              reply_markup=back_keyboard("mainstart"))
