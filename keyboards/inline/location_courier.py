from typing import List
from keyboards.inline_builder import get_paginated_keyboard
from aiogram.types import InlineKeyboardButton

def create_location_keyboard(locations_data, page, back_callback_data, cb_prefix, items_per_page: int = 7)-> List[InlineKeyboardButton]:
    buttons = []

    for loc_name, lat, lon in locations_data:
        buttons.append(InlineKeyboardButton(text=loc_name, callback_data=f"location:{lat}:{lon}")) 


    return get_paginated_keyboard(buttons, page, back_callback_data, cb_prefix, items_per_page)
