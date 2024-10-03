# shared/helpers.py

import logging
import sqlite3
import time
# Настройка логирования
logger = logging.getLogger(__name__)

def create_connection(db_file):
    """Создает соединение с базой данных SQLite, указанной в db_file."""
    try:
        conn = sqlite3.connect(db_file)
        logger.info(f"Database connected: {db_file}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query, params=()):
    """Выполняет SQL-запрос."""
    if conn is None:
        logger.error("No database connection available")
        return False

    try:
        c = conn.cursor()
        logger.info(f'Executing query: {query} with params: {params}')  # Логирование запроса
        c.execute(query, params)
        conn.commit()
        logger.info(f"Query executed successfully: {query} with params {params}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error executing query: {e}")
        return False
    finally:
        try:
            conn.close()  # Закрытие соединения
            logger.info("Database connection closed")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")

def execute_query_with_retry(conn, query, params=(), max_retries=5):
    """Выполняет SQL-запрос с повторными попытками при блокировке базы данных."""
    retries = 0
    while retries < max_retries:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries += 1
                logger.warning(f"Database is locked, retrying {retries}/{max_retries}")
                time.sleep(1)  # Задержка перед повторной попыткой
            else:
                logger.error(f"Error executing query: {e}")
                return False
        finally:
            if retries >= max_retries:
                logger.error(f"Failed to execute query after {max_retries} retries")
                return False
