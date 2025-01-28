import logging, asyncio
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from Filter.Filter import IsNotCommand, IncludeStateData, LinkNumberFilter
from database.add_to_db import add_courier
from database.database import Company
from handlers.courier_handlers import main_menu_courier
from keyboards.inline.time_days_work_keybard import days_work_keyboard, time_work_keyboard
from keyboards.inline.location_courier import create_location_keyboard
from keyboards.inline.orders_inline.user_order_inline.comment import comment_keyboard
from keyboards.reply.sent_contact import create_contact_keyboard
from config_data.config import COUNTRIES, TYPES_COMPANIES
from loader import dp, bot
from states.company_states import CompanyRegistrationState
from lang.get_message import get_message, get_keyboard, extract_language
from utils.validate_data import validate_bing_key

router = Router()
dp.include_router(router)



# старт регистрации компании
@router.callback_query(F.data == 'company')
async def registration_company_start_handler(call: CallbackQuery, state: FSMContext):
    lang= extract_language(Message)
    await call.answer()
    msg = get_message(lang, "company", "registration_type_prompt")
    info = get_message(lang, "company", "registration_micro_guide")
    await call.message.edit_text(info, reply_markup=None)
    await asyncio.sleep(10)
    await call.message.answer(msg, reply_markup=comment_keyboard(TYPES_COMPANIES))
    await state.set_state(CompanyRegistrationState.type)



# старт регистрации - запрос выбора типа компании
@router.message(IsNotCommand(), CompanyRegistrationState.type)
async def registration_type_handler(message: Message, state: FSMContext):
    lang = extract_language(message)

    user_input = message.text  # Переименовываем переменную для четкости
    if user_input in TYPES_COMPANIES:
        await state.update_data(type=user_input)
        msg = get_message(lang, "company", "registration_country_prompt")
        await message.answer(msg, reply_markup=comment_keyboard(COUNTRIES))
        await state.set_state(CompanyRegistrationState.country)
    else:
        msg = get_message(lang, "company", "registration_country_prompt_error")
        await message.answer(msg)  # Также используем исходный объект message



# приём страны и запрос города
@router.message(IsNotCommand(), CompanyRegistrationState.country)
async def registration_country_handler(message: Message, state: FSMContext):
    lang= extract_language(Message)
    country = message.text
    if country in COUNTRIES:
        await state.update_data(country=country)
        msg = get_message(lang, "company", "registration_city_prompt")
        await state.set_state(CompanyRegistrationState.city)
    else:
        msg = get_message(lang, "company", "registration_city_prompt")
    await message.answer(msg)



# получение списка городов
@router.message(IsNotCommand(), CompanyRegistrationState.city)
async def registration_city_handler(message: Message, state: FSMContext):
    lang= extract_language(Message)

    city = message.text
    # Тут логика для проверки введенного города
    await state.update_data(city=city)
    msg = get_message(lang, "company", "registration_name_prompt")
    await message.answer(msg)
    await state.set_state(CompanyRegistrationState.name)



# Получение названия компании
@router.message(IsNotCommand(), CompanyRegistrationState.name)
async def registration_name_handler(message: Message, state: FSMContext):
    lang= extract_language(Message)

    name = message.text
    # Тут логика для проверки введенного названия
    await state.update_data(name=name)
    msg = get_message(lang, "company", "registration_description_prompt")
    await message.answer(msg)
    await state.set_state(CompanyRegistrationState.description)



# Получение описания компании
@router.message(IsNotCommand(), CompanyRegistrationState.description)
async def registration_description_handler(message: Message, state: FSMContext):
    lang= extract_language(Message)

    description = message.text
    await state.update_data(description=description)
    msg = get_message(lang, "company", "registration_days_work_prompt")
    days = get_keyboard(lang, "company", "days_of_week")
    keyboard = days_work_keyboard(days)
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state(CompanyRegistrationState.days_work)



