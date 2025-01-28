from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states.order_states import OrderStatus

# создание инлайн кнопок
def inline_builder(buttons: List[dict], row_quantity: int = 1) -> InlineKeyboardMarkup:
    # Создаем список списков кнопок
    inline_keyboard = []
    
    if row_quantity == 1:
        for button in buttons:
            inline_btn = InlineKeyboardButton(text=button["text"], callback_data=button["callback_data"])
            inline_keyboard.append([inline_btn])
    else:
        # Добавление кнопок по row_quantity в ряд
        row = []
        for button in buttons:
            row.append(InlineKeyboardButton(text=button["text"], callback_data=button["callback_data"]))
            if len(row) == row_quantity:
                inline_keyboard.append(row)
                row = []
        if row:
            inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# добавление кнопок пагинации к основному список кнопок
def get_paginated_keyboard(buttons: list[InlineKeyboardButton], page: int, back_callback_data: str, cb_prefix: str, items_per_page: int = 7) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    for button in buttons[start_index:end_index]:
        keyboard_builder.row(button)

    navigation_buttons = []
    # Кнопка "prev page", если текущая не первая страница
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text=f" {page-1} ◀️", callback_data=f"page:{cb_prefix}:{page-1}"))
    # Кнопка "Назад" добавляется обязательно
    navigation_buttons.append(InlineKeyboardButton(text="🏡 Назад", callback_data=back_callback_data))
    # Кнопка "next page", если не последняя страница
    if end_index < len(buttons):
        navigation_buttons.append(InlineKeyboardButton(text=f"▶️ {page+1} ", callback_data=f"page:{cb_prefix}:{page+1}"))

    keyboard_builder.row(*navigation_buttons)
    return keyboard_builder.as_markup()


# кнопки ордеров
def get_inline_orders(orders, ind:int = 1) -> List[InlineKeyboardButton]:
    
    buttons = []
    if ind == 1:
        for order in orders: # кнопки ордеров
            text = f"Заказ №{order.id} - {'Выполнен' if order.status == OrderStatus.COMPLETED else 'Не выполнен'}"
            callback_data = f"order_info_{order.id}"
            buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data)) 
            
    elif ind == 2:
        for order in orders: # кнопки ордеров
            text = f"📄 Заказ №{order.id} - {'Выполнен' if order.status == OrderStatus.COMPLETED else 'Не выполнен'}"
            callback_data = f"courier_order_info_{order.id}"
            buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data)) 

    return buttons

