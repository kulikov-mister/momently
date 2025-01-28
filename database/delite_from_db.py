from database.database import SentMessage, Location


def delete_sent_messages(order_id: int):
    SentMessage.delete().where(SentMessage.order_id == order_id).execute()


def delete_location_from_db(location_id: int):
    location = Location.get(Location.id == location_id)
    location.delete_instance()
