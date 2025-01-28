from aiogram import Bot, Dispatcher
from config_data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML",
          disable_web_page_preview=True)
dp = Dispatcher()
