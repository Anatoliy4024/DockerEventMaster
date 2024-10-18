# service_scenario.py

from telegram import Update
from telegram.ext import ContextTypes

from bot.admin_bot.keyboards.admin_keyboards import service_menu_keyboard, user_statistics_menu


async def service_welcome_message(update: Update):
    # Приветственное сообщение для Службы сервиса
    message = await update.message.reply_text(
        "Привет! Твоему id - соответствует Службе сервиса.\n"
        "Предоставляю доступ к технической информации"
    )
    # Отображаем меню с кнопками для Службы сервиса
    options_message = await update.message.reply_text(
        "Выбери действие:",
        reply_markup=service_menu_keyboard()
    )
    return message, options_message

# Обработчик кнопки "Статистика пользователей"
async def handle_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Отображаем подменю для статистики пользователей
    await query.edit_message_text(
        text="Выберите интересующую статистику:",
        reply_markup=user_statistics_menu()
    )

# Обработчик возврата в основное меню
async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Возвращаем основное меню сервиса
    await query.edit_message_text(
        text="Выбери действие:",
        reply_markup=service_menu_keyboard()
    )
