import os
import logging
import random
import sqlite3
import psycopg2
import pytz
from psycopg2 import OperationalError
import time

from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.picnic_bot.abstract_functions import create_connection, execute_query_with_retry
from bot.picnic_bot.constants import (UserData, TemporaryData, time_selection_headers, people_selection_headers,
                                      party_styles_headers, time_set_texts,ORDER_STATUS)
from bot.picnic_bot.database_logger import log_message, log_query
from bot.picnic_bot.keyboards import (language_selection_keyboard, yes_no_keyboard, generate_calendar_keyboard,
                                      generate_time_selection_keyboard, generate_person_selection_keyboard,
                                      generate_party_styles_keyboard)
from bot.picnic_bot.message_handlers import (handle_message, handle_city_confirmation, update_order_data, handle_name,
                                             show_payment_page_handler, show_proforma,
                                             check_client_is_exist, reset_user_data)
from bot.picnic_bot.calculations import calculate_total_cost

from dotenv import load_dotenv

from bot.picnic_bot.status_3 import update_order_status_to_paid, get_last_order_id

# Загрузка переменных из .env файла
load_dotenv()


# Включаем логирование и указываем файл для логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Установите уровень на DEBUG для детальной информации
    filename='db_operations.log',  # Укажите имя файла для логов
    filemode='w'  # 'w' - перезаписывать файл при каждом запуске, 'a' - добавлять к существующему файлу
)

logger = logging.getLogger(__name__)

