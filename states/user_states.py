from aiogram.filters.state import StatesGroup, State


class UserRegistrationState(StatesGroup):
    name = State()
    phone = State()


class StartState(StatesGroup):
    waiting_for_role = State()
