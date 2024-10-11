import asyncio
import logging
import os

import psycopg2
from psycopg2 import OperationalError
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from bot.picnic_bot.abstract_functions import create_connection, execute_query, execute_query_with_retry
from bot.picnic_bot.constants import TemporaryData, ORDER_STATUS, UserData
from bot.picnic_bot.keyboards import (yes_no_keyboard, generate_calendar_keyboard, generate_time_selection_keyboard,
                       generate_person_selection_keyboard, generate_party_styles_keyboard)
from bot.picnic_bot.order_info_sender import send_message_to_admin_and_service  # функция отправки
                                     # сообщений АдминБоту для сценария админа и сервисной службы
from dotenv import load_dotenv
# Загрузка переменных из .env файла
load_dotenv()


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data
    step = user_data.get_step()

    if step == 'greeting':
        await handle_name(update, context)
    elif step == 'preferences_request':
        await handle_preferences(update, context)
    elif step == 'city_request':
        await handle_city(update, context)
    else:
        await update.message.reply_text(
            get_translation(user_data, 'buttons_only'),  # Используем функцию для получения перевода
            reply_markup=get_current_step_keyboard(step, user_data)
        )

def check_client_is_exist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Инициализация данных пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    # Создайте соединение с базой данных
    conn = create_connection()
    if conn is not None:
        try:
            # Проверка существования пользователя
            logging.info(f"Проверка существования пользователя с user_id: {update.message.from_user.id}")
            select_query = "SELECT 1 FROM users WHERE user_id = %s"
            cursor = conn.cursor()
            cursor.execute(select_query, (update.message.from_user.id,))
            exists = cursor.fetchone()

            if not exists:
                # Вставка нового пользователя в users
                logging.info(f"Вставка нового пользователя: {user_data.get_username()}")

                # Задаем начальные значения для status и number_of_events которые ввели для АдминБота
                status = 0  # Начальное значение для статуса
                number_of_events = 0  # Начальное значение для счетчика событий

                insert_query = "INSERT INTO users (user_id, username, status, number_of_events) VALUES (%s, %s, %s, %s)"
                insert_params = (update.message.from_user.id, user_data.get_username(), status, number_of_events)
                execute_query_with_retry(conn, insert_query, insert_params)

                print(f"Принт 9: user_id {update.message.from_user.id} сохранен в таблицу orders")
                return False

            return True

        except Exception as e:
            logging.error(f"Ошибка базы данных: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных")
        return False


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Инициализация данных пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    print("Принт 1: Начало функции handle_name")

    if update.callback_query:
        print("Принт 2: Обнаружен callback_query")
        user_data.set_name("Имя пользователя")
    else:
        print("Принт 3: Получено сообщение от пользователя")
        print(f"Принт 4: Значение из update.message.text: {update.message.text}")
        user_data.set_name(update.message.text)
        print(f"Принт 5: Имя пользователя, присвоенное в user_data: {user_data.get_name()}")

    print("Принт 6: После блока if update.callback_query")

    user_data.set_step('name_received')
    user_data.set_username(update.message.from_user.username if update.message else "Имя пользователя")

    print(f"Принт 7: Имя пользователя из update.message.text: {update.message.text}")

    language_code = user_data.get_language()
    print(f"Принт 8: Сохранение user_name: {user_data.get_name()} и username: {user_data.get_username()}")

    logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # Проверка существования пользователя
    exists = check_client_is_exist(update, context)

    if exists:
        # Создайте соединение с базой данных
        conn = create_connection()
        if conn is not None:
            try:

                # Обновление имени пользователя в таблице orders
                logging.info(f"Обновление имени пользователя: {user_data.get_name()}")

                # Получаем session_number для обновления записи
                session_number_query = "SELECT MAX(session_number) FROM orders WHERE user_id = %s"
                cursor = conn.cursor()
                cursor.execute(session_number_query, (update.message.from_user.id,))
                session_number = cursor.fetchone()[0]

                if session_number is None:
                    logging.error("Не удалось получить session_number. Возможно, записи в базе данных отсутствуют.")
                else:
                    update_query = "UPDATE orders SET user_name = %s WHERE user_id = %s AND session_number = %s"
                    update_params = (user_data.get_name(), update.message.from_user.id, session_number)
                    execute_query_with_retry(conn, update_query, update_params)

                # Теперь сохраняем user_id в таблицу orders
                save_user_id_to_orders(update.message.from_user.id, user_data.get_name())

            except Exception as e:
                logging.error(f"Ошибка базы данных: {e}")
            finally:
                conn.close()
                logging.info("Соединение с базой данных закрыто")
        else:
            logging.error("Не удалось создать соединение с базой данных")

    greeting_texts = {
        'en': f'Hello {user_data.get_name()}! Do you want to see available dates?',
        'ru': f'Привет {user_data.get_name()}! Хочешь увидеть доступные даты?',
        'es': f'Hola {user_data.get_name()}! ¿Quieres ver las fechas disponibles?',
        'fr': f'Bonjour {user_data.get_name()}! Voulez-vous voir les dates disponibles?',
        'uk': f'Привіт {user_data.get_name()}! Хочеш подивитися які дати доступні?',
        'pl': f'Cześć {user_data.get_name()}! Chcesz zobaczyć dostępne daty?',
        'de': f'Hallo {user_data.get_name()}! Möchten Sie verfügbare Daten sehen?',
        'it': f'Ciao {user_data.get_name()}! Vuoi vedere le date disponibili?'
    }

    if update.message:
        print("Принт 12: Ответ пользователю с использованием update.message")
        await update.message.reply_text(
            greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
            reply_markup=yes_no_keyboard(language_code)
        )
    elif update.callback_query:
        print("Принт 13: Ответ пользователю с использованием update.callback_query")
        await update.callback_query.message.reply_text(
            greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
            reply_markup=yes_no_keyboard(language_code)
        )

    print("Принт 14: Конец функции handle_name")


