import logging
import os

import psycopg2  # Заменяем sqlite3 на psycopg2 для работы с PostgreSQL
from dotenv import load_dotenv
from psycopg2 import OperationalError
from telegram import Update, Bot

from bot.admin_bot.constants import ORDER_STATUS
from bot.admin_bot.helpers.database_helpers import get_full_proforma
from bot.admin_bot.translations import language_selection_keyboard, translations

ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN_ADMIN')  # Получаем токен из .env файла


# Загружаем переменные окружения из .env файла
load_dotenv()

def get_db_connection():
    try:
        # Подключаемся к базе данных, используя переменные окружения
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'mydatabase'),
            user=os.getenv('DB_USER', 'myuser'),
            password=os.getenv('DB_PASSWORD', 'mypassword')
        )
    except OperationalError as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


async def user_welcome_message(update: Update, first_name):
    return await update.message.reply_text(
            f"Welcome {first_name}! Choose your language / Выберите язык",
            reply_markup=language_selection_keyboard()
        )


async def send_proforma_to_user(user_id, session_number, user_data):
    """Отправляет информацию о заказе пользователю."""
    conn = None  # Инициализация переменной
    try:
        # Получаем полную проформу
        order_info = get_full_proforma(user_id, session_number)

        # Получаем язык пользователя из user_data
        language = user_data.get_language() or 'en'
        trans = translations.get(language, translations['en'])  # Используем 'en' по умолчанию

        # Формируем сообщение для отправки пользователю
        user_message = (
            f"{trans['order_confirmed']}\n"
            f"{trans['proforma_number']} {order_info[0]}_{order_info[1]}_{order_info[10]}\n"
            f"{trans['event_date']} {order_info[2]}\n"
            f"{trans['time']} {order_info[3]} - {order_info[4]}\n"
            f"{trans['people_count']} {order_info[5]}\n"
            f"{trans['event_style']} {order_info[6]}\n"
            f"{trans['city']} {order_info[7]}\n"
            f"{trans['amount_to_pay']} {float(order_info[8]) - 20} евро\n"
            f"\n{trans['delivery_info']}"
        )

        # Отправляем сообщение пользователю
        bot = Bot(token=BOT_TOKEN)
        message = await bot.send_message(chat_id=user_id, text=user_message)

        logging.info(f"Message sent to user {user_id}.")

        # Обновляем статус ордера
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = %s WHERE user_id = %s AND session_number = %s",
            (ORDER_STATUS["5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ"], user_id, session_number)
        )
        conn.commit()

        return message

    except Exception as e:
        logging.error(f"Failed to send order info to user: {e}")

    finally:
        if conn:  # Проверяем, инициализирована ли переменная
            conn.close()
