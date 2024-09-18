import sqlite3
import logging
from telegram import Update, Bot
from telegram.ext import ContextTypes
from bot.admin_bot.helpers.database_helpers import get_latest_session_number, get_full_proforma
from shared.config import BOT_TOKEN
from shared.constants import UserData, ORDER_STATUS
from shared.translations import language_selection_keyboard, translations

from shared.config import DATABASE_PATH

ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}

import logging

# Логирование
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO,
#     filename=r'C:\Users\USER\PycharmProjects\EventMaster\bot\admin_bot\helpers\logs'  # Укажите путь к файлу лога
# )
# logger = logging.getLogger(__name__)

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
        print("???????????????????????????????????????????????")

        # Отправляем сообщение пользователю
        bot = Bot(token=BOT_TOKEN)
        message = await bot.send_message(chat_id=user_id, text=user_message)

        logging.info(f"Message sent to user {user_id}.")

        # Обновляем статус ордера
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = ? WHERE user_id = ? AND session_number = ?",
            (ORDER_STATUS["5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ"], user_id, session_number)
        )
        conn.commit()

        return message

    except Exception as e:
        logging.error(f"Failed to send order info to user: {e}")

    if conn:  # Проверяем, инициализирована ли переменная

        conn.close()