def create_connection():
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
    except OperationalError as e:
        logging.error(f"Error connecting to database: {e}")
        return None



def update_order_data(query, params, user_id):
    """Обновляет данные в таблице orders с проверками и обработкой ошибок."""
    conn = create_connection()  # Подключение к PostgreSQL

    if conn is not None:
        try:
            # Проверка существования записи для данного user_id
            check_query = "SELECT 1 FROM orders WHERE user_id = %s"
            cursor = conn.cursor()
            cursor.execute(check_query, (user_id,))
            exists = cursor.fetchone()

            if exists:
                logging.info(f"Запись для user_id {user_id} уже существует в таблице orders.")
            else:
                logging.info(f"Вставка нового user_id {user_id} в таблицу orders.")
                insert_query = """
                    INSERT INTO orders (user_id, session_number, user_name, language, selected_date, start_time, end_time, duration, people_count, selected_party_style, city, preferences, status)
                    VALUES (%s, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1)
                """
                cursor.execute(insert_query, (user_id,))
                conn.commit()
                logging.info(f"user_id {user_id} успешно добавлен в таблицу orders с NULL для полей.")

            # Выполнение обновления данных
            logging.info(f"Выполнение запроса: {query} с параметрами {params}")
            cursor.execute(query, params)
            conn.commit()
            logging.info(f"Запрос успешно выполнен: {query} с параметрами {params}")

        except psycopg2.Error as e:
            logging.error(f"Ошибка базы данных при выполнении запроса: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных для выполнения запроса")


