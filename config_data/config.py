# config_data/config.py
import os
from dotenv import load_dotenv, find_dotenv
from peewee import SqliteDatabase
from geopy import Photon
from geopy.adapters import AioHTTPAdapter

database = SqliteDatabase('database/Couriers.db')
geolocator = Photon(user_agent="geoapiExercises", adapter_factory=AioHTTPAdapter, timeout=5)
cost_per_km = 50
CURRENCY = "₸"

# PROXY_URL = "http://proxy.server:3128"

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

COUNTRIES = ["Kazakhstan 🇰🇿"]
TYPES_COMPANIES = ["Курьерская служба", "Служба доставки товаров из Китая"]

# Инициализируем бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
ADMIN_IDS = [int(admin_id) for admin_id in ADMIN_ID.split(",")]
BING_MAPS_KEY = os.getenv('BING_MAPS_KEY')
