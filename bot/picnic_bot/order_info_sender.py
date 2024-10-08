import os

import psycopg2
import logging
from telegram import Bot
from bot.picnic_bot.abstract_functions import create_connection
from bot.picnic_bot.constants import ORDER_STATUS

from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


async def send_message_to_admin_and_service(user_id, session_num):
    """Отправляет информацию о заказе Администратору и Сервисной службе"""

    # Получаем токен из переменных окружения
    bot_token = os.getenv('TELEGRAM_TOKEN_ADMIN')
    if not bot_token:
        raise ValueError("Bot token is not set in the environment variables")

    admin_and_service_list = list()

    # Создаем подключение к базе данных PostgreSQL
    conn = create_connection()
    if conn is None:  # Проверяем, удалось ли создать соединение
        logging.error("Не удалось установить соединение с базой данных.")
        return  # Выходим из функции, если соединение не было создано

    cursor = conn.cursor()

    try:
        logging.info(f"Executing SELECT for user_id: {user_id}, session_number: {session_num}")
        cursor.execute("SELECT user_id, status FROM users WHERE status in (2,1)")
        admin_and_service_list = cursor.fetchall()

        logging.info(f"Executing SELECT for user_id: {user_id}, session_number: {session_num}")
        cursor.execute(
            """
            SELECT order_id, user_id, session_number, user_name, selected_date, start_time, end_time, duration,
            people_count, selected_style, preferences, city, calculated_cost 
            FROM orders 
            WHERE user_id = %s AND status = 3 AND session_number = %s
            """,
            (user_id, session_num)
        )
        order_info = cursor.fetchone()

        if order_info is None:
            logging.error(f"No recent orders with status 3 found for user_id {user_id}.")
            return
        else:
            logging.info(f"Order found: {order_info}")

        # Формируем сообщение для отправки админботу
        admin_message = (
            f"Привет твой id соответствует\n"
            f"номеру Сервисной службы AdminPicnicsAlicanteBot\n"
            f"https://t.me/AssistPicnicsBot\n"
            f"Сейчас пришло сообщение от PicnicsAlicanteBot:\n"
            f"____________________\n"
            f"ПРОФОРМА № {order_info[1]}_{order_info[2]}_3\n"
            f"Дата: {order_info[4]}\n"
            f"____________________\n"
            f"\nЕсли ты не видишь кнопок меню-жми /start"
        )

        service_message = (
            f"!!!!!!!!!!!!!!!!!Привет твой id соответствует\n"
            f"номеру Сервисной службы AdminPicnicsAlicanteBot\n"
            f"https://t.me/AssistPicnicsBot\n"
            f"Сейчас пришло сообщение от PicnicsAlicanteBot:\n"
            f"____________________\n"
            f"ПРОФОРМА № {order_info[1]}_{order_info[2]}_3\n"
            f"Дата: {order_info[4]}\n"
            f"____________________\n"
            f"\nЕсли ты не видишь кнопок меню-жми /start"
        )

        # Отправляем сообщение админботу
        bot = Bot(token=bot_token)
        for admin_id in admin_and_service_list:
            massage_text = admin_message
            if admin_id[1] == 2:
                massage_text = service_message
            await bot.send_message(chat_id=admin_id[0], text=massage_text)
            logging.info(f"Message sent to admin bot {admin_id[0]}.")

        # Обновляем статус ордера
        logging.info(f"Updating order status for user_id: {user_id}, session_number: {session_num}")
        cursor.execute(
            "UPDATE orders SET status = %s WHERE user_id = %s AND session_number = %s",
            (ORDER_STATUS["4-Админ и Сервисная служба получили сообщение о новой ПРОФОРМЕ"], user_id, session_num)
        )
        conn.commit()

        logging.info(f"Order status updated for user_id: {user_id}, session_number: {session_num}")

        # Обновляем количество зарезервированных ордеров - number_of_events
        logging.info(f"Counting orders for user_id: {user_id} with status > 2")
        cursor.execute(
            "SELECT COUNT(order_id) FROM orders WHERE user_id = %s AND status > 2",
            (user_id,)
        )
        events_num = cursor.fetchone()[0]
        logging.info(f"Number of events for user_id {user_id}: {events_num}")

        cursor.execute("UPDATE users SET number_of_events = %s WHERE user_id = %s", (events_num, user_id))
        conn.commit()

        logging.info(f"User {user_id} number_of_events updated to {events_num}.")

    except Exception as e:
        logging.error(f"Failed to send order info to admin bot: {e}")
        print(f"Ошибка при отправке сообщения: {e}")

    finally:
        cursor.close()
        conn.close()
        logging.info(f"Database connection closed for user_id: {user_id}")