def get_user_status(user_id):
    try:
        # Подключаемся к базе данных PostgreSQL
        conn = create_connection()
        cursor = conn.cursor()

        # Выполняем SQL-запрос для получения статуса пользователя
        cursor.execute("SELECT status FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Возвращаем статус пользователя
        else:
            return None  # Если пользователь не найден

    except psycopg2.Error as e:
        print(f"Ошибка при получении статуса: {e}")
        return None

    finally:
        if conn:
            conn.close()


# добавление обработчика ошибок
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # Notify the developer via Telegram (if desired)
    if isinstance(update, Update):
        await update.message.reply_text("An error occurred. The administrator has been notified.")

# Пути к видеофайлам
VIDEO_PATHS = [
    'bot/picnic_bot/media/IMG_4077_1 (online-video-cutter.com).mp4',
    'bot/picnic_bot/media/IMG_6156 (online-video-cutter.com).mp4',
    'bot/picnic_bot/media/IMG_5981 (online-video-cutter.com).mp4',
    'bot/picnic_bot/media/IMG_6412 (online-video-cutter.com).mp4'
]

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
# BOT_TOKEN = '7407529729:AAErOT5NBpMSO-V-HPAW-MDu_1WQt0TtXng'

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN_PICNIC')  # Получаем токен из .env файла


# Создайте соединение с базой данных
conn = create_connection()

# Версия "соединение с базой данных" сделанная с 13.00 до 14.00 - 8.08.2024
def execute_query_with_retry(conn, query, params=(), max_retries=5):
    """Выполняет SQL-запрос с повторными попытками при ошибках базы данных."""
    global cursor
    retries = 0
    while retries < max_retries:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return
        except psycopg2.OperationalError as e:
            if retries < max_retries:
                retries += 1
                logging.warning(f"Error occurred, retrying {retries}/{max_retries}")
                time.sleep(1)  # Задержка перед повторной попыткой
            else:
                logging.error(f"Max retries reached. Error: {e}")
                raise e
        finally:
            if cursor:
                cursor.close()

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


def execute_query(conn, query, params=()):
    """Выполняет SQL-запрос."""
    try:
        c = conn.cursor()
        log_query(query, params)  # Логирование запроса
        c.execute(query, params)
        conn.commit()
        log_message(f"Query executed successfully: {query} with params {params}")
    except sqlite3.Error as e:
        log_message(f"Error executing query: {e}")

# Использование в вашей функции start:
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Функция start запущена")

    # Инициализация данных пользователя
    user_data = context.user_data.get('user_data', UserData())
    reset_user_data(user_data)
    context.user_data['user_data'] = user_data

    # Установка начальных данных
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    username = update.message.from_user.username if update.message else update.callback_query.from_user.username

    # Получаем параметр 'start' из данных команды
    start_query = update.message.text if update.message else update.callback_query.data

    # logging.info(f"Получен start_query: {start_query}, update.message.text: {update.message.text}, update.callback_query.data: {update.callback_query}")

    # /start payment_success
    query_param = start_query.split()[-1]

    logging.info(f"Получен start_query: {query_param}")

    # Словари с сообщениями для успешной оплаты и отмены
    payment_messages = {
        'payment_success': {
            'en': "Payment was successful!",
            'ru': "Оплата прошла успешно!",
            'es': "¡El pago fue exitoso!",
            'fr': "Le paiement a été effectué avec succès !",
            'uk': "Оплата пройшла успішно!",
            'pl': "Płatność zakończyła się sukcesem!",
            'de': "Die Zahlung war erfolgreich!",
            'it': "Il pagamento è andato a buon fine!"
        },
        'payment_cancelled': {
            'en': "Payment was cancelled. Returning to the previous step.",
            'ru': "Платеж был отменен. Возвращаем вас на предыдущий шаг.",
            'es': "El pago fue cancelado. Volviendo al paso anterior.",
            'fr': "Le paiement a été annulé. Retour à l'étape précédente.",
            'uk': "Платіж був скасований. Повертаємо вас на попередній крок.",
            'pl': "Płatność została anulowana. Wracamy do poprzedniego kroku.",
            'de': "Die Zahlung wurde abgebrochen. Rückkehr zum vorherigen Schritt.",
            'it': "Il pagamento è stato annullato. Torna al passaggio precedente."
        }
    }

    # Проверка успешной оплаты
    if query_param == "payment_success":
        language_code = user_data.get_language()  # Получаем язык пользователя
        success_message = payment_messages['payment_success'].get(language_code,
                                                                  payment_messages['payment_success']['en'])
        await update.message.reply_text(success_message)
        # Переход на следующий шаг
        await show_proforma(update, context)
        return

    # Проверка отмены оплаты
    elif query_param == "payment_cancelled":
        language_code = user_data.get_language()  # Получаем язык пользователя
        cancelled_message = payment_messages['payment_cancelled'].get(language_code,
                                                                      payment_messages['payment_cancelled']['en'])
        await update.message.reply_text(cancelled_message)
        # Возврат на предыдущий шаг
        return

    elif query_param == "expired_date":
        language_code = user_data.get_language()  # Получаем язык пользователя
        occupied_message_texts = {
            'en': "The selected date and time are already booked by another customer. Please choose another date — press /start.",
    'ru': "Выбранная дата и время уже оплачены другим заказчиком. Пожалуйста, выберите другую дату — нажмите /start.",
    'uk': "Вибрана дата і час вже оплачено іншим клієнтом. Будь ласка, виберіть іншу дату — натисніть /start.",
    'es': "La fecha y hora seleccionadas ya han sido reservadas por otro cliente. Por favor, elija otra fecha — presione /start.",
    'fr': "La date et l'heure sélectionnées ont déjà été réservées par un autre client. Veuillez choisir une autre date — appuyez sur /start.",
    'pl': "Wybrana data i godzina są już zarezerwowane przez innego klienta. Proszę wybrać inną datę — naciśnij /start.",
    'de': "Das ausgewählte Datum und die Uhrzeit sind bereits von einem anderen Kunden gebucht. Bitte wählen Sie ein anderes Datum — drücken Sie /start.",
    'it': "La data e l'orario selezionati sono già stati prenotati da un altro cliente. Si prega di scegliere un'altra data — premere /start."
            # Добавьте другие языки по необходимости
        }
        occupied_message = occupied_message_texts.get(language_code, occupied_message_texts['en'])

        # Сообщение о занятости времени и кнопка для выбора новой даты
        await context.bot.send_message(chat_id=user_data.get_user_id(), text=occupied_message)

        return

    else:
        user_data.set_user_id(user_id)
        user_data.set_username(username)

        user_data.set_step('start')
        user_data.set_language('en')  # Здесь можно задать язык или получить его от пользователя

        logging.info(f"Получен user_id: {user_id}, username: {username}, language: {user_data.get_language()}")

        logging.info("ЗАПИС КОРИСТУВАЧА")
        # await handle_name(update, context)
        check_client_is_exist(update, context)

        # Создаем новую запись в таблице orders с новым session_number
        conn = create_connection()
        if conn is not None:
            try:
                # Проверка текущего максимального session_number для user_id
                select_query = "SELECT MAX(session_number) FROM orders WHERE user_id = %s"
                cursor = conn.cursor()
                cursor.execute(select_query, (user_id,))

                # Получаем результат запроса
                result = cursor.fetchone()
                logging.info("(((((((((((((((((((((((((((((((((((((((((((((((")
                logging.info(result)

                # Проверка, что результат не None и session_number существует
                if result and result[0] is not None:
                    current_session = result[0]
                    new_session_number = current_session + 1
                else:
                    new_session_number = 1  # Если записей нет или session_number пустой

                user_data.set_session_number(new_session_number)

                # Принт для отслеживания в терминале
                print(f"Принт: Новый session_number для user_id {user_id} = {new_session_number}")

                # Создаем новую запись в таблице orders
                insert_query = """
                    INSERT INTO orders (user_id, session_number, selected_date, start_time, end_time, duration, people_count,
                    selected_style, city, preferences, calculated_cost, status)
                    VALUES (%s, %s, null, null, null, null, null, null, null, null, null, 1)
                """
                cursor.execute(insert_query, (user_id, new_session_number))
                conn.commit()

                logging.info(
                    f"Создана новая запись в таблице orders для user_id: {user_id} с session_number: {new_session_number}")

            except Exception as e:
                logging.error(f"Ошибка базы данных: {e}")
            finally:
                conn.close()
                logging.info("Соединение с базой данных закрыто")
        else:
            logging.error("Не удалось создать соединение с базой данных")

        # Отправляем ответ пользователю
        if update.message:
            await update.message.reply_text(
                f"Welcome {username}! Choose your language / Выберите язык / Elige tu idioma",
                reply_markup=language_selection_keyboard()
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                f"Welcome {username}! Choose your language / Выберите язык / Elige tu idioma",
                reply_markup=language_selection_keyboard()
            )
        logging.info("Функция start завершена")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Функция button_callback запущена")

    # Инициализация данных пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    query = update.callback_query
    await query.answer()
    # Обновляем запись только для последней сессии
    session_number_query = "SELECT MAX(session_number) FROM orders WHERE user_id = %s"
    conn = create_connection() #(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(session_number_query, (user_data.get_user_id(),))
    session_number = cursor.fetchone()[0]

    # Проверяем, что session_number не None и является числом
    if session_number is None:
        logging.error("Не удалось получить session_number. Возможно, записи в базе данных отсутствуют.")
    else:
        logging.info(f"Используем session_number: {session_number} для обновления.")
    logging.info("Функция ??????????????????????? запущена")
    logging.info(query.data)
    logging.info("Функция ??????????????????????? запущена")

    # Обработка выбора языка
    if query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)
        user_data.set_step('greeting')

        # Блокируем кнопки языков после выбора
        await query.edit_message_reply_markup(reply_markup=disable_language_buttons(query.message.reply_markup))

        # Обновляем язык в базе данных
        conn = create_connection()#(DATABASE_PATH)
        if conn is not None:
            try:
                update_query = "UPDATE orders SET language = %s WHERE user_id = %s AND session_number = %s"
                update_params = (language_code, update.callback_query.from_user.id, session_number)
                execute_query_with_retry(conn, update_query, update_params)
            except Exception as e:
                logging.error(f"Ошибка обновления языка в базе данных: {e}")
            finally:
                conn.close()

        # Отправляем сообщение с "ожиданием" на выбранном языке
        loading_texts = {
            'en': 'Loading...',
            'ru': 'Ожидай...',
            'es': 'Cargando...',
            'fr': 'Chargement...',
            'uk': 'Завантаження...',
            'pl': 'Ładowanie...',
            'de': 'Laden...',
            'it': 'Caricamento...'
        }
        loading_message = await query.message.reply_text(
            loading_texts.get(language_code, 'Loading...'),
        )

        # Выбор случайного видео
        video_path = random.choice(VIDEO_PATHS)

        # Загрузка видео и обновление сообщения
        if os.path.exists(video_path):
            # Отправляем видео как документ
            with open(video_path, 'rb') as video_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=video_file,
                    disable_notification=True
                )
                # Удаляем сообщение с "ожиданием"
                await loading_message.delete()
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Video file not found.")
            await loading_message.delete()


        # Тексты с гиперссылкой в зависимости от выбранного языка
        greeting_texts = {
            'en': 'Hello! What is your name?   [(Instruction,terms, booking conditions, and privacy policy)](https://telegra.ph/Privacy-Policy-09-19-96).',
            'ru': 'Привет! Как вас зовут?   [(Инструкция, термины, условия бронирования и политика конфиденциальности)](https://telegra.ph/Politika-konfidencialnosti-09-19-5).',
            'es': '¡Hola! ¿Cómo te llamas?  [(Instrucciones, términos y condiciones de reserva y política de privacidad)](https://telegra.ph/Pol%C3%ADtica-de-privacidad-09-19-8).',
            'fr': 'Salut! Quel est votre nom ?   [(Instructions, conditions générales de réservation et politique de confidentialité)](https://telegra.ph/Politique-de-confidentialit%C3%A9-09-19-3).',
            'uk': 'Привіт! Як вас звати?   [(Інструкція, терміни, умови бронювання і політика конфіденційності)](https://telegra.ph/Pol%D1%96tika-konf%D1%96denc%D1%96jnost%D1%96-09-19).',
            'pl': 'Cześć! Jak masz на імʼя?   [(umowy, warunki rezerwacji i polityka prywatności)](https://telegra.ph/Polityka-prywatno%C5%9Bci-09-19).',
            'de': 'Hallo! Wie heißt du?   [(Anleitung, allgemeine Geschäftsbedingungen und Datenschutzrichtlinie)](https://telegra.ph/Datenschutzrichtlinie-09-19).',
            'it': 'Ciao! Come ti chiami?   [(Istruzioni, termini, condizioni di prenotazione e informativa sulla privacy)](https://telegra.ph/Politica-sulla-privacy-09-19).'
        }

        # Отправляем сообщение с приветствием и ссылкой, отключая предварительный просмотр
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=greeting_texts.get(language_code,
                                    'Hello! What is your name? We respect and protect your [privacy](https://telegra.ph/Privacy-Policy-09-19-96).'),
            parse_mode='Markdown',
            disable_web_page_preview=True  # Отключаем предварительный просмотр
        )





    elif query.data == 'yes':
        if user_data.get_step() == 'name_received':
            # Обновляем имя введенное юзером в базе данных
            conn = create_connection()#(DATABASE_PATH)
            if conn is not None:
                try:
                    update_query = "UPDATE orders SET user_name = %s WHERE user_id = %s AND session_number = %s"
                    update_params = (user_data.get_name(), update.callback_query.from_user.id, session_number)
                    execute_query_with_retry(conn, update_query, update_params)
                except Exception as e:
                    logging.error(f"Ошибка обновления языка в базе данных: {e}")
                finally:
                    conn.close()

            user_data.set_step('calendar')
            await show_calendar(query, user_data.get_month_offset(), user_data.get_language())
        elif user_data.get_step() == 'date_confirmation':
            user_data.set_step('time_selection')
            await query.message.reply_text(
                time_selection_headers['start'].get(user_data.get_language(),
                                                    "Select start and end time (minimum duration 2 hours)"),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'start', user_data.get_selected_date())
            )

        elif user_data.get_step() == 'order_sent':
            user_data.set_step('order_confirmation')
            # await show_payment_page(update, context)

            user_status = get_user_status(user_data.get_user_id())
            if user_status != 1:

                # Переход на шаг оплаты (если это не админ, просто продолжаем сценарий)

                message_text,message_button = show_payment_page_handler(context)

                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text,
                                               reply_markup=message_button)
            else:

                # Получаем последний order_id из базы данных
                order_id = get_last_order_id(user_data.get_user_id())[0]

                if order_id is None:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Order ID not found",)

                update_order_status_to_paid(order_id)

                # Переход на следующий шаг
                await show_proforma(update, context)





        elif user_data.get_step() == 'time_confirmation':
            user_data.set_step('people_selection')
            await query.message.reply_text(
                people_selection_headers.get(user_data.get_language(), 'How many people are attending?'),
                reply_markup=generate_person_selection_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'people_confirmation':
            user_data.set_step('style_selection')
            await query.message.reply_text(
                party_styles_headers.get(user_data.get_language(), 'What style do you choose?'),
                reply_markup=generate_party_styles_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'style_confirmation':
            user_data.set_step('preferences_request')
            preferences_request_texts = {
                'en': 'Please write your preferences for table setting colors, food items (or exclusions), and desired table accessories (candles, glasses, etc.) - no more than 1000 characters.',
                'ru': 'Напишите свои предпочтения по цвету сервировки, продуктам (или исключениям), и желаемые аксессуары для стола (свечи, бокалы и прочее) - не более 1000 знаков.',
                'es': 'Escriba sus preferencias de colores para la mesa, artículos de comida (o exclusiones), y accesorios para la mesa (velas, copas, etc.) - no más de 1000 caracteres.',
                'fr': 'Veuillez écrire vos préférences pour les couleurs de la table, les aliments (ou exclusions), et les accessoires de table désirés (bougies, verres, etc.) - pas plus de 1000 caractères.',
                'uk': 'Напишіть свої уподобання щодо кольору сервірування, продуктів (або виключень), і бажані аксесуари для столу (свічки, келихи тощо) - не більше 1000 знаків.',
                'pl': 'Napisz swoje preferencje dotyczące kolorów nakrycia stołu, produktów spożywczych (lub wykluczeń), i pożądanych akcesoriów do stołu (świece, szklanki itp.) - nie więcej niż 1000 znaków.',
                'de': 'Bitte schreiben Sie Ihre Vorlieben für Tischfarben, Lebensmittel (oder Ausschlüsse), und gewünschte Tischaccessoires (Kerzen, Gläser usw.) - nicht mehr als 1000 Zeichen.',
                'it': 'Scrivi le tue preferenze per i colori della tavola, gli alimenti (o esclusioni), e gli accessori desiderati per la tavola (candele, bicchieri, ecc.) - non più di 1000 caratteri.'
            }
            await query.message.reply_text(
                preferences_request_texts.get(user_data.get_language(),
                                              "Please write your preferences for table setting colors, food items (or exclusions), and desired table accessories (candles, glasses, etc.) - no more than 1000 characters.")
            )

        # Disable the "no" button
        await query.edit_message_reply_markup(reply_markup=disable_yes_no_buttons(query.message.reply_markup))

    elif query.data == 'no':
        logging.info(f"Текущее состояние user_data.get_step(): {user_data.get_step()}")
        if user_data.get_step() == 'calendar':
            user_data.set_step('name_received')
            logging.info("Лог перед вызовом handle_name")  # Лог до вызова
            await handle_name(query, context)
            logging.info("Лог после вызова handle_name")  # Лог после вызова
        elif user_data.get_step() == 'date_confirmation':
            user_data.set_step('calendar')
            await show_calendar(query, user_data.get_month_offset(), user_data.get_language())
        elif user_data.get_step() == 'name_received':
            user_data.set_step('greeting')
            await start(update, context)
        elif user_data.get_step() == 'time_selection':
            print(user_data.get_selected_date())
            user_data.clear_time()
            await query.message.reply_text(
                time_selection_headers['start'].get(user_data.get_language(),
                                                    "Select start and end time (minimum duration 2 hours)"),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'start', user_data.get_selected_date())
            )
        elif user_data.get_step() == 'time_confirmation':
            user_data.clear_time()
            await query.message.reply_text(
                time_selection_headers['start'].get(user_data.get_language(),
                                                    "Select start and end time (minimum duration 2 hours)"),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'start',user_data.get_selected_date())
            )
        elif user_data.get_step() == 'people_selection':
            await query.message.reply_text(
                people_selection_headers.get(user_data.get_language(), 'How many people are attending?'),
                reply_markup=generate_person_selection_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'people_confirmation':
            user_data.set_step('people_selection')
            await query.message.reply_text(
                people_selection_headers.get(user_data.get_language(), 'How many people are attending?'),
                reply_markup=generate_person_selection_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'style_selection':
            await query.message.reply_text(
                party_styles_headers.get(user_data.get_language(), 'What style do you choose?'),
                reply_markup=generate_party_styles_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'style_confirmation':
            user_data.set_step('style_selection')
            await query.message.reply_text(
                party_styles_headers.get(user_data.get_language(), 'What style do you choose?'),
                reply_markup=generate_party_styles_keyboard(user_data.get_language())
            )
        elif user_data.get_step() == 'order_sent':
            user_data.set_step('start')
            await query.message.reply_text(
                f"Welcome {user_data.get_username()}! Choose your language / Выберите язык / Elige tu idioma",
                reply_markup=language_selection_keyboard()
            )

    elif query.data.startswith('date_'):
        selected_date = query.data.split('_')[1]
        print(f"Принт: Выбрана дата - {selected_date}")
        user_data.set_step('date_confirmation')
        user_data.set_date(selected_date)

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET selected_date = %s WHERE user_id = %s AND session_number = %s",
            (selected_date, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

        # Меняем цвет кнопки на красный и делаем все остальные кнопки неактивными
        await query.edit_message_reply_markup(
            reply_markup=disable_calendar_buttons(query.message.reply_markup, selected_date))

        confirmation_texts = {
            'en': f'You selected {selected_date}, correct?',
            'ru': f'Вы выбрали {selected_date}, правильно?',
            'es': f'Seleccionaste {selected_date}, ¿correcto?',
            'fr': f'Vous avez sélectionné {selected_date}, correct ?',
            'uk': f'Ви вибрали {selected_date}, правильно?',
            'pl': f'Wybrałeś {selected_date}, правильно?',
            'de': f'Sie haben {selected_date} gewählt, richtig?',
            'it': f'Hai selezionato {selected_date}, corretto?'
        }
        await query.message.reply_text(
            confirmation_texts.get(user_data.get_language(), f'You selected {selected_date}, correct?'),
            reply_markup=yes_no_keyboard(user_data.get_language())
        )

    elif query.data.startswith('time_'):
        selected_time = query.data.split('_')[1]
        logging.info("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
        logging.info(user_data.get_start_time())
        logging.info(query.data)
        if not user_data.get_start_time():
            user_data.set_start_time(selected_time)

            # Обновляем запись только для последней сессии
            update_order_data(
                "UPDATE orders SET start_time = %s WHERE user_id = %s AND session_number = %s",
                (selected_time, user_data.get_user_id(), session_number),

                user_data.get_user_id()
            )
            # time.sleep(1.5)  # Задержка перед повторной попыткой

            await query.message.reply_text(
                time_set_texts['start_time'].get(user_data.get_language(),
                                                 'Start time set to {}. Now select end time.').format(selected_time),
                reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'end',
                                                              user_data.get_selected_date(),user_data.get_start_time())
            )

        else:
            user_data.set_end_time(selected_time)

            # Обновляем запись только для последней сессии
            update_order_data(
                "UPDATE orders SET end_time = %s WHERE user_id = %s AND session_number = %s",
                (selected_time, user_data.get_user_id(), session_number),
                user_data.get_user_id()
            )

            # === ВСТАВЛЯЕМ БЛОК ДЛЯ РАСЧЕТА ПРОДОЛЖИТЕЛЬНОСТИ ===
            start_time = datetime.strptime(user_data.get_start_time(), '%H:%M')
            end_time = datetime.strptime(user_data.get_end_time(), '%H:%M')
            duration_minutes = (end_time - start_time).seconds // 60

            # Округление до ближайшего часа
            if duration_minutes % 60 != 0:
                duration_hours = (duration_minutes // 60) + 1
            else:
                duration_hours = duration_minutes // 60

            # Обновляем длительность в базе данных
            update_order_data(
                "UPDATE orders SET duration = %s WHERE user_id = %s AND session_number = %s",
                (duration_hours, user_data.get_user_id(), session_number),
                user_data.get_user_id()
            )

            if (end_time - start_time).seconds >= 7200:
                user_data.set_step('time_confirmation')
                await query.message.reply_text(
                    time_set_texts['end_time'].get(user_data.get_language(),
                                                   'End time set to {}. Confirm your selection.').format(selected_time),
                    reply_markup=yes_no_keyboard(user_data.get_language())
                )
            else:
                await query.message.reply_text(
                    f"Minimum duration is 2 hours. Please select an end time at least 2 hours after the start time.",
                    reply_markup=generate_time_selection_keyboard(user_data.get_language(), 'end',
                                                                  user_data.get_selected_date(), user_data.get_start_time())
                )
        await query.edit_message_reply_markup(
            reply_markup=disable_time_buttons(query.message.reply_markup, selected_time))

    elif query.data.startswith('person_'):
        selected_person = query.data.split('_')[1]
        user_data.set_step('people_confirmation')
        user_data.set_person_count(selected_person)

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET people_count = %s WHERE user_id = %s AND session_number = %s",
            (int(selected_person), user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )
        update_order_data(
            "UPDATE orders SET status = %s, updated_at = %s WHERE user_id = %s AND session_number = %s",
            (ORDER_STATUS["2-заполнено для расчета"], datetime.now(pytz.UTC), user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )
        # Рассчитываем стоимость
        duration = user_data.get_duration()
        people_count = int(user_data.get_person_count())

        # Рассчитываем стоимость с помощью функции calculate_total_cost (замените на свою функцию)
        total_cost = calculate_total_cost(duration, people_count)
        user_data.set_calculated_cost(total_cost)

        # Обновляем запись в базе данных
        update_order_data(
            "UPDATE orders SET calculated_cost = %s WHERE user_id = %s AND session_number = %s",
            (total_cost, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

        await query.edit_message_reply_markup(
            reply_markup=disable_person_buttons(query.message.reply_markup, selected_person))

        confirmation_texts = {
            'en': f'You selected {selected_person} people, correct?',
            'ru': f'Вы выбрали {selected_person} человек, правильно?',
            'es': f'Seleccionaste {selected_person} personas, ¿correctо?',
            'fr': f'Vous avez sélectionné {selected_person} personnes, correct ?',
            'uk': f'Ви вибрали {selected_person} людей, правильно?',
            'pl': f'Wybrałeś {selected_person} osób, правильно?',
            'de': f'Sie haben {selected_person} Personen gewählt, richtig?',
            'it': f'Hai selezionato {selected_person} persone, corretto?'
        }
        await query.message.reply_text(
            confirmation_texts.get(user_data.get_language(), f'You selected {selected_person} people, correct?'),
            reply_markup=yes_no_keyboard(user_data.get_language())
        )

    elif query.data.startswith('style_'):
        selected_style = query.data.split('_')[1]
        user_data.set_step('style_confirmation')
        user_data.set_style(selected_style)

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET selected_style = %s WHERE user_id = %s AND session_number = %s",
            (selected_style, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

        await query.edit_message_reply_markup(
            reply_markup=disable_style_buttons(query.message.reply_markup, selected_style))

        confirmation_texts = {
            'en': f'You selected {selected_style} style, correct?',
            'ru': f'Вы выбрали стиль {selected_style}, правильно?',
            'es': f'Seleccionaste el estilo {selected_style}, ¿correcto?',
            'fr': f'Vous avez sélectionné le style {selected_style}, correct ?',
            'uk': f'Ви вибрали стиль {selected_style}, правильно?',
            'pl': f'Wybrałeś styl {selected_style}, poprawne?',
            'de': f'Sie haben den Stil {selected_style} gewählt, richtig?',
            'it': f'Hai selezionato lo stile {selected_style}, corretto?'

        }
        await query.message.reply_text(
            confirmation_texts.get(user_data.get_language(), f'You selected {selected_style} style, correct?'),
            reply_markup=yes_no_keyboard(user_data.get_language())
        )

    # Добавляем обработку для города
    elif user_data.get_step() == 'city_request':
        user_data.set_city(query.data)

        # Обновляем запись только для последней сессии
        update_order_data(
            "UPDATE orders SET city = %s WHERE user_id = %s AND session_number = %s",
            (query.data, user_data.get_user_id(), session_number),
            user_data.get_user_id()
        )

    elif user_data.get_step() == 'order_sent':
        # await show_payment_page(update, context)

        message_text, message_button = show_payment_page_handler(context)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text,
                                       reply_markup=message_button)

        # await query.message.reply_text(show_payment_page_handler(context))
        # await asyncio.sleep(3)
        # await show_proforma(update, context)

    elif query.data.startswith('prev_month_') or query.data.startswith('next_month_'):
        month_offset = int(query.data.split('_')[2])
        user_data.set_month_offset(month_offset)

        logging.info(f"Календарная клавиатура сгенерирована для month_offset={month_offset}")

        await show_calendar(query, month_offset, user_data.get_language())

    logging.info("Функция button_callback завершена")

async def show_calendar(query, month_offset, language):
    logging.info(f"Функция show_calendar запущена с параметрами: month_offset={month_offset}, language={language}")

    # Ограничение значений month_offset
    if month_offset < -1:
        logging.info("month_offset был меньше -1, установлен в -1")
        month_offset = -1
    elif month_offset > 2:
        logging.info("month_offset был больше 2, установлен в 2")
        month_offset = 2

    # Генерация клавиатуры календаря
    calendar_keyboard = generate_calendar_keyboard(month_offset, language)
    logging.info(f"Календарная клавиатура сгенерирована для month_offset={month_offset}, language={language}")


    # Тексты для выбора даты на разных языках
    select_date_text = {
        'en': "Select a date:",
        'ru': "Выберите дату:",
        'es': "Seleccione una fecha:",
        'fr': "Sélectionnez une date:",
        'uk': "Виберіть дату:",
        'pl': "Wybierz datę:",
        'de': "Wählen Sie ein Datum:",
        'it': "Seleziona una data:"
    }

    # Отправка сообщения с клавиатурой календаря
    await query.message.reply_text(
        select_date_text.get(language, 'Select a date:'),
        reply_markup=calendar_keyboard
    )
    logging.info("Сообщение с клавиатурой календаря отправлено пользователю")

def disable_calendar_buttons(reply_markup, selected_date):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(selected_date):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_date.split('-')[2]}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_time_buttons(reply_markup, selected_time):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(selected_time):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_time}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_person_buttons(reply_markup, selected_person):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(f'person_{selected_person}'):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_person}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_style_buttons(reply_markup, selected_style):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(f'style_{selected_style}'):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_style}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

def disable_yes_no_buttons(reply_markup):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

if __name__ == '__main__':
    temp_data = TemporaryData()


    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        # Уведомление разработчика через Telegram
        if isinstance(update, Update):
            try:
                if update.message:
                    await update.message.reply_text("An error occurred. The administrator has been notified.")
                elif update.callback_query:
                    await update.callback_query.message.reply_text(
                        "An error occurred. The administrator has been notified.")
            except Exception as e:
                logger.error(f"Error notifying the user: {e}")


    def disable_language_buttons(reply_markup):
        new_keyboard = []
        for row in reply_markup.inline_keyboard:
            new_row = []
            for button in row:
                # Делаем кнопку неактивной, присваивая ей callback_data='none'
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
            new_keyboard.append(new_row)
        return InlineKeyboardMarkup(new_keyboard)



    logging.basicConfig(level=logging.DEBUG)

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_city_confirmation))

    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)

    application.run_polling()