# Функция для обработки выбора даты
async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор даты пользователем и обновляет поле start_time в таблице orders."""
    user_id = update.callback_query.from_user.id
    selected_date = update.callback_query.data.split('_')[1]  # Извлекаем выбранную дату из callback_data

    update_order_data(user_id, selected_date, "UPDATE orders SET selected_date = %s WHERE user_id = %s")
    print(f"Дата {selected_date} обновлена в таблице orders для user_id {user_id}")

    await update.callback_query.message.reply_text(f"Вы выбрали дату: {selected_date}")



def get_translation(user_data, key):
    language_code = user_data.get_language()  # Получаем код языка пользователя
    return translations.get(language_code, translations['en'])  # Возвращаем перевод или английский по умолчанию


# Функция для обработки имени
async def handle__name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    user_data = context.user_data.get('user_data', UserData())
    user_data.set_name(update.message.text)
    user_data.set_step('name_received')
    context.user_data['user_data'] = user_data

    language_code = user_data.get_language()

    greeting_texts = {
        'en': f'Hello {user_data.get_name()}! Do you want to see available dates?',
        'ru': f'Привет {user_data.get_name()}! Хочешь увидеть доступные даты?',
        'es': f'¡Hola {user_data.get_name()}! ¿Quieres ver las fechas disponibles?',
        'fr': f'Bonjour {user_data.get_name()}! Voulez-vous voir les dates disponibles?',
        'uk': f'Привіт {user_data.get_name()}! Хочеш подивитися доступні дати?',
        'pl': f'Cześć {user_data.get_name()}! Chcesz zobaczyć dostępne daty?',
        'de': f'Hallo {user_data.get_name()}! Möchten Sie verfügbare Daten sehen?',
        'it': f'Ciao {user_data.get_name()}! Vuoi vedere le date disponibili?'
    }

    await update.message.reply_text(
        greeting_texts.get(language_code, f'Hello {user_data.get_name()}! Do you want to see available dates?'),
        reply_markup=yes_no_keyboard(language_code)
    )


# Функция для обработки предпочтений
async def handle_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    user_data.set_preferences(update.message.text)
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    # Получаем session_number для обновления записи
    session_number_query = "SELECT MAX(session_number) FROM orders WHERE user_id = %s"
    conn = create_connection()   #(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(session_number_query, (user_data.get_user_id(),))
    session_number = cursor.fetchone()[0]

    if session_number is None:
        logging.error("Не удалось получить session_number. Возможно, записи в базе данных отсутствуют.")
    else:
        logging.info(f"Используем session_number: {session_number} для обновления.")

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET preferences = %s WHERE user_id = %s AND session_number = %s",
            (update.message.text, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

    user_data.set_step('preferences_received')
    context.user_data['user_data'] = user_data

    language_code = user_data.get_language()

    city_request_texts = {
        'en': 'Please specify the city for the event.',
        'ru': 'Пожалуйста укажите город проведения ивента.',
        'es': 'Por favor, especifique la ciudad para el evento.',
        'fr': 'Veuillez indiquer la ville pour l\'événement.',
        'uk': 'Будь ласка, вкажіть місто проведення івенту.',
        'pl': 'Proszę podać miasto, w którym odbędzie się wydarzenie.',
        'de': 'Bitte geben Sie die Stadt für die Veranstaltung an.',
        'it': 'Si prega di specificare la città per l\'evento.'
    }

    await update.message.reply_text(
        city_request_texts.get(language_code, 'Please specify the city for the event.')
    )
    user_data.set_step('city_request')


# Обработчик города
async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    user_data.set_city(update.message.text)
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    # Получаем session_number для обновления записи
    session_number_query = "SELECT MAX(session_number) FROM orders WHERE user_id = %s"
    conn = create_connection()    #(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(session_number_query, (user_data.get_user_id(),))
    session_number = cursor.fetchone()[0]

    if session_number is None:
        logging.error("Не удалось получить session_number. Возможно, записи в базе данных отсутствуют.")
    else:
        logging.info(f"Используем session_number: {session_number} для обновления.")

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET city = %s WHERE user_id = %s AND session_number = %s",
            (update.message.text, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

    context.user_data['user_data'] = user_data

    # Переходим к следующему шагу
    await handle_city_confirmation(update, context)


# Обработчик подтверждения города и отправка ордера
async def handle_city_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())

    if user_data.get_step() == 'city_request':  # Убедимся, что переходим на правильный шаг
        # Подтверждение сохранения данных
        confirmation_texts = {
            'en': "Please wait for the calculation...",
            'ru': "Ожидайте расчета...",
            'es': "Espere el cálculo...",
            'fr': "Veuillez attendre le calcul...",
            'uk': "Очікуйте розрахунку...",
            'pl': "Proszę czekać na obliczenia...",
            'de': "Bitte warten Sie auf die Berechnung...",
            'it': "Attendere il calcolo..."
        }
        # Отправляем сообщение "Ожидайте расчета..."
        message = await update.message.reply_text(
            confirmation_texts.get(user_data.get_language())
        )

        # Добавляем искусственную задержку для создания эффекта ожидания
        await asyncio.sleep(1.5)  # Задержка в 2 секунды

        # Эффект "взрыва" перед генерацией текста ордера
        await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text="💥💥💥")
        await asyncio.sleep(0.3)  # Небольшая задержка для эффекта

        # Удаляем сообщение
        await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)

        # Генерация текста ордера
        order_summary = generate_order_summary(user_data)

        # Отправляем текст ордера клиенту
        await update.message.reply_text(order_summary)
        confirmation_texts = {
            'en': "Do you want to confirm this booking?",
            'ru': "Хочешь забронировать (Да) или изменить данные (Нет)?",
            'es': "¿Desea confirmar esta reserva?",
            'fr': "Voulez-vous confirmer cette réservation?",
            'uk': "Хочеш підтвердити це бронювання?",
            'pl': "Czy chcesz potwierdzić tę rezerwację?",
            'de': "Möchten Sie diese Buchung bestätigen?",
            'it': "Vuoi confermare questa prenotazione?"
        }
        confirmation_message = confirmation_texts.get(user_data.get_language(), confirmation_texts['en'])
        user_data.set_step('order_sent')
        await update.message.reply_text(
            confirmation_message,
            reply_markup=yes_no_keyboard(user_data.get_language())
        )


# Функция генерации текста ордера
def generate_order_summary(user_data):
    order_texts = {
        'en': {
            'order_check': "Please review your booking order:",
            'order_number': "Order №",
            'client_name': "Client Name",
            'preferences': "Preferences",
            'city': "City",
            'people_count': "Number of People",
            'date': "Date",
            'start_time': "Event Start Time",
            'duration': "Event Duration",
            'total_cost': "Total Cost",
            'style': "Event Style"
        },
        'ru': {
            'order_check': "Проверьте ваш ордер на бронирование:",
            'order_number': "Ордер №",
            'client_name': "Имя клиента",
            'preferences': "Предпочтения",
            'city': "Город",
            'people_count': "Количество персон",
            'date': "Дата",
            'start_time': "Начало ивента",
            'duration': "Продолжительность ивента",
            'total_cost': "Общая стоимость",
            'style': "Стиль мероприятия"
        },
        'es': {
            'order_check': "Por favor, revise su orden de reserva:",
            'order_number': "Orden №",
            'client_name': "Nombre del cliente",
            'preferences': "Preferencias",
            'city': "Ciudad",
            'people_count': "Número de personas",
            'date': "Fecha",
            'start_time': "Hora de inicio del evento",
            'duration': "Duración del evento",
            'total_cost': "Costo total",
            'style': "Estilo del evento"
        },
        'fr': {
            'order_check': "Veuillez vérifier votre commande de réservation :",
            'order_number': "Commande №",
            'client_name': "Nom du client",
            'preferences': "Préférences",
            'city': "Ville",
            'people_count': "Nombre de personnes",
            'date': "Date",
            'start_time': "Heure de début de l'événement",
            'duration': "Durée de l'événement",
            'total_cost': "Coût total",
            'style': "Style de l'événement"
        },
        'uk': {
            'order_check': "Перевірте ваше замовлення на бронювання:",
            'order_number': "Замовлення №",
            'client_name': "Ім'я клієнта",
            'preferences': "Уподобання",
            'city': "Місто",
            'people_count': "Кількість осіб",
            'date': "Дата",
            'start_time': "Час початку заходу",
            'duration': "Тривалість заходу",
            'total_cost': "Загальна вартість",
            'style': "Стиль заходу"
        },
        'pl': {
            'order_check': "Proszę sprawdzić swoje zamówienie na rezerwację:",
            'order_number': "Zamówienie №",
            'client_name': "Imię klienta",
            'preferences': "Preferencje",
            'city': "Miasto",
            'people_count': "Liczba osób",
            'date': "Data",
            'start_time': "Czas rozpoczęcia wydarzenia",
            'duration': "Czas trwania wydarzenia",
            'total_cost': "Całkowity koszt",
            'style': "Styl wydarzenia"
        },
        'de': {
            'order_check': "Bitte überprüfen Sie Ihre Buchungsbestellung:",
            'order_number': "Bestellnummer №",
            'client_name': "Kundenname",
            'preferences': "Vorlieben",
            'city': "Stadt",
            'people_count': "Anzahl der Personen",
            'date': "Datum",
            'start_time': "Beginn der Veranstaltung",
            'duration': "Dauer der Veranstaltung",
            'total_cost': "Gesamtkosten",
            'style': "Veranstaltungsstil"
        },
        'it': {
            'order_check': "Si prega di controllare il vostro ordine di prenotazione:",
            'order_number': "Ordine №",
            'client_name': "Nome del cliente",
            'preferences': "Preferenze",
            'city': "Città",
            'people_count': "Numero di persone",
            'date': "Data",
            'start_time': "Orario di inizio dell'evento",
            'duration': "Durata dell'evento",
            'total_cost': "Costo totale",
            'style': "Stile dell'evento"
        }
    }

    subscript_text = {
        'en': (
            "Formula for calculation:\n"
            "- Minimum cost: 2 persons for 2 hours - 160 euros\n"
            "- Each additional person: 20 euros\n"
            "- Each additional hour: 30 euros for all\n"
        ),
        'ru': (
            "Формула расчета:\n"
            "- Минимальная стоимость: 2 персоны на 2 часа - 160 евро\n"
            "- Каждая дополнительная персона: 20 евро\n"
            "- Каждый дополнительный час: 30 евро для всех\n"
        ),
        'es': (
            "Fórmula de cálculo:\n"
            "- Costo mínimo: 2 personas por 2 horas - 160 euros\n"
            "- Cada persona adicional: 20 euros\n"
            "- Cada hora adicional: 30 euros para todos\n"
        ),
        'fr': (
            "Formule de calcul:\n"
            "- Coût minimum : 2 personnes pour 2 heures - 160 euros\n"
            "- Chaque personne supplémentaire : 20 euros\n"
            "- Chaque heure supplémentaire : 30 euros pour tous\n"
        ),
        'uk': (
            "Формула розрахунку:\n"
            "- Мінімальна вартість: 2 особи на 2 години - 160 євро\n"
            "- Кожна додаткова особа: 20 євро\n"
            "- Кожна додаткова година: 30 євро для всіх\n"
        ),
        'pl': (
            "Formuła obliczeń:\n"
            "- Minimalny koszt: 2 osoby na 2 godziny - 160 euro\n"
            "- Każda dodatkowa osoba: 20 euro\n"
            "- Każda dodatkowa godzina: 30 euro dla wszystkich\n"
        ),
        'de': (
            "Berechnungsformel:\n"
            "- Mindestkosten: 2 Personen für 2 Stunden - 160 Euro\n"
            "- Jede zusätzliche Person: 20 Euro\n"
            "- Jede zusätzliche Stunde: 30 Euro für alle\n"
        ),
        'it': (
            "Formula di calcolo:\n"
            "- Costo minimo: 2 persone per 2 ore - 160 euro\n"
            "- Ogni persona aggiuntiva: 20 euro\n"
            "- Ogni ora aggiuntiva: 30 euro per tutti\n"
        )
    }

    lang = user_data.get_language()

    order_id = f"{user_data.get_user_id()}_{user_data.get_session_number()}"
    order_text = f"{order_texts[lang]['order_check']}\n\n{order_texts[lang]['order_number']} {order_id}\n"
    order_text += "____________________\n"

    # Добавляем к ордеру все введенные данные
    if user_data.get_name():
        order_text += f"{order_texts[lang]['client_name']}: {user_data.get_name()}\n"
    if user_data.get_preferences():
        order_text += f"{order_texts[lang]['preferences']}: {user_data.get_preferences()}\n"
    if user_data.get_style():
        order_text += f"{order_texts[lang]['style']}: {user_data.get_style()}\n"
    if user_data.get_city():
        order_text += f"{order_texts[lang]['city']}: {user_data.get_city()}\n"
    if user_data.get_person_count():
        order_text += f"{order_texts[lang]['people_count']}: {user_data.get_person_count()}\n"
    if user_data.get_selected_date():
        order_text += f"{order_texts[lang]['date']}: {user_data.get_selected_date()}\n"
    if user_data.get_start_time():
        order_text += f"{order_texts[lang]['start_time']}: {user_data.get_start_time()}\n"
    if user_data.get_duration():
        # Преобразуем длительность в часы на основе языка
        duration_translations = {
            'en': 'hours',
            'ru': 'часа',
            'es': 'horas',
            'fr': 'heures',
            'uk': 'години',
            'pl': 'godzin',
            'de': 'Stunden',
            'it': 'ore'
        }
        duration_text = f"{user_data.get_duration()} {duration_translations.get(lang, 'hours')}"
        order_text += f"{order_texts[lang]['duration']}: {duration_text}\n"
    if user_data.get_calculated_cost() is not None:
        order_text += "____________________\n"
        order_text += f"{order_texts[lang]['total_cost']}: {user_data.get_calculated_cost()} EUR\n"

    # Добавляем формулу расчета в конце
    order_text += f"\n{subscript_text[lang]}"

    return order_text


def show_payment_page_handler(context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())
    payment_message_texts = {
        'en': "You will be redirected to a secure payment page - Stripe payment platform.\n"
              "Then return to the bot to see your proforma considering your prepayment.",

        'ru': "Вы будете перенаправлены на безопасную страницу оплаты - платформу платежей Stripe.\n"
              "Затем вернитесь в бот, чтобы увидеть вашу Проформу с учетом вашей предоплаты.",

        'es': "Será redirigido a una página de pago segura - plataforma de pagos Stripe.\n"
              "Luego regrese al bot para ver su proforma con el anticipo considerado.",

        'fr': "Vous serez redirigé vers une page de paiement sécurisée - plateforme de paiement Stripe.\n"
              "Ensuite, revenez dans le bot pour voir votre proforma tenant compte de votre prépaiement.",

        'uk': "Вас буде перенаправлено на безпечну сторінку оплати - платформу платежів Stripe.\n"
              "Потім поверніться в бот, щоб побачити свою Проформу з урахуванням вашої передоплати.",

        'pl': "Zostaniesz przekierowany na bezpieczną stronę płatności - platformę płatności Stripe.\n"
              "Następnie wróć do bota, aby zobaczyć swoją proformę z uwzględnieniem przedpłaty.",

        'de': "Sie werden auf eine sichere Zahlungsseite weitergeleitet - Zahlungsplattform Stripe.\n"
              "Kehren Sie dann in den Bot zurück, um Ihre Proforma mit Ihrer Vorauszahlung zu sehen.",

        'it': "Verrai reindirizzato a una pagina di pagamento sicura - piattaforma di pagamento Stripe.\n"
              "Torna quindi al bot per vedere la tua proforma tenendo conto del tuo pagamento anticipato."
    }
    language_code = user_data.get_language()
    payment_message = payment_message_texts.get(language_code, payment_message_texts['en'])

    # Текст кнопки на разных языках
    button_texts = {
        'en': "Complete Booking and Get PROFORMA",
        'ru': "Завершить бронирование и получить ПРОФОРМУ",
        'es': "Completar reserva y obtener PROFORMA",
        'fr': "Terminer la réservation et obtenir la PROFORMA",
        'uk': "Завершити бронювання та отримати ПРОФОРМУ",
        'pl': "Zakończ rezerwację i uzyskaj PROFORMĘ",
        'de': "Buchung abschließen und PROFORMA erhalten",
        'it': "Completa la prenotazione e ottieni la PROFORMA"
    }

    language_code = user_data.get_language()
    button_text = button_texts.get(language_code, button_texts['en'])  # Используем английский текст по умолчанию

    stripe_link = os.getenv('BASE_URL')

    # Создание кнопки
    button = InlineKeyboardButton(button_text, url=stripe_link)

    # Добавление кнопки в разметку и отправка пользователю
    reply_markup = InlineKeyboardMarkup([[button]])

    return (payment_message, reply_markup)



async def show_proforma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем данные пользователя
    global proforma_number
    user_data = context.user_data.get('user_data', UserData())

    # Получаем user_id из user_data
    user_id = user_data.get_user_id()

    last_order = get_latest_order(user_id)


    # Обновляем статус пользователя в таблице orders до "зарезервировано"
    conn = create_connection()  # Изменено для подключения к PostgreSQL
    if conn is not None:
        try:
            # Проверка текущего максимального session_number для user_id
            select_query = "SELECT MAX(session_number) FROM orders WHERE user_id = %s"  # Замена ? на %s для PostgreSQL
            cursor = conn.cursor()
            cursor.execute(select_query, (user_id,))
            current_session = cursor.fetchone()[0]

            user_data.set_session_number(current_session)

            if current_session is None:
                logging.error(f"Ошибка обновления статуса в таблице orders для user_id {user_id}")
            else:
                # Обновляем статус заказа
                update_query = "UPDATE orders SET status = %s WHERE user_id = %s AND session_number = %s"
                cursor.execute(update_query, (
                ORDER_STATUS["3-зарезервировано - заказчик оплатил аванс"], user_id, current_session))
                conn.commit()
                logging.info(f"User {user_id}: статус обновлен до 'зарезервировано'.")
        except psycopg2.Error as e:
            logging.error(f"Ошибка обновления статуса в таблице orders: {e}")
        finally:
            conn.close()

    # Получаем номер проформы (номер ордера с добавлением статуса "_3")

    #
    # SELECT
    # order_id_0, user_id_1, session_number_2, user_name_3, selected_date_5, start_time_6, end_time_7, duration_8,
    # people_count_9, selected_style_10, preferences_11, city_12 calculated_cost_14
    proforma_number = f"{last_order[1]}_{last_order[2]}_3"
    selected_date = last_order[5]
    start_time = last_order[6]
    end_time = last_order[7]
    person_count = last_order[9]
    calculated_cost = last_order[14]


    # Тексты проформы на разных языках
    proforma_texts = {
        'en': (
            f"PROFORMA № {proforma_number}\n"
            f"_______________________\n"
            f"DATE: {selected_date}\n"
            f"TIME: {start_time} - {end_time}\n"
            f"PEOPLE: {person_count}\n"
            f"PREPAYMENT: 20 euros\n"
            f"AMOUNT TO PAY (excluding reservation):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} euros"
        ),
        'ru': (
            f"ПРОФОРМА № {proforma_number}\n"
            f"_______________________\n"
            f"ДАТА: {selected_date}\n"
            f"ВРЕМЯ: {start_time} - {end_time}\n"
            f"ПЕРСОН: {person_count}\n"
            f"ПРЕДОПЛАТА: 20 евро\n"
            f"СУММА К ОПЛАТЕ (за вычетом резерва):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} евро"
        ),
        'es': (
            f"PROFORMA N.º {proforma_number}\n"
            f"_______________________\n"
            f"FECHA: {selected_date}\n"
            f"HORA: {start_time} - {end_time}\n"
            f"PERSONAS: {person_count}\n"
            f"PREPAGO: 20 euros\n"
            f"CANTIDAD A PAGAR (excluyendo reserva):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} euros"
        ),
        'fr': (
            f"PROFORMA N° {proforma_number}\n"
            f"_______________________\n"
            f"DATE: {selected_date}\n"
            f"HEURE: {start_time} - {end_time}\n"
            f"PERSONNES: {person_count}\n"
            f"PRÉPAYEMENT: 20 euros\n"
            f"MONTANT À PAYER (hors réservation):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} euros"
        ),
        'uk': (
            f"ПРОФОРМА № {proforma_number}\n"
            f"_______________________\n"
            f"ДАТА: {selected_date}\n"
            f"ЧАС: {start_time} - {end_time}\n"
            f"ЛЮДЕЙ: {person_count}\n"
            f"ПЕРЕДОПЛАТА: 20 євро\n"
            f"СУМА ДО СПЛАТИ (за вирахуванням резерву):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} євро"
        ),
        'pl': (
            f"PROFORMA NR {proforma_number}\n"
            f"_______________________\n"
            f"DATA: {selected_date}\n"
            f"GODZINA: {start_time} - {end_time}\n"
            f"LUDZI: {person_count}\n"
            f"PRZEDPŁATA: 20 euro\n"
            f"KWOTA DO ZAPŁATY (z wyłączeniem rezerwacji):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} euro"
        ),
        'de': (
            f"PROFORMA NR {proforma_number}\n"
            f"_______________________\n"
            f"DATUM: {selected_date}\n"
            f"ZEIT: {start_time} - {end_time}\n"
            f"PERSONEN: {person_count}\n"
            f"VORAUSZAHLUNG: 20 Euro\n"
            f"BETRAG ZUR ZAHLUNG (ohne Reservierung):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} Euro"
        ),
        'it': (
            f"PROFORMA N. {proforma_number}\n"
            f"_______________________\n"
            f"DATA: {selected_date}\n"
            f"ORARIO: {start_time} - {end_time}\n"
            f"PERSONE: {person_count}\n"
            f"ANTICIPO: 20 euro\n"
            f"IMPORTO DA PAGARE (esclusa la prenotazione):\n"
            f"_______________________\n"
            f"{calculated_cost - 20} euro"
        )
    }

    # Определяем язык и текст проформы
    language_code = user_data.get_language()
    proforma_text = proforma_texts.get(language_code, proforma_texts['ru'])  # Используем русский текст по умолчанию

    # Текст кнопки на разных языках
    button_texts = {
        'en': "Complete Booking and Get PROFORMA",
        'ru': "Завершить бронирование и получить ПРОФОРМУ",
        'es': "Completar reserva y obtener PROFORMA",
        'fr': "Terminer la réservation et obtenir la PROFORMA",
        'uk': "Завершити бронювання та отримати ПРОФОРМУ",
        'pl': "Zakończ rezerwację i uzyskaj PROFORMĘ",
        'de': "Buchung abschließen und PROFORMA erhalten",
        'it': "Completa la prenotazione e ottieni la PROFORMA"
    }

    language_code = user_data.get_language()
    button_text = button_texts.get(language_code, button_texts['en'])  # Используем английский текст по умолчанию

    # Ссылка на админбот с автоматическим запуском команды /start
    admin_bot_username = "AssistPicnicsBot"  # Убираем символ '@'
    admin_bot_link = f"https://t.me/{admin_bot_username}?start=start"

    # Создание кнопки
    button = InlineKeyboardButton(button_text, url=admin_bot_link)

    # Добавление кнопки в разметку и отправка пользователю
    reply_markup = InlineKeyboardMarkup([[button]])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=proforma_text, reply_markup=reply_markup)

    await send_message_to_admin_and_service(user_data.get_user_id(), user_data.get_session_number())


    # чистка кеша - обнуление класса USER_DATA
    reset_user_data(user_data)

def reset_user_data(data):
    data.name = None
    data.preferences = None
    data.city = None
    data.month_offset = 0
    data.step = None
    data.start_time = None
    data.end_time = None
    data.person_count = None
    data.style = None
    data.date = None
    data.session_number = None  # Добавляем свойство session_number
    data.calculated_cost = None  # Добавляем новое свойство

    # Функция для получения текущей клавиатуры для шага
def get_current_step_keyboard(step, user_data):
    language = user_data.get_language()
    if step == 'calendar':
        month_offset = user_data.get_month_offset() if hasattr(user_data, 'get_month_offset') else 0
        return generate_calendar_keyboard(month_offset, language)
    elif step == 'time_selection':
        print(user_data.get_selected_date())
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDd")
        return generate_time_selection_keyboard(language, 'start', user_data.get_selected_date())
    elif step == 'people_selection':
        return generate_person_selection_keyboard(language)
    elif step == 'style_selection':
        return generate_party_styles_keyboard(language)
    else:
        return None


# Словарь с переводами сообщения "Выбор только кнопками" на разные языки
translations = {
    'en': "Please use the buttons",
    'ru': "Выбор только кнопками",
    'es': "Por favor, usa los botones",
    'fr': "Veuillez utiliser les boutons",
    'de': "Bitte verwenden Sie die Tasten",
    'it': "Si prega di utilizzare i pulsanti",
    'uk': "Будь ласка, використовуйте кнопки",
    'pl': "Proszę użyć przycisków"
}

def save_user_id_to_orders(user_id,user_n):
    """Сохраняет user_id в таблицу orders с начальным значением null для даты."""
    conn = create_connection()
    if conn is not None:
        try:
            logging.info(f"Проверка существования записи в orders для user_id: {user_id}")
            select_query = "SELECT 1 FROM orders WHERE user_id = %s"
            cursor = conn.cursor()
            cursor.execute(select_query, (user_id,))
            exists = cursor.fetchone()

            if exists:
                logging.info(f"Запись для user_id {user_id} уже существует в таблице orders.")
            else:
                logging.info(f"Вставка нового user_id {user_id} с null датой в таблицу orders.")
                insert_query = "INSERT INTO orders (user_id, user_name, selected_date) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (user_id, user_n, None))  # Передаем None для заполнения null в базе данных
                conn.commit()
                logging.info(f"user_id {user_id} успешно добавлен в таблицу orders с null датой.")

        except Exception as e:
            logging.error(f"Ошибка базы данных при работе с таблицей orders: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных для работы с таблицей orders")


# Функция для получения перевода на основе языка пользователя
def get_translation(user_data, key):
    language_code = user_data.get_language()  # Получаем код языка пользователя
    return translations.get(language_code, translations['en'])  # Возвращаем перевод или английский по умолчанию

def get_latest_order(user_id):
    """
    Получаем максимальный ордер по session_number со статусом 2
    """
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Сначала пытаемся найти session_number со статусом 2 (2-заполнено для расчета)
        cursor.execute("""
            SELECT * 
            FROM orders 
            WHERE user_id = %s 
            AND status = %s 
            ORDER BY session_number DESC 
            LIMIT 1
        """, (user_id, ORDER_STATUS["2-заполнено для расчета"]))

        result = cursor.fetchone()

        if result:
            return result

        else:
            raise ValueError("Нет подходящих записей для этого пользователя.")

    finally:
        cursor.close()
        conn.close()
