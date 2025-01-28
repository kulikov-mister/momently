from aiogram.filters.state import StatesGroup, State


class OrderStatus(StatesGroup):
    GENERATED = 'GENERATED'
    ACCEPTED = 'ACCEPTED'
    PRICE_CANCELED = 'PRICE_CANCELED'
    EXPECTATION = 'EXPECTATION'
    TRIP = 'TRIP'
    COMPLETED = 'COMPLETED'
    CANCELED = 'CANCELED'


class CourierOrderState(StatesGroup):
    FIRST_LOCATION = State()
    SECOND_LOCATION = State()
    PAYMENT_METHOD = State()
    COMMENT = State()
    LOCATION = State()


class ProposePriceState(StatesGroup):
    price = State()
    coment = State()
