# service_scenario.py

from telegram import Update
from telegram.ext import ContextTypes

from bot.admin_bot.helpers.database_helpers import get_user_statistics
from bot.admin_bot.keyboards.admin_keyboards import service_menu_keyboard


async def service_welcome_message(update: Update, context):
    # Приветственное сообщение для Службы сервиса
    user = update.message.from_user
    user_id = user.id  # Получаем user_id пользователя

    # Приветственное сообщение
    message = await update.message.reply_text(
        f"Привет! Твой id - {user_id} соответствует Службе сервиса.\n"
        "Предоставляю доступ к технической информации"
    )

    # Отображаем меню с кнопками для Службы сервиса
    options_message = await update.message.reply_text(
        "Выбери действие:",
        reply_markup=service_menu_keyboard()  # Показываем главное меню сервиса
    )

    # Сохраняем ID сообщения с кнопками
    context.user_data['delete_messages'] = [options_message.message_id]
    return message, options_message

async def handle_service_menu_callback(update, context):
    query = update.callback_query
    if query.data == 'user_stats':
        stats = get_user_statistics()  # вызов функции для получения статистики
        message = (
            f"Пользователи с незаконченным заказом: {stats['pending_orders']}\n"
            f"Пользователи с неоплаченными заказами: {stats['unpaid_orders']}\n"
            f"Пользователи с оплаченным резервом: {stats['paid_reservations']}\n"
            f"Повторные действия пользователей: {stats['repeat_actions']}"
        )
        await query.message.edit_text(message)
