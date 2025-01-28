from config_data.config import geolocator, ADMIN_ID
from database.database import User, Order, Courier, SentItem
from states.order_states import OrderStatus


async def get_user(user_id):
    user = User.get_or_none(User.user_id == user_id)
    return user


async def get_courier(user_id):
    user = Courier.get_or_none(Courier.user_id == user_id)
    return user


def get_order_by_courier_id(courier_id):
    # Получаем заказ для такси, где статус заказа либо GENERATED, ACCEPTED, либо EXPECTATION
    return Order.get_or_none(
        (Order.courier_id == courier_id) &
        (Order.status.in_([OrderStatus.GENERATED, OrderStatus.ACCEPTED, OrderStatus.EXPECTATION]))
    )


def get_couriers_by_location(location_id):
    return Courier.select().where(Courier.location_id == location_id)


def get_all_couriers():
    couriers = Courier.select()
    return couriers


def get_all_couriers_with_child_seat():
    return Courier.select().where(Courier.child_seat == True)


def get_generated_orders():
    orders = Order.select().where(Order.status == 'GENERATED')
    return orders


def get_order_by_id(order_id):
    try:
        return Order.get(Order.id == order_id)
    except Order.DoesNotExist:
        return None


def get_order_by_user_id(user_id):
    return Order.get_or_none((Order.user_id == user_id) & (Order.status == OrderStatus.GENERATED))


def has_orders(user_id):
    # Проверяем наличие заказов для пользователя с заданным user_id
    # Теперь мы также проверяем, чтобы статус был GENERATED, ACCEPTED или EXPECTATION
    orders_count = Order.select().where(
        (Order.user_id == user_id) &
        (Order.status.in_([OrderStatus.GENERATED, OrderStatus.ACCEPTED, OrderStatus.EXPECTATION]))
    ).count()
    return orders_count > 0


def get_sent_messages(order_id):
    return [(msg.user_id, msg.message_id) for msg in Order.get(Order.id == order_id).sent_messages]


async def get_active_orders_by_user_id(user_id):
    # Получаем список заказов для пользователя с заданным user_id и с нужным статусом
    orders = Order.select().where(
        (Order.user_id == user_id) &
        (Order.status.in_([OrderStatus.GENERATED, OrderStatus.ACCEPTED, OrderStatus.EXPECTATION, OrderStatus.TRIP]))
    )
    return orders


def get_all_unique_users():
    user_ids = set()
    for user in User.select():
        user_ids.add(user.user_id)
    for taxi in Courier.select():
        user_ids.add(taxi.user_id)
    return user_ids


async def get_address_from_coordinates(lat, lon):
    location = await geolocator.reverse([lat, lon], exactly_one=True)
    return location.address


async def get_sent_item_by_order(order):
    try:
        sent_item = SentItem.select().where(SentItem.order == order).get()
    except SentItem.DoesNotExist:
        return None
    return sent_item



