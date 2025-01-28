# filters/Filter.py
import re
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config_data.config import ADMIN_IDS
from lang.get_message import get_message


# фильтр на админа
class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, callback_query: CallbackQuery = None) -> bool:
        user_id = message.from_user.id if message else callback_query.from_user.id if callback_query else None
        return user_id in ADMIN_IDS

# фильтр на команды
class IsCommand(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result = message.text and message.text.startswith('/')
        return result

# фильтр на некоманды
class IsNotCommand(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result =  message.text and not message.text.startswith('/')
        return result
    
# фильтр проверки стейтов
class IsStates(BaseFilter):
    def __init__(self, states):
        self.states = states

    async def __call__(self, event, state: FSMContext):
        current_state = await state.get_state()
        return current_state in self.states
    

# фильтр на некоманды и стейты
class IsNotCommandInStates(BaseFilter):
    def __init__(self, states):
        self.states = states

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        # Проверка, что состояние не None и оно находится в списке состояний
        return message.text and not message.text.startswith('/') and (current_state is not None and current_state in self.states)


# фильтр на наличие данных в стейте
class IncludeStateData(BaseFilter):
    def __init__(self, keys):
        self.keys = keys

    async def __call__(self, event, state: FSMContext):
        state_data = await state.get_data()
        return all(key in state_data for key in self.keys)


# фильтр на наличие ссылки и номера в тексте 
class LinkNumberFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # Регулярное выражение для поиска URL, юзернеймов и номеров телефона
        regex = r"(\b(?:https?://)?\w[\w.-]+\.[a-zA-Z]{2,6}\b|@\w[\w_\.]+|\+?\d{1,4}([-. ()\[\]{}\"'_]\d{1,4}){0,4})"

        # Список цифр, записанных словами
        number_words = [
            "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", 
            "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", 
            "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать",
            "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", 
            "восемьдесят", "девяносто",
            "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", 
            "семьсот", "восемьсот", "девятьсот", "тысяча", "тысячи"
        ]
        # Проверяем, содержит ли сообщение URL, юзернеймы, номера телефона или цифры словами
        lang = message.from_user.language_code
        if re.search(regex, message.text):
            msg = get_message(lang, "default", "do_not_include_link_msg")
            return message.answer(msg)

        if any(word in message.text for word in number_words):
            msg = get_message(lang, "default", "do_not_include_number_word_msg")
            return message.answer(msg)

        return True