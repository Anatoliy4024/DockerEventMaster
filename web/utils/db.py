# db.py
# db.py
import logging

import psycopg2
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def create_connection():
    """Создает соединение с базой данных PostgreSQL напрямую."""
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        client_encoding="UTF8"
    )
    return connection

def get_user_by_email(email):
    """Получает пользователя по email."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def insert_user(email, password):
    """Добавляет нового пользователя."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, registration_password) VALUES (%s, %s);", (email, password))
    conn.commit()
    cursor.close()
    conn.close()

def insert_order(vars_tuple):
    """Добавление нового ордера в БД"""
    conn = create_connection()
    cursor = conn.cursor()
    # insert_query = """
    #                     INSERT INTO orders (user_id, session_number, selected_date, start_time, end_time, duration, people_count,
    #                     selected_style, city, preferences, calculated_cost, status)
    #                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 2)
    #                 """
    # cursor.execute(insert_query, vars_tuple)
    # conn.commit()

    update_query = """
                      UPDATE orders SET user_name = %s, selected_date = %s, start_time = %s, end_time = %s, duration = %s, people_count = %s,
                      selected_style = %s, city = %s, preferences = %s, calculated_cost = %s, status = 2
                      WHERE user_id = %s AND session_number = %s
                   """
    # cursor.execute(update_query, (
    #     ORDER_STATUS["3-зарезервировано - заказчик оплатил аванс"], user_id, current_session))

    cursor.execute(update_query, vars_tuple)

    conn.commit()

    cursor.close()
    conn.close()

def get_order_info(user_id):
    # Создаем соединение с базой данных
    conn = create_connection()  # Используем функцию для подключения к базе данных
    cursor = conn.cursor()

    try:
        # Получаем максимальный session_number для данного пользователя
        cursor.execute("""
            SELECT MAX(session_number) 
            FROM orders 
            WHERE user_id = %s
        """, (user_id,))
        session_number = cursor.fetchone()[0]

        if not session_number:
            raise ValueError("Не найдено подходящего session_number для пользователя")

        # Извлекаем данные ордера для последнего session_number
        cursor.execute("""
            SELECT order_id, user_id, session_number, user_name, language, 
                   selected_date, start_time, end_time, duration, people_count, 
                   selected_style, preferences, city, status, calculated_cost, 
                   created_at, updated_at
            FROM orders 
            WHERE user_id = %s AND session_number = %s
        """, (user_id, session_number))

        order_info = cursor.fetchone()

        if not order_info:
            raise ValueError("Не удалось найти ордер для последнего session_number")

        # Возвращаем информацию в виде словаря для дальнейшего использования
        return {
            'order_id': order_info[0],  # order_id
            'user_id': order_info[1],  # user_id
            'session_number': order_info[2],  # session_number
            'user_name': order_info[3],  # user_name
            'language': order_info[4],  # language
            'selected_date': order_info[5],  # selected_date
            'start_time': order_info[6],  # start_time
            'end_time': order_info[7],  # end_time
            'duration': order_info[8],  # duration
            'people_count': order_info[9],  # people_count
            'selected_style': order_info[10],  # selected_style
            'preferences': order_info[11],  # preferences
            'city': order_info[12],  # city
            'status': order_info[13],  # status
            'calculated_cost': order_info[14],  # calculated_cost
            'created_at': order_info[15],  # created_at
            'updated_at': order_info[16]  # updated_at
        }

    except Exception as e:
        logging.error(f"Ошибка при получении данных ордера: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
