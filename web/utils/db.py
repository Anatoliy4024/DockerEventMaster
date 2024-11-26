# db.py
# db.py

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
