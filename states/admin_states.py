from aiogram.filters.state import StatesGroup, State

class CompanyState(StatesGroup):
    BROADCAST = State()
    LOCATION = State()
    LOCATION_NAME = State()


class CompanyFindOrder(StatesGroup):
    waiting_for_order_number = State()
