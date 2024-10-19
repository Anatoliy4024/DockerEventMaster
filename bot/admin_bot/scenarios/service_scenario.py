# service_scenario.py

from telegram import Update
from telegram.ext import ContextTypes

from bot.admin_bot.keyboards.admin_keyboards import service_menu_keyboard, user_statistics_menu


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


async def show_statistics_menu(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Переход на подменю статистики
    options_message = await query.message.reply_text(
        "Выберите интересующую статистику:",
        reply_markup=user_statistics_menu()
    )

    # Сохраняем ID нового сообщения
    context.user_data['delete_messages'].append(options_message.message_id)

# Обработчик для кнопки "Вернуться в основное меню"
async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Возвращаемся к главному меню сервиса
    await query.edit_message_text(
        text="Выбери действие:",
        reply_markup=service_menu_keyboard()
    )