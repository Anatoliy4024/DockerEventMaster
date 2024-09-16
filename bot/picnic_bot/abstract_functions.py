import psycopg2
from psycopg2 import OperationalError
import time
from bot.picnic_bot.database_logger import log_message, log_query
from bot.picnic_bot.constants import UserData


def create_connection():
    """Создает соединение с базой данных PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mydatabase",
            user="myuser",
            password="mypassword",
            client_encoding="UTF8"
        )
        log_message("Database connected")
        return conn
    except OperationalError as e:
        log_message(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query, params=()):
    """Выполняет SQL-запрос в PostgreSQL."""
    if conn is None:
        log_message("No database connection available")
        return False

    try:
        with conn.cursor() as cursor:
            log_query(query, params)  # Логирование запроса
            cursor.execute(query, params)
            conn.commit()
            log_message(f"Query executed successfully: {query} with params {params}")
            return True
    except OperationalError as e:
        log_message(f"Error executing query: {e}")
        return False
    finally:
        try:
            conn.close()  # Закрытие соединения
            log_message("Database connection closed")
        except OperationalError as e:
            log_message(f"Error closing database connection: {e}")

def execute_query_with_retry(conn, query, params=(), max_retries=5):
    """Выполняет SQL-запрос с повторными попытками при блокировке базы данных."""
    retries = 0
    while retries < max_retries:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return
        except OperationalError as e:
            if "could not obtain lock" in str(e):  # Сообщение об ошибке блокировки в PostgreSQL
                retries += 1
                log_message(f"Database is locked, retrying {retries}/{max_retries}")
                time.sleep(1)  # Задержка перед повторной попыткой
            else:
                log_message(f"Error executing query: {e}")
                raise e
        finally:
            if retries >= max_retries:
                log_message(f"Failed to execute query after {max_retries} retries")