# Фильтр на выбор рабочего времени
@router.callback_query(F.data=="confirm_days", CompanyRegistrationState.days_work)
async def registration_days_work_handler(call: CallbackQuery, state: FSMContext):
    lang= extract_language(call)
    order_of_days = get_keyboard(lang, "company", "days_of_week")

    # Построение списка выбранных дней
    selected_days = set()
    for row in call.message.reply_markup.inline_keyboard:
        for button in row:
            if "day_" in button.callback_data and "_-" in button.callback_data:
                day = button.callback_data.split("_")[1]
                selected_days.add(day)

    # Сортировка выбранных дней в соответствии с порядком дней недели
    sorted_selected_days = [day for day in order_of_days if day in selected_days]

    # Выводим лог выбранных дней для отладки
    print("Выбранные дни:", sorted_selected_days)

    if len(sorted_selected_days) >= 3:
        await state.update_data(work_days=sorted_selected_days)

        # Обработка подтверждения выбора
        await call.answer("Выбор дней подтвержден")
        lang = extract_language(call.from_user)
        keyboard = time_work_keyboard(lang)
        msg = get_message(lang, "company", "registration_time_work_prompt")
        await call.message.edit_text(msg, reply_markup=keyboard)
        await state.set_state(CompanyRegistrationState.time_work)

    else:
        await call.answer("Выберите минимум 3 дня", show_alert=True)



# Фильтр на выбор времени работы
@router.callback_query(F.data == "confirm_time", CompanyRegistrationState.time_work)
async def registration_time_work_handler(call: CallbackQuery, state: FSMContext):
    lang = extract_language(call.from_user)

    # Извлекаем выбранное время начала и окончания из клавиатуры
    selected_start_time = None
    selected_end_time = None
    for row in call.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith("start_") and "_-" in button.callback_data:
                selected_start_time = button.text.strip("✔️ ").strip()
            elif button.callback_data.startswith("end_") and "_-" in button.callback_data:
                selected_end_time = button.text.strip("✔️ ").strip()

    # Проверяем, что выбраны и время начала, и время окончания
    if not selected_start_time or not selected_end_time:
        await call.answer("Пожалуйста, выберите время начала и окончания рабочего дня.", show_alert=True)
        return

    # Формируем строку с временем работы
    time_work = f"{selected_start_time}-{selected_end_time}" if selected_start_time != selected_end_time else get_message(lang, "company", "24h")

    await state.update_data(time_work=time_work)
    msg = get_message(lang, "company", "registration_contact_info_prompt")
    await call.message.edit_text(msg, reply_markup=None)
    # await call.message.answer(msg)
    # Переходим к следующему состоянию (при необходимости обновляем state здесь)
    await state.set_state(CompanyRegistrationState.contact_info)



# Получение информации о компании
@router.message(IsNotCommand(), CompanyRegistrationState.contact_info)
async def registration_contact_info_handler(message: Message, state: FSMContext):
    lang= extract_language(Message)

    contact_info = message.text
    await state.update_data(contact_info=contact_info)
    
    msg = get_message(lang, "company", "registration_admin_phone_prompt")
    kb_text = get_keyboard(lang, "company", "contact_keyboard")
    contact_keyboard = create_contact_keyboard(kb_text)
    await message.answer(msg, reply_markup=contact_keyboard)
    await state.set_state(CompanyRegistrationState.admin_phone)



# Получение телефона администратора
@router.message(F.contact, CompanyRegistrationState.admin_phone)
async def registration_admin_phone_handler(message: Message, state: FSMContext):
    lang= extract_language(Message)

    admin_phone = message.contact.phone_number
    await state.update_data(admin_phone=admin_phone)
    msg = get_message(lang, "company", "registration_bing_key_prompt")
    await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    await state.set_state(CompanyRegistrationState.bing_key)



