
import asyncio
import os
import psycopg2  # Используем psycopg2 вместо sqlite3 для PostgreSQL
import logging
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.admin_bot.constants import UserData, ORDER_STATUS
from bot.admin_bot.scenarios.user_scenario import send_proforma_to_user, get_full_proforma
from bot.admin_bot.helpers.database_helpers import get_latest_session_number
from bot.admin_bot.keyboards.admin_keyboards import user_options_keyboard, irina_service_menu, service_menu_keyboard
from bot.admin_bot.scenarios.user_scenario import user_welcome_message
from bot.admin_bot.scenarios.admin_scenario import admin_welcome_message, handle_find_client_callback, \
    show_calendar_to_admin, handle_date_selection, generate_proforma_buttons_by_date, handle_proforma_button_click, \
    handle_find_client_callback, null_status, handle_delete_client_callback
from bot.admin_bot.scenarios.service_scenario import service_welcome_message
from bot.admin_bot.translations import language_selection_keyboard
from bot.admin_bot.database_logger import log_message, log_query
from psycopg2 import OperationalError
from dotenv import load_dotenv

ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN_ADMIN')

# Включаем логирование и указываем файл для логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Установите уровень на DEBUG для детальной информации
    filename='db_operations.log',  # Укажите имя файла для логов
    filemode='w'  # 'w' - перезаписывать файл при каждом запуске, 'a' - добавлять к существующему файлу
)

logger = logging.getLogger(__name__)


# Загружаем переменные окружения из .env файла
load_dotenv()

def get_db_connection():
    try:
        # Подключаемся к базе данных, используя переменные окружения
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'mydatabase'),
            user=os.getenv('DB_USER', 'myuser'),
            password=os.getenv('DB_PASSWORD', 'mypassword')
        )
    except OperationalError as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


def get_user_info_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM users WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info

