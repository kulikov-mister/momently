from geopy.distance import geodesic
from peewee import *

from config_data.config import database, cost_per_km, ADMIN_ID
from states.order_states import OrderStatus


class BaseModel(Model):
    class Meta:
        database = database


class Location(BaseModel):
    name = CharField()
    latitude = FloatField()
    longitude = FloatField()


class User(BaseModel):
    user_id = IntegerField(unique=True)
    name = CharField()
    phone = CharField()


class Company(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = IntegerField(unique=True)
    type = CharField()
    country = CharField()
    city = CharField()
    name = CharField()
    description = TextField()
    contact_info = CharField()
    admin_phone = CharField()
    bing_key = CharField()


class Courier(BaseModel):
    user_id = IntegerField(unique=True)
    company_id = ForeignKeyField(Company, backref='couriers', null=True)
    name = CharField()
    phone = CharField()
    rating = FloatField(default=0)
    is_active = BooleanField(default=True)
    admin_deactivated = BooleanField(default=False)
    location = ForeignKeyField(Location, backref='couriers', null=True)
    is_pro = BooleanField(default=False)


class Order(BaseModel):
    user_id = CharField()
    courier_id = IntegerField(null=True)
    location_id = ForeignKeyField(Location, backref='orders', null=True)
    first_latitude = FloatField()
    first_longitude = FloatField()
    second_latitude = FloatField(null=True)
    second_longitude = FloatField(null=True)
    status = CharField(default=OrderStatus.GENERATED)
    distance = FloatField(null=True)
    cost = FloatField(null=True)
    payment_method = CharField(null=True)
    comment = TextField(null=True)
    rating = FloatField(null=True)


class SentMessage(BaseModel):
    order = ForeignKeyField(Order, backref='sent_messages')
    user_id = IntegerField()
    message_id = IntegerField()


class SentItem(BaseModel):
    order = ForeignKeyField(Order, backref='sent_items')
    text_message_id = IntegerField(null=True)
    start_location_message_id = IntegerField(null=True)
    end_location_message_id = IntegerField(null=True)


def create_order(user_id, first_latitude, first_longitude):
    order = Order.create(user_id=user_id, first_latitude=first_latitude, first_longitude=first_longitude)
    return order


def update_order_second_location(order, second_latitude, second_longitude):
    order.second_latitude = second_latitude
    order.second_longitude = second_longitude

    first_location = (order.first_latitude, order.first_longitude)
    second_location = (order.second_latitude, order.second_longitude)
    distance = geodesic(first_location, second_location).kilometers
    cost = distance * cost_per_km

    order.distance = distance
    order.cost = cost
    order.save()


User.create_table()
Company.create_table()
Courier.create_table()
Order.create_table()
SentMessage.create_table()
Location.create_table()
SentItem.create_table()



