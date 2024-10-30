import psycopg2  # Заменили sqlite3 на psycopg2
import logging
#from constants import DATABASE_PATH  # Не забываем обновить в дальнейшем, если понадобится
from datetime import datetime, timedelta, time
import os  # Для использования переменных окружения

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reserved_time_intervals(selected_date):
    logging.info(f"Функция reserved_time_intervals вызвана для даты: {selected_date}")

    # Создаем подключение к базе данных PostgreSQL
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),  # Используем переменные окружения
            database=os.getenv('DB_NAME', 'event_db'),
            user=os.getenv('DB_USER', 'myuser'),
            password=os.getenv('DB_PASSWORD', 'mypassword')
        )
        logging.info("Соединение с базой данных успешно установлено.")
    except Exception as e:
        logging.error(f"Не удалось подключиться к базе данных: {e}")
        return []

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT start_time, end_time 
            FROM orders 
            WHERE status > 2 AND selected_date = %s
        """, (selected_date,))  # Используем %s вместо ?

        reserved_times = cursor.fetchall()
        logging.info(f"Зарезервированные интервалы: {reserved_times}")

        if not reserved_times:
            logging.warning("Нет зарезервированных интервалов для указанной даты.")
            return []

        return reserved_times

    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        return []

    finally:
        cursor.close()  # Закрываем курсор
        conn.close()  # Закрываем соединение
        logging.info("Соединение с базой данных закрыто.")

def check_time_reserved(cur_time, reserved_time_intervals):
    """
    Проверяет, пересекается ли временной интервал с уже зарезервированными временными интервалами.
    """
    timelist = create_reserved_timelist(reserved_time_intervals)

    if cur_time in timelist:
        return True
    return False

def get_reserved_times_for_date(selected_date):
    logging.info(f"Функция get_reserved_times_for_date вызвана для даты: {selected_date}")

    # Получаем все зарезервированные временные интервалы для указанной даты
    reserved_intervals = reserved_time_intervals(selected_date)
    print(reserved_intervals)
    if not reserved_intervals:
        logging.info(f"Для даты {selected_date} нет зарезервированных временных интервалов.")
    return reserved_intervals

def create_reserved_timelist(time_list):
    reserved_time_list = list()

    for i in time_list:
        # logging.info(f"Функция get_reserved_times_for_date вызвана для даты: {i}")

        # start = datetime.strptime(i[0], "%H:%M") - timedelta(hours=5)
        start = timedelta(hours=i[0].hour, minutes=i[0].minute) - timedelta(hours=4, minutes=30)
        # end = datetime.strptime(i[1], "%H:%M") + timedelta(hours=5, minutes=30)
        end = timedelta(hours=i[1].hour, minutes=i[1].minute) + timedelta(hours=5, minutes=30)

        # logging.info(f"Функция get_reserved_times_for_date вызвана для даты: {start}") # 3,5
        # logging.info(f"Функция get_reserved_times_for_date вызвана для даты: {end}") # 15,5


        while start < end:
            # if start.time() > time(7, 30) and start.time() < time(22, 30):
            if start > timedelta(hours=7, minutes=30) and start < timedelta(hours=22, minutes=30):
                hours = int(start.total_seconds() // 3600)
                minutes = int((start.total_seconds() % 3600)//60)
                # reserved_time_list.append(start.strftime('%H:%M'))
                reserved_time_list.append(f"{hours:02d}:{minutes:02d}")
            start += timedelta(minutes=30)
    return reserved_time_list
