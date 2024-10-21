import psycopg2  # Заменяем sqlite3 на psycopg2 для работы с PostgreSQL
import subprocess
import logging
from asyncio.log import logger
import telegram
from psycopg2 import OperationalError

from bot.admin_bot.helpers.calendar_helpers import generate_calendar_keyboard
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.admin_bot.helpers.database_helpers import get_full_proforma
from bot.admin_bot.keyboards.admin_keyboards import irina_service_menu, yes_no_keyboard
from bot.admin_bot.constants import UserData, ORDER_STATUS
from bot.admin_bot.helpers.calendar_helpers import disable_calendar_buttons
from bot.admin_bot.translations import translations, language_selection_keyboard
import os  # Для работы с переменными окружения
from dotenv import load_dotenv

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


async def admin_welcome_message(update: Update):
    # Приветственное сообщение для выбора языка
    message = await update.message.reply_text(
        "Привет, администратор! Я - твой АдминБот. Выбери язык / Choose your language:",
        reply_markup=language_selection_keyboard()
    )
    return message


# Функция для показа календаря и редактирования сообщения
async def show_calendar_to_admin(update, context, month_offset=0):
    query = update.callback_query

    # Генерация календаря с учетом смещения месяца
    calendar_markup = generate_calendar_keyboard(month_offset)

    try:
        # Редактируем текущее сообщение, а не отправляем новое
        logger.info(f"Попытка редактировать сообщение с новым календарем для месяца offset: {month_offset}")
        await query.edit_message_reply_markup(reply_markup=calendar_markup)
    except telegram.error.BadRequest as e:
        # Обработка ошибки, если сообщение уже было отредактировано
        if str(e) == "Message is not modified":
            logger.warning(f"Сообщение не изменилось. Ошибка: {str(e)}")
            pass
        else:
            logger.error(f"Произошла ошибка при редактировании сообщения: {str(e)}")
            raise

    # Обработка нажатий на календарь
    if query.data.startswith('prev_month_'):
        # Извлекаем смещение месяца для предыдущего месяца
        month_offset = int(query.data.split('_')[2])  # Извлекаем корректную часть callback_data
        await show_calendar_to_admin(update, context, month_offset)

    elif query.data.startswith('next_month_'):
         # Извлекаем смещение месяца для следующего месяца
         month_offset = int(query.data.split('_')[2])  # Извлекаем корректную часть callback_data
         await show_calendar_to_admin(update, context, month_offset)

    elif query.data == 'show_calendar':
         # Нажата кнопка "Показать календарь"
        await show_calendar_to_admin(update, context)


async def handle_delete_client_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает нажатие на кнопку 'Удалить клиента из базы данных'.
    """
    await show_calendar_to_admin(update, context)


async def handle_find_client_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает нажатие на кнопку 'Удалить клиента из базы данных'.
    """
    await show_calendar_to_admin(update, context)


async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    logger.info(f"ЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦЦ: {data}")
    if data.startswith('date_'):
        # Извлекаем выбранную дату
        selected_date = data.split('_')[1]
        logging.info(f"Selected date: {selected_date}")  # Логируем дату

        # Сохраняем выбранную дату в контексте
        context.user_data['selected_date'] = selected_date
        logging.info(f"Context date saved: {context.user_data['selected_date']}")  # Логируем сохраненную дату

        # Отключаем остальные кнопки и оставляем выбранную с красной точкой
        new_reply_markup = disable_calendar_buttons(query.message.reply_markup, selected_date)
        await query.edit_message_reply_markup(reply_markup=new_reply_markup)

        # Подтверждаем выбор даты
        message = await query.message.reply_text(f"Вы выбрали дату {selected_date}, правильно?", reply_markup=yes_no_keyboard('ru'))

        context.user_data['delete_messages'].append(message.message_id)

    elif query.data == "yes":
        selected_date = context.user_data.get("selected_date")
        logging.info(f"User confirmed date: {selected_date}")  # Логируем подтвержденную дату

        if selected_date:
            # Получаем user_id
            user_id = update.effective_user.id
            logging.info(f"User ID: {user_id}, Selected Date: {selected_date}")  # Логируем user_id и дату

            # Генерируем кнопки для проформ по выбранной дате
            selected_date = context.user_data.get("selected_date")
            proforma_keyboard = await generate_proforma_buttons_by_date(selected_date)
            message = await query.message.reply_text(f"Проформы для даты {selected_date}:", reply_markup=proforma_keyboard)
            context.user_data['delete_messages'].append(message.message_id)

            # Обновляем статус клиента с 2 на 3
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET status = 3 WHERE user_id = %s AND status = 2", (user_id,))
                conn.commit()
                cursor.close()
                conn.close()

                # Уведомляем админа об успешном внесении клиента
                await query.message.reply_text("Вы удачно внесли нового клиента!")
            except Exception as e:
                logging.error(f"Ошибка обновления статуса клиента: {e}")
                await query.message.reply_text(f"Произошла ошибка при обновлении статуса клиента: {e}")

        else:
            await query.message.reply_text("Ошибка: выбранная дата не найдена.")



