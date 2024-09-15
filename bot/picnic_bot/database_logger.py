import logging
import psycopg2

# Настройка логирования
logging.basicConfig(
    filename='db_operations.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'  # Устанавливаем кодировку UTF-8
)

def log_message(message):
    logging.info(message)

def log_query(query, params=()):
    logging.info(f'Executing query: {query} with params: {params}')

def execute_query_with_logging(conn, query, params=()):
    try:
        cursor = conn.cursor()  # Открываем курсор для выполнения запроса
        log_query(query, params)
        cursor.execute(query, params)
        conn.commit()  # Подтверждаем транзакцию
        log_message('Query executed successfully.')
    except psycopg2.Error as e:  # Обрабатываем ошибки PostgreSQL
        log_message(f'Error executing query: {e}')
    finally:
        cursor.close()  # Закрываем курсор после выполнения запроса