# завершение регистрации
@router.message(IsNotCommand(), CompanyRegistrationState.bing_key)
async def registration_bing_key_handler(message: Message, state: FSMContext):
    lang= extract_language(Message)

    bing_key = message.text
    await state.update_data(bing_key=bing_key)
    
    is_valid = await validate_bing_key(bing_key)
    if not is_valid:
        msg = get_message(lang, "company", "bing_key_error")
        await message.answer(msg, show_alert=True)
        return
    await state.update_data(bing_key=bing_key)
    get_data = await state.get_data()

    msg = get_message(lang, "company", "registration_complete_message")
    await message.answer(msg)
    # await state.clear()  # Регистрация завершена, можно очистить состояние
    logging.info(get_data)


# {'type': 'Курьерская служба', 'country': 'Kazakhstan 🇰🇿', 'city': 'Astana', 
#  'name': 'First logistics', 'description': 'Description', 'work_days': ['Среда', 'Четверг', 'Воскресенье'], 
#  'time_work': '22:00-23:00', 'contact_info': 'Telephone', 'admin_phone': '77051546166', 
#  'bing_key': 'AheDIEkrwhHidr9uycF4sOGSrDhaUdiLI77jirooKsopPzfg8aFbrGbKmaN5SzoF'}





# _____________________________________________________________________________
# дополнительные хендлеры
# 

# нажатие на день
@router.callback_query(F.data.startswith("day_"))
async def day_selected_handler(call: CallbackQuery):
    _, day, action = call.data.split("_")

    # Получение текущего состояния выбранных дней из клавиатуры
    selected_days = set()
    for row in call.message.reply_markup.inline_keyboard:
        for button in row:
            if "day_" in button.callback_data and "_-" in button.callback_data:
                selected_day = button.callback_data.split("_")[1]
                selected_days.add(selected_day)

    # Добавление или удаление дня в зависимости от действия
    if action == "+":
        selected_days.add(day)
    else:
        selected_days.discard(day)

    # Обновление клавиатуры с новым состоянием выбранных дней
    new_keyboard = days_work_keyboard(call.from_user.language_code, selected_days)
    await call.message.edit_reply_markup(reply_markup=new_keyboard)

    # Отправляем подтверждение выбора
    await call.answer(f"{'➕' if action == '+' else '➖'}: {day}")



# Нажатие на время начала рабочего дня
@router.callback_query(F.data.startswith("start_"))
async def start_time_selected(call: CallbackQuery):
    selected_start_time = call.data.split("_")[1] + ":00"

    # Извлекаем текущее выбранное время окончания из клавиатуры
    selected_end_time = None
    for row in call.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith("end_") and "_-" in button.callback_data:
                selected_end_time = button.text.strip("✔️ ").strip()

    # Обновляем клавиатуру, отмечая выбранные времена
    new_keyboard = time_work_keyboard(call.from_user.language_code, selected_start_time, selected_end_time)
    await call.message.edit_reply_markup(reply_markup=new_keyboard)

    await call.answer(f"Время начала: {selected_start_time}")

# Нажатие на время окончания рабочего дня
@router.callback_query(F.data.startswith("end_"))
async def end_time_selected(call: CallbackQuery):
    selected_end_time = call.data.split("_")[1] + ":00"

    # Извлекаем текущее выбранное время начала из клавиатуры
    selected_start_time = None
    for row in call.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith("start_") and "_-" in button.callback_data:
                selected_start_time = button.text.strip("✔️ ").strip()

    # Обновляем клавиатуру, отмечая выбранные времена
    new_keyboard = time_work_keyboard(call.from_user.language_code, selected_start_time, selected_end_time)
    await call.message.edit_reply_markup(reply_markup=new_keyboard)

    await call.answer(f"Время окончания: {selected_end_time}")





# ______________________________________________________________________________________
# пустой хендлер
@router.callback_query(F.data)
async def empty_callback_handler(call: CallbackQuery):
    await call.answer(call.data)