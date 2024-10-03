import psycopg2
from psycopg2 import OperationalError
import logging

from bot.picnic_bot.abstract_functions import create_connection

# Функция для инициализации базы данных
def initialize_db():
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()

        # Создание таблицы пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username TEXT,
            status INTEGER,
            number_of_events INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Создание таблицы заказов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            user_id INTEGER,
            session_number INTEGER,  -- Номер сессии
            user_name TEXT,  -- Имя пользователя
            language TEXT,  -- Язык пользователя
            selected_date TIMESTAMP,
            start_time TIME,  -- Время начала мероприятия
            end_time TIME,  -- Время окончания мероприятия
            duration INTEGER,  -- Длительность мероприятия
            people_count INTEGER,  -- Количество участников
            selected_style TEXT,  -- Выбранный стиль мероприятия
            preferences TEXT,  -- Предпочтения пользователя
            city TEXT,  -- Город проведения мероприятия
            status INTEGER,  -- Статус заказа
            calculated_cost INTEGER,  -- Рассчитанная стоимость мероприятия
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        ''')

        # Применение изменений
        conn.commit()
        logging.info("Таблицы успешно созданы в базе данных")

        # Закрытие соединения
        cursor.close()
        conn.close()
    else:
        logging.error("Не удалось установить соединение с базой данных")

if __name__ == '__main__':
    initialize_db()
