<h1 align="center">🔥 Momently Bot 🔥</h1>
<h3 align="center">Telegram Bot</h3>

---
## Идея бота 
(Бот создан в 2023 году на aiogram3 и python 3.8)

Создать бот для курьерской службы компании, отслеживать по статусы посылок по Api Bing Maps. Принимать заказы, 

## Описание Бота Momently

### Возможности бота:

🌵 Регистрация компаний/клиентов/курьеров

🌵 Создание/принятие заказов

🌵 Админ-панель для админа и компаний

🌵 История заказов

🌵 Отправка геопозиции, определение адреса и расстояния и стоимости по координатам

🌵 Создавать, изменять, удалять локации (для компаний)

🌵 Создавать, изменять, удалять компании (для админа)

🌵 Активация/деактивация курьеров, рассылка, изменения статуса курьера (для компаний)

🌵 Активация/деактивация посылок, рассылка, изменения статуса работы (для админа)




---

## Инструкция по развертыванию
1. Перейти в папку с ботом: `cd name_dir`
1. `python3 -m venv venv_name` - создание виртуального окружения.
2. `source venv_name/bin/activate` - активация виртуального окружения.
3. `pip install -r requirements.txt` - подключить все библиотеки проекта.

---

## Инструкция по запуску

1. Создайте бота в Telegram через BotFather и получите токен для использования API.
2. `touch .env` - создайть файл .env  подробнее написано в `.env.template`
3. `echo "BOT_TOKEN=your_bot_token" >> .env` - добавить Токен бота
4. `echo "BING_MAPS_KEY=your_api Bing Maps" >> .env` - добавить api key
5. `echo "ADMIN_ID=your_admin_id" >> .env` - добавить Телеграм id админа
6. `sudo apt update`
7. `sudo apt install nodejs npm`
8. `sudo npm install pm2@latest -g`
9. `pm2 start python3 --name "bot" -- main.py`

### может содержать баги
#### скрины появятся чуть-позже
