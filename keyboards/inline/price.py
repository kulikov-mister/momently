from aiogram import Router, F
from aiogram.types import CallbackQuery
from loader import dp, bot
from keyboards.inline.inlline_back import back_keyboard
from config_data.config import CURRENCY

router = Router()
dp.include_router(router)

price_list = (
    "🚀 <b>Мы рады предложить вам наши услуги.</b>\n\n"
    "🎯 Наша цель - доставить ваш заказ быстро и аккуратно.\n\n"
    "📜 <b>Вот наши тарифы:</b>\n\n\n"
    f"📏 До 2 км: 140 {CURRENCY}\n\n"
    f"📏 2 км: 160 {CURRENCY}\n\n"
    f"📏 3 км: 170 {CURRENCY}\n\n"
    f"📏 4 км: 180 {CURRENCY}\n\n"
    f"📏 5 км: 190 {CURRENCY}\n\n"
    f"📏 6 км: 200 {CURRENCY}\n\n"
    f"📏 7 км: 210 {CURRENCY}\n\n"
    f"📏 8 км: 220 {CURRENCY}\n\n"
    f"📏 9 км: 230 {CURRENCY}\n\n"
    f"📏 От 10 км: 240 {CURRENCY}\n\n\n"
    "🚚💨 Стоимость доставки зависит от расстояния, которое нужно преодолеть нашему курьеру, чтобы доставить ваш заказ.\n\n"
    "❤️ Спасибо, что выбрали наш сервис! Мы всегда готовы к сотрудничеству! 🤝\n\n"
    "Если у вас возникнут вопросы, не стесняйтесь обращаться к нам! Мы всегда готовы помочь! 😊👍")


@router.callback_query(F.data == 'price')
async def send_price_list(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(text=price_list,
                              reply_markup=back_keyboard("mainstart"))
