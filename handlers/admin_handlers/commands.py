# handlers/admin_handlers/commands.py
import logging
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from Filter.Filter import IsNotCommand, IncludeStateData, LinkNumberFilter
from database.add_to_db import add_courier
from database.database import Company
from handlers.courier_handlers import main_menu_courier
from keyboards.inline.time_days_work_keybard import days_work_keyboard, time_work_keyboard
from keyboards.inline.location_courier import create_location_keyboard
from keyboards.inline.orders_inline.user_order_inline.comment import comment_keyboard
from keyboards.reply.sent_contact import create_contact_keyboard
from config_data.config import COUNTRIES, TYPES_COMPANIES
from loader import dp, bot
from states.company_states import CompanyRegistrationState
from lang.get_message import get_message, get_keyboard, extract_language
from utils.validate_data import validate_bing_key

router = Router()
dp.include_router(router)


