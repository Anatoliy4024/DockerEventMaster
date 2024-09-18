# Функция для изменения статуса  (user_id, status) в таблице users БД
#
import sqlite3
from shared.config import DATABASE_PATH


def insert_user_status(user_id, status):
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # SQL-запрос для добавления нового пользователя и его статуса
        cursor.execute("""
            INSERT INTO users (user_id, status) 
            VALUES (?, ?)
            ON CONFLICT(user_id) 
            DO UPDATE SET status = excluded.status;
        """, (7508525320, 0))# Для изменения статуса введи желаемый user_id и номер статуса: 1 - админ, 2-сервисная служба

        # Сохранение изменений
        conn.commit()
        print(f"User ID {user_id} updated with status {status}.")

    except sqlite3.Error as e:
        print(f"Ошибка при вставке данных: {e}")

    finally:
        # Закрытие соединения с базой данных
        if conn:
            conn.close()


# Пример использования
# insert_user_status(123456789, 1)
