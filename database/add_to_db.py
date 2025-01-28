from database.database import User, Order, SentMessage, Courier, Location, SentItem


def add_user(user_id, name, phone):
    User.create(user_id=user_id, name=name, phone=phone)


def add_courier(user_id, name, phone, location):
    Courier.create(user_id=user_id, name=name, phone=phone, location=location)


def add_location_to_db(location_data):
    Location.create(name=location_data["name_location"],
                    latitude=location_data["latitude"],
                    longitude=location_data["longitude"])


def create_order_in_db(order_data):
    Order.create(
        user_id=order_data["user_id"],
        first_latitude=order_data["first_latitude"],
        first_longitude=order_data["first_longitude"],
        second_latitude=order_data["second_latitude"],
        second_longitude=order_data["second_longitude"],
        payment_method=order_data["payment_method"],
        comment=order_data["comment"],
        location_id=order_data["location_id"],
        distance=order_data["distance"],
        cost=order_data["cost"],
    )


def save_sent_messages(order_id, sent_messages):
    order = Order.get(Order.id == order_id)
    for user_id, message_id in sent_messages:
        SentMessage.create(order=order, user_id=user_id, message_id=message_id)


async def create_sent_item(order):
    sent_item = SentItem.get_or_none(order=order)
    if sent_item is None:
        sent_item = SentItem.create(order=order)
    return sent_item
