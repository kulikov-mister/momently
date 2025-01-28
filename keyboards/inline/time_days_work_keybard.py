# keyboards/inline/time_days_work_keybard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lang.get_message import get_keyboard


# кнопки для выбора рабочих дней
def days_work_keyboard(lang, selected_days=None):
    if selected_days is None:
        selected_days = set()
    days = get_keyboard(lang, "company", "days_of_week")
    confirm_button_text = get_keyboard(lang, "company", "confirm_button")

    builder = InlineKeyboardBuilder()
    for day in days:
        is_selected = day in selected_days
        # Изменяем callback_data в зависимости от состояния выбора
        callback_data = f"day_{day}_{'-' if is_selected else '+'}"
        button_text = f"{'✔️ ' if is_selected else ''}{day}"
        builder.row(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    builder.row(InlineKeyboardButton(text=confirm_button_text, callback_data="confirm_days"))

    return builder.as_markup()



# кнопкки для выбора рабочего времени
def time_work_keyboard(lang, selected_start_time=None, selected_end_time=None):
    builder = InlineKeyboardBuilder()
    for hour in range(24):
        start_button_text = f"{hour}:00"
        end_button_text = f"{hour}:00"
        
        # Отмечаем выбранное время начала и окончания
        is_start_selected = selected_start_time == start_button_text
        is_end_selected = selected_end_time == end_button_text

        start_callback_data = f"start_{hour}_{'-' if is_start_selected else '+'}"
        end_callback_data = f"end_{hour}_{'-' if is_end_selected else '+'}"

        builder.row(
            InlineKeyboardButton(text=f"{'✔️ ' if is_start_selected else ''}{start_button_text}", callback_data=start_callback_data),
            InlineKeyboardButton(text=f"{'✔️ ' if is_end_selected else ''}{end_button_text}", callback_data=end_callback_data)
        )

    confirm_button_text = get_keyboard(lang, "company", "confirm_button")
    builder.row(InlineKeyboardButton(text=confirm_button_text, callback_data="confirm_time"))

    return builder.as_markup()