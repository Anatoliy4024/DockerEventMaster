import psycopg2
import logging
from telegram import Bot

from abstract_functions import create_connection

from constants import ORDER_STATUS

async def send_order_info_to_servis(user_id, session_num):
    """Отправляет информацию о заказе Сервисной службе"""

    bot_token = '7495955549:AAGG0PQNvFC-SN0PO4rx0WVi2HEeIM8mnVg'  # Токен админбота
    admin_list = list()

    # Создаем подключение к базе данных PostgreSQL
    conn = create_connection()
    cursor = conn.cursor()

    try:
        logging.info(f"Executing SELECT for user_id: {user_id}, session_number: {session_num}")
        cursor.execute("SELECT user_id FROM users WHERE status = 2")
        admin_list = cursor.fetchall()

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

        # Отправляем сообщение админботу
        bot = Bot(token=bot_token)
        for admin_id in admin_list:
            await bot.send_message(chat_id=admin_id[0], text=admin_message)
            logging.info(f"Message sent to admin bot {admin_id[0]}.")

        # Обновляем статус ордера
        logging.info(f"Updating order status for user_id: {user_id}, session_number: {session_num}")
        cursor.execute(
            "UPDATE orders SET status = %s WHERE user_id = %s AND session_number = %s",
            (ORDER_STATUS["4-Ирина и Сервисная служба получили сообщение о новой ПРОФОРМЕ"], user_id, session_num)
        )
        conn.commit()

        logging.info(f"Order status updated for user_id: {user_id}, session_number: {session_num}")

        # Обновляем количество зарезервированных ордеров - number_of_events
        logging.info(f"Counting orders for user_id: {user_id} with status 3 or 4")
        cursor.execute(
            "SELECT COUNT(order_id) FROM orders WHERE user_id = %s AND status IN (3,4)",
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


async def send_message_to_admin(user_id, session_num):
    """Отправляет информацию о заказе Админу"""

    bot_token = '7495955549:AAGG0PQNvFC-SN0PO4rx0WVi2HEeIM8mnVg'  # Токен админбота
    irina_chat_id = 884649958  # chat_id Ирины

    # Создаем подключение к базе данных PostgreSQL
    conn = create_connection()
    cursor = conn.cursor()

    try:
        logging.info(f"Executing SELECT for user_id: {user_id}, session_number: {session_num}")
        cursor.execute(
            """
            SELECT order_id, user_id, session_number, user_name, selected_date, start_time, end_time, duration,
            people_count, selected_style, preferences, city, calculated_cost 
            FROM orders 
            WHERE user_id = %s AND status IN (3,4) AND session_number = %s
            """,
            (user_id, session_num)
        )
        order_info = cursor.fetchone()

        if order_info is None:
            logging.error(f"No recent orders with status 3 found for user_id {user_id}.")
            return
        else:
            logging.info(f"Order found: {order_info}")

        # Формируем сообщение для отправки Ирине
        irina_message = (
            f"Добрый день!\n"
            f"Я - твой АдминБот\n"
            f"Есть новый заказ через\n"
            f"PicnicsAlicanteBot\n"
            f"____________________\n"
            f"ПРОФОРМА № {order_info[1]}_{order_info[2]}_3\n"
            f"Дата: {order_info[4]}\n"
            f"____________________\n"
            f"\nЕсли не видно кнопок меню - жми /start"
        )

        # Отправляем сообщение Ирине
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=irina_chat_id, text=irina_message)
        logging.info(f"Message sent to Irina {irina_chat_id}.")

    except Exception as e:
        logging.error(f"Failed to send order info to Irina: {e}")
        print(f"Ошибка при отправке сообщения Ирине: {e}")

    finally:
        cursor.close()
        conn.close()
        logging.info(f"Database connection closed for user_id: {user_id}")
