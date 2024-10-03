import psycopg2
import logging
from bot.admin_bot.constants import ORDER_STATUS
from bot.admin_bot.translations import translations
import os  # Для работы с переменными окружения
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Функция для подключения к базе данных
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


# def get_db_connection():
#     return psycopg2.connect(
#         host=os.getenv('DATABASE_HOST', 'localhost'),
#         dbname=os.getenv('DATABASE_NAME', 'mydatabase'),
#         user=os.getenv('DATABASE_USER', 'myuser'),
#         password=os.getenv('DATABASE_PASSWORD', 'mypassword')
#     )
#

def get_full_proforma(user_id, session_number):
    """
    Получает полную проформу для пользователя по user_id и session_number.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT user_id, session_number, selected_date, start_time, end_time, people_count, selected_style,
                   city, calculated_cost, preferences, status, order_id
            FROM orders
            WHERE user_id = %s AND session_number = %s
            """,
            (user_id, session_number)
        )
        order_info = cursor.fetchone()

        if order_info:
            return order_info
        else:
            raise ValueError("Нет подходящей проформы для этого пользователя.")

    finally:
        cursor.close()
        conn.close()


# Функция для получения последнего session_number
def get_latest_session_number(user_id):
    """
    Получает максимальный session_number для пользователя с user_id.
    Если найден статус 4, обновляет его на 5 после просмотра проформы.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Сначала пытаемся найти session_number со статусом 4 (Ирина и Сервисная служба получили сообщение)
        cursor.execute("""
            SELECT session_number 
            FROM orders 
            WHERE user_id = %s 
            AND status = %s 
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
                WHERE user_id = %s 
                AND status = %s 
                ORDER BY session_number DESC 
                LIMIT 1
            """, (user_id, ORDER_STATUS["5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ"]))

            result = cursor.fetchone()

            if result:
                return result[0]  # Возвращает session_number для статуса 5
            else:
                raise ValueError("Нет подходящих записей для этого пользователя.")

    finally:
        cursor.close()
        conn.close()
