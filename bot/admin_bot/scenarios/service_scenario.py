# service_scenario.py

from telegram import Update
from bot.admin_bot.keyboards.admin_keyboards import service_menu_keyboard
async def service_welcome_message(update: Update):
    # Приветственное сообщение для Службы сервиса
    message = await update.message.reply_text(
        "Привет! Твой id - ........ соответствует Службе сервиса.\n"
        "Предоставляю доступ к технической информации"
    )
    # Отображаем меню с кнопками для Службы сервиса
    options_message = await update.message.reply_text(
        "Выбери действие:",
        reply_markup=service_menu_keyboard()
    )
    return message, options_message
