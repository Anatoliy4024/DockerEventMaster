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
