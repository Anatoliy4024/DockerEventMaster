import logging
import os

import psycopg2
from psycopg2 import OperationalError

from bot.picnic_bot.constants import ORDER_STATUS
#from bot.picnic_bot.main import create_connection


def create_flask_to_db_connection():
    """Создает соединение с базой данных PostgreSQL."""
    try:
        # Получаем параметры подключения из переменных окружения
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        logging.info("Database connected")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Error connecting to database: {e}")
        return None


# Функция для обновления статуса заказа по order_id
def update_order_status_to_paid(order_id):
    conn = create_flask_to_db_connection()  # Подключение к базе данных PostgreSQL

    if conn is not None:
        try:
            cursor = conn.cursor()

            # Обновляем статус заказа по order_id
            update_query = "UPDATE orders SET status = %s WHERE order_id = %s"
            cursor.execute(update_query, (
                ORDER_STATUS["3-зарезервировано - заказчик оплатил аванс"], order_id))
            conn.commit()

            logging.info(f"Order {order_id}: статус обновлен до 'зарезервировано'.")

        except psycopg2.Error as e:
            logging.error(f"Ошибка обновления статуса в таблице orders: {e}")

        finally:
            conn.close()
    else:
        logging.error("Не удалось подключиться к базе данных.")
