from typing import List, Tuple
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_builder import get_paginated_keyboard

from loader import dp

router = Router()
dp.include_router(router)

def create_address_keyboard(locations: List[Tuple[str, float, float]], page, back_callback_data, cb_prefix, items_per_page:int = 7) -> InlineKeyboardMarkup:
    buttons = []
    for addr, lat, lon in locations:
        buttons.append(InlineKeyboardButton(text=addr, callback_data=f"location:{lat}:{lon}"))

    return get_paginated_keyboard(buttons, page, back_callback_data, cb_prefix, items_per_page)


# какой-то адрес
@router.callback_query(F.data.startswith('address:'))
async def process_callback_address(call: CallbackQuery):
    _, address_index = call.data.split(':')
    address_index = int(address_index)

    await call.answer()