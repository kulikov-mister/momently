from aiogram.filters.state import StatesGroup, State


class CourierRegistrationState(StatesGroup):
    name = State()
    phone = State()
    location = State()


class StartState(StatesGroup):
    waiting_for_role = State()


class CourierLocationState(StatesGroup):
    waiting_for_location = State()
