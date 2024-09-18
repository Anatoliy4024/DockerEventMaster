# database_helpers.py

import sqlite3
import logging
from shared.constants import ORDER_STATUS
from shared.config import DATABASE_PATH
from shared.translations import translations

# def get_user_data(user_id):
#     conn = sqlite3.connect(DATABASE_PATH)
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
#     user_data = cursor.fetchone()
#     conn.close()
#     return user_data

def get_full_proforma(user_id, session_number):
    """
    Получает полную проформу для пользователя по user_id и session_number.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT user_id, session_number, selected_date, start_time, end_time, people_count, selected_style,
            city, calculated_cost, preferences, status, order_id
            FROM orders
            WHERE user_id = ? AND session_number = ?
            """,
            (user_id, session_number)
        )
        order_info = cursor.fetchone()

        if order_info:
            return order_info
        else:
            raise ValueError("Нет подходящей проформы для этого пользователя.")

    finally:
        conn.close()



# Функция для получения последнего session_number
def get_latest_session_number(user_id):
    """
    Получает максимальный session_number для пользователя с user_id.
    Если найден статус 4, обновляет его на 5 после просмотра проформы.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Сначала пытаемся найти session_number со статусом 4 (Ирина и Сервисная служба получили сообщение)
        cursor.execute("""
            SELECT session_number 
            FROM orders 
            WHERE user_id = ? 
            AND status = ? 
            ORDER BY session_number DESC 
            LIMIT 1
        """, (user_id, ORDER_STATUS["4-Ирина и Сервисная служба получили сообщение о новой ПРОФОРМЕ"]))

        result = cursor.fetchone()

        if result:
            session_number = result[0]

            return session_number  # Возвращает session_number после обновления статуса

        else:
            # Если ничего не найдено, ищем session_number со статусом 5 (Заказчик просмотрел ПРОФОРМУ)
            cursor.execute("""
                SELECT session_number 
                FROM orders 
                WHERE user_id = ? 
                AND status = ? 
                ORDER BY session_number DESC 
                LIMIT 1
            """, (user_id, ORDER_STATUS["5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ"]))

            result = cursor.fetchone()

            if result:
                return result[0]  # Возвращает session_number для статуса 5
            else:
                raise ValueError("Нет подходящих записей для этого пользователя.")

    finally:
        conn.close()


##############  "Это перенос функции в user_scenario.py


# async def send_proforma_to_user(user_id, session_number, user_data):
#     """Отправляет информацию о заказе пользователю."""
#     conn = None  # Инициализация переменной
#     try:
#         # Получаем полную проформу
#         order_info = get_full_proforma(user_id, session_number)
#
#         # Получаем язык пользователя из user_data
#         language = user_data.get_language() or 'en'
#         trans = translations.get(language, translations['en'])  # Используем 'en' по умолчанию
#
#         # Формируем сообщение для отправки пользователю
#         user_message = (
#             f"{trans['order_confirmed']}\n"
#             f"{trans['proforma_number']} {order_info[0]}_{order_info[1]}_{order_info[10]}\n"
#             f"{trans['event_date']} {order_info[2]}\n"
#             f"{trans['time']} {order_info[3]} - {order_info[4]}\n"
#             f"{trans['people_count']} {order_info[5]}\n"
#             f"{trans['event_style']} {order_info[6]}\n"
#             f"{trans['city']} {order_info[7]}\n"
#             f"{trans['amount_to_pay']} {float(order_info[8]) - 20} евро\n"
#             f"\n{trans['delivery_info']}"
#         )
#
#         # Отправляем сообщение пользователю
#         bot = Bot(token=BOT_TOKEN)
#         message = await bot.send_message(chat_id=user_id, text=user_message)
#
#         logging.info(f"Message sent to user {user_id}.")
#
#         # Обновляем статус ордера
#         conn = sqlite3.connect(DATABASE_PATH)
#         cursor = conn.cursor()
#         cursor.execute(
#             "UPDATE orders SET status = ? WHERE user_id = ? AND session_number = ?",
#             (ORDER_STATUS["5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ"], user_id, session_number)
#         )
#         conn.commit()
#
#         return message
#
#     except Exception as e:
#         logging.error(f"Failed to send order info to user: {e}")
#         print(f"Ошибка при отправке сообщения: {e}")
#
#     if conn:  # Проверяем, инициализирована ли переменная
#
#         conn.close()