def generate_proforma_buttons(proforma_list):
    keyboard = []
    for proforma in proforma_list:
        # Формируем полный номер проформы: user_id, session_number, status
        full_proforma_number = f"{proforma['user_id']}_{proforma['session_number']}_{proforma['status']}"
        keyboard.append(
            [InlineKeyboardButton(full_proforma_number, callback_data=f"proforma_{proforma['session_number']}")])

    return InlineKeyboardMarkup(keyboard)


async def generate_proforma_buttons_by_date(selected_date):
    logging.info(f"{selected_date}, {type(selected_date)}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # Пример запроса в базу данных
    conn = get_db_connection()  # Используем подключение к PostgreSQL
    cursor = conn.cursor()

    try:
        # Предполагается, что вам нужно получить проформы по дате
        cursor.execute("""
            SELECT user_id, session_number, status
            FROM orders
            WHERE selected_date = %s AND status >= 3
        """, (selected_date,))

        proforma_list = cursor.fetchall()

        if not proforma_list:
            return None  # Если проформы не найдены

        # Генерация кнопок для проформ
        buttons = []
        for proforma in proforma_list:
            proforma_number = f"{proforma[0]}_{proforma[1]}_{proforma[2]}"

            # Выводим callback_data в консоль для проверки
            print(f"Callback data для кнопки: {proforma_number}")

            buttons.append([InlineKeyboardButton(proforma_number, callback_data=f"{proforma[0]}_{proforma[1]}_{proforma[2]}")])

        return InlineKeyboardMarkup(buttons)

    finally:
        cursor.close()
        conn.close()


async def handle_proforma_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())

    query = update.callback_query
    proforma_data = query.data.split('_')

    # Проверяем, что данные проформы корректны
    if len(proforma_data) == 3:
        user_id = proforma_data[0]
        session_number = proforma_data[1]
        status = proforma_data[2]

        # Логируем для отладки
        print(f"user_id: {user_id}, session_number: {session_number}, status: {status}")

        # Попробуем получить информацию о проформе
        try:
            proforma_info = get_full_proforma(user_id, session_number)
            if proforma_info:
                # Формируем текст сообщения для отправки админу
                full_proforma_text = (
                    f"Полная информация по проформе:\n\n"
                    f"User ID: {proforma_info[0]}\n"
                    f"Session Number: {proforma_info[1]}\n"
                    f"Дата события: {proforma_info[2]}\n"
                    f"Время: {proforma_info[3]} - {proforma_info[4]}\n"
                    f"Количество участников: {proforma_info[5]}\n"
                    f"Стиль мероприятия: {proforma_info[6]}\n"
                    f"Город: {proforma_info[7]}\n"
                    f"Стоимость: {proforma_info[8]} евро\n"
                    f"Статус: {proforma_info[10]}"
                )
                message = await query.message.reply_text(full_proforma_text)
                context.user_data['delete_messages'].append(message.message_id)

                #logging.info(f"Updating order status for order_id: {ORDER_STATUS['6-Администратор зашел в АдминБот и просмотрел новую ПРОФОРМУ']}YYYYYYYYYYYYYYYYYYYYYYY")

                # Обновляем статус ордера
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE user_id = %s AND session_number = %s",
                    (ORDER_STATUS['6-Администратор зашел в АдминБот и просмотрел новую ПРОФОРМУ'], user_id, session_number)
                )
                conn.commit()

                if user_data.get_step() == "delete_client":
                    user_data.set_step(f"delete_client_{proforma_info[11]}")
                    message = await query.message.reply_text(f"удалить эту запись?",
                                                   reply_markup=yes_no_keyboard('ru'))
                    context.user_data['delete_messages'].append(message.message_id)

                #     формируем кнопки
            else:
                message = await query.message.reply_text("Проформа не найдена.")
                context.user_data['delete_messages'].append(message.message_id)

        except Exception as e:
            message = await query.message.reply_text(f"Произошла ошибка при получении проформы: {str(e)}")
            context.user_data['delete_messages'].append(message.message_id)


def null_status(order_id):
    # Создаем подключение к базе данных
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Обновляем статус ордера
        logging.info(f"Updating order status for order_id: {order_id}")
        cursor.execute("UPDATE orders SET status = 0 WHERE order_id = %s",
                       (order_id,))
        conn.commit()

        logging.info(f"Order status updated for order_id: {order_id}")


    except Exception as e:
        logging.error(f"Failed to send order info to admin bot: {e}")
        print(f"Принт: Ошибка при отправке сообщения: {e}")

    finally:
        cursor.close()
        conn.close()
        logging.info(f"Database connection closed for order_id: {order_id}")