# Функция для получения по user_id в таблице users - статуса: админ - status = 1, сервисная служба - status = 2
def get_user_status(user_id):
    try:
        # Подключаемся к базе данных PostgreSQL
        conn = get_db_connection()
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


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id  # Получаем user_id пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data["delete_messages"] = list()
    context.user_data['user_data'] = user_data

    # Инициализация переменной message по умолчанию
    message = None

    # Получаем статус пользователя из базы данных
    status = get_user_status(user_id)

    if status is None:
        # Если пользователь не найден в базе данных
        await update.message.reply_text("Вы не зарегистрированы в системе.")
        return

    # Проверка статуса пользователя
    if status == 1:
        # Пользователь является админом
        message = await admin_welcome_message(update)
    elif status == 2:
        # Пользователь является сервисным сотрудником
        message = await service_welcome_message(update)
    else:
        # Обычный пользователь
        message = await user_welcome_message(update, user.first_name)

    # Сохраняем ID сообщения с кнопками
    if message:
        context.user_data['language_message_id'] = message.message_id


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'inactive_button':
        # Эта кнопка неактивна, ничего не делаем
        return

    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    status = get_user_status(update.effective_user.id)

    if status is None:
        # Если пользователь не найден в базе данных
        await update.message.reply_text("Вы не зарегистрированы в системе.")
        return

    # Обработка нажатий на календарь
    if query.data.startswith('prev_month_'):
        month_offset = int(query.data.split('_')[2])  # Извлекаем смещение месяца
        await show_calendar_to_admin(update, context, month_offset)

    elif query.data.startswith('next_month_'):
        month_offset = int(query.data.split('_')[2])  # Извлекаем смещение месяца
        await show_calendar_to_admin(update, context, month_offset)

    elif query.data == 'show_calendar':
        await show_calendar_to_admin(update, context)

    elif query.data == 'find_and_view_order':
        user_data.set_step('find_and_view_order')
        await handle_find_client_callback(update, context)

    elif query.data == 'delete_client':
        user_data.set_step('delete_client')
        await handle_delete_client_callback(update, context)

    elif query.data == "yes":
        selected_date = context.user_data.get("selected_date")
        if user_data.get_step().startswith("delete_client_"):
            order_id = user_data.get_step().split("_")[-1]
            null_status(order_id)

            # Удаляем предыдущие сообщения с опциями и проформой
            del_message_id = context.user_data.get("delete_messages")
            if del_message_id:

                for i in del_message_id:
                    try:
                        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=i)
                    except Exception as e:
                        logger.error(f"Error deleting options message: {e}")

            # Если это администратор, переключаем на админ-меню
            if status == 1:
                options_message = await query.message.reply_text(
                    "Выбери действие:",
                    reply_markup=irina_service_menu()
                )
                context.user_data['delete_messages'].append(options_message.message_id)
            else:
                # Для других пользователей остается логика стандартного меню юзера
                headers = {
                    'en': "Choose",
                    'ru': "Выбери",
                    'es': "Elige",
                    'fr': "Choisissez",
                    'uk': "Виберіть",
                    'pl': "Wybierz",
                    'de': "Wählen",
                    'it': "Scegli"
                }

                new_options_message = await query.message.reply_text(
                    headers.get(user_data.get_language(), "Choose"),
                    reply_markup=user_options_keyboard(user_data.get_language(), update.effective_user.id)
                )

                context.user_data['delete_messages'].append(new_options_message.message_id)

        elif selected_date:
            proforma_keyboard = await generate_proforma_buttons_by_date(selected_date)
            message = await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"Проформы для даты {selected_date}:",
                reply_markup=proforma_keyboard
            )
            context.user_data['delete_messages'].append(message.message_id)

        else:
            message = await query.message.reply_text("Ошибка: выбранная дата не найдена.")
            context.user_data['delete_messages'].append(message.message_id)
    elif query.data == "no":
        # Удаляем предыдущие сообщения с календарем и подтверждением даты
        del_message_id = context.user_data.get("delete_messages")
        if del_message_id:
            for i in del_message_id:
                try:
                    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=i)
                except Exception as e:
                    logger.error(f"Error deleting message: {e}")

        # Если это администратор, переключаем на админ-меню
        if status == 1:
            options_message = await query.message.reply_text(
                "Выбери действие:",
                reply_markup=irina_service_menu()
            )
            context.user_data['delete_messages'] = [options_message.message_id]  # Сохраняем ID сообщения

        else:
            # Логика для других пользователей
            headers = {
                'en': "Choose",
                'ru': "Выбери",
                'es': "Elige",
                'fr': "Choisissez",
                'uk': "Виберіть",
                'pl': "Wybierz",
                'de': "Wählen",
                'it': "Scegli"
            }

            new_options_message = await query.message.reply_text(
                headers.get(user_data.get_language(), "Choose"),
                reply_markup=user_options_keyboard(user_data.get_language(), update.effective_user.id)
            )
            context.user_data['delete_messages'] = [new_options_message.message_id]

        # Возвращение в главное меню администратора
        await admin_welcome_message(update)

    # Обработка нажатий на кнопки смены языка
    elif query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)

        # Удаляем предыдущие сообщения с опциями и проформой
        del_message_id = context.user_data.get("delete_messages")
        if del_message_id:

            for i in del_message_id:
                try:
                    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=i)
                except Exception as e:
                    logger.error(f"Error deleting options message: {e}")

        # Если это администратор, переключаем на админ-меню
        if status == 1:
            options_message = await query.message.reply_text(
                "Выбери действие:",
                reply_markup=irina_service_menu()
            )
            context.user_data['delete_messages'].append(options_message.message_id)
        else:
            # Для других пользователей остается логика стандартного меню юзера
            headers = {
                'en': "Choose",
                'ru': "Выбери",
                'es': "Elige",
                'fr': "Choisissez",
                'uk': "Виберіть",
                'pl': "Wybierz",
                'de': "Wählen",
                'it': "Scegli"
            }

            new_options_message = await query.message.reply_text(
                headers.get(language_code, "Choose"),
                reply_markup=user_options_keyboard(language_code, update.effective_user.id)
            )

            context.user_data['delete_messages'].append(new_options_message.message_id)

    # Обработка кнопки для получения проформы
    elif query.data == 'get_proforma':
        try:
            # Получаем user_id пользователя
            user_id = update.effective_user.id
            # Получаем последний session_number для пользователя
            session_number = get_latest_session_number(user_id)
            if session_number:
                # Получаем полную информацию о проформе
                proforma_info = get_full_proforma(user_id, session_number)

                if proforma_info:
                    # Отправляем проформу пользователю
                    proforma_message = await send_proforma_to_user(user_id, session_number, user_data)
                    # Сохраняем ID сообщения с проформой
                    context.user_data['proforma_message_id'] = proforma_message.message_id
                else:
                    await query.message.reply_text(f"Не удалось получить данные проформы для session_number: {session_number}")
            else:
                await query.message.reply_text(f"Не удалось найти session_number для user_id: {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при получении информации о пользователе: {str(e)}")
            await query.message.reply_text("Произошла ошибка при попытке получить информацию о пользователе.")


# Основной блок для запуска бота
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(handle_date_selection, pattern=r'^date_\d{4}-\d{2}-\d{2}$'))
    # Обработчик для кнопок проформы
    application.add_handler(CallbackQueryHandler(handle_proforma_button_click, pattern=r'^\d+_\d+_\d+$'))

    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()
