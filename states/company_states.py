from aiogram.filters.state import StatesGroup, State


class CompanyRegistrationState(StatesGroup):
    type = State()
    country = State()
    city = State()
    name = State()
    description = State()
    days_work = State()
    time_work = State()
    contact_info = State()
    admin_phone = State()
    bing_key = State()