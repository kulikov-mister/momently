from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline_builder import inline_builder
from database.database import Location, Courier
from database.delite_from_db import delete_location_from_db
from loader import dp

router = Router()
dp.include_router(router)

# кнопка удалить локацию
@router.callback_query(F.data == 'delete_location')
async def delete_location_request(call: CallbackQuery, state: FSMContext):
    await state.update_data(admin_id=call.from_user.id)

    # Получите все доступные локации из базы данных
    locations = Location.select()

    # Создайте клавиатуру с кнопками для каждой локации
    buttons_data = [
        {"text": location.name, "callback_data": f"delete_location_confirm_{location.id}"}
        for location in locations
    ]

    await call.message.edit_text("💫 Выберите локацию, которую хотите удалить.",
                                 reply_markup=inline_builder(buttons_data))


# подтверждение удаления
@router.callback_query(F.data.startswith('delete_location_confirm_'))
async def delete_location_confirm_request(call: CallbackQuery, state: FSMContext):
    location_id = call.data.split("_")[3]
    if location_id == "1":
        # Отмените удаление, если это основная локация
        await call.message.edit_text("❗️ Основную локацию нельзя удалить.")
    else:
        location = Location.get(Location.id == location_id)
        await state.update_data(location_to_delete_id=location_id)

        # Переназначьте курьеров на основную локацию
        main_location = Location.get(Location.id == 1)
        Courier.update(location=main_location).where(Courier.location == location).execute()

        buttons_data = [
                {"text": "❌ Удалить", "callback_data": "confirm_delete_yes"},
                {"text": "⭕️ Оставить", "callback_data": "confirm_delete_no"},
                {"text": "🏠 Главное меню", "callback_data": "mainstart_company"}
            ]

        await call.message.edit_text(
            f"🤨 Вы уверены, что хотите удалить локацию <b>{location.name}</b>? Все курьеры на этой локации будут перемещены на основную локацию.",
            reply_markup=inline_builder(buttons_data, 2))


# кнопка да на подтверждении удаления локации
@router.callback_query(F.data == 'confirm_delete_yes')
async def confirm_delete_location(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    location_id = state_data["location_to_delete_id"]
    location = Location.get(Location.id == location_id)

    delete_location_from_db(location_id)
    
    buttons_data = [{"text": "🏠 Главное меню", "callback_data": "mainstart_company"}]
    await call.message.edit_text(f"✅ Локация <b>{location.name}</b> успешно удалена.",
                                 reply_markup=inline_builder(buttons_data))

# кнопка нет на подтверждении удаления локации
@router.callback_query(F.data == 'confirm_delete_no')
async def cancel_delete_location(call: CallbackQuery, state: FSMContext):
    buttons_data = [{"text": "🏠 Главное меню", "callback_data": "mainstart_company"}]
    await call.message.edit_text("👌 Окей, локация не будет удалена.",
                                 reply_markup=inline_builder(buttons_data))
