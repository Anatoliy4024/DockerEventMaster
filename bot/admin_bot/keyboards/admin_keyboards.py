## keybords.py

import logging
import os
import urllib.parse
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.admin_bot.helpers.database_helpers import get_full_proforma, get_latest_session_number

from bot.admin_bot.translations import translations, button_texts
from dotenv import load_dotenv
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN_PICNIC')  # Получаем токен из .env файла



def irina_service_menu():
    keyboard = [
        [InlineKeyboardButton("Найти и смотреть ПРОФОРМУ", callback_data='find_and_view_order')],
        [InlineKeyboardButton("Внести клиента в базу данных", url='https://t.me/PicnicsAlicanteBot?start=start')],
        [InlineKeyboardButton("Удалить клиента из базы данных", callback_data='delete_client')]
    ]
    return InlineKeyboardMarkup(keyboard)

def service_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Статистика пользователей", callback_data='user_stats')],
        [InlineKeyboardButton("Статистика сервера", callback_data='system_stats')]
    ]
    return InlineKeyboardMarkup(keyboard)

def user_options_keyboard(language, user_id):
    # Стандартное сообщение на языке пользователя
    trans = translations.get(language, translations['en'])  # Используем 'en' как язык по умолчанию
    contact_message = trans['whatsapp_message']

    try:
        # Получаем последний session_number для пользователя
        session_number = get_latest_session_number(user_id)

        if session_number:
            # Получаем полную информацию о проформе
            order_info = get_full_proforma(user_id, session_number)

            if order_info and len(order_info) >= 3:  # Убедитесь, что данные извлечены корректно
                # Формируем номер проформы и добавляем статус
                proforma_number = f"{order_info[0]}_{order_info[1]}_{order_info[10]}"
                contact_message = f"{trans['whatsapp_message']} {proforma_number}. {trans['whatsapp_footer']}"
    except Exception as e:
        logging.error(f"Ошибка при получении номера проформы: {e}")
        # Оставляем contact_message по умолчанию

    # Кодируем сообщение для использования в URL
    encoded_message = urllib.parse.quote(contact_message)

    # Создаем клавиатуру с тремя кнопками
    keyboard = [
        [InlineKeyboardButton(button_texts[language][0], callback_data='get_proforma')],
        [InlineKeyboardButton(button_texts[language][1], url=f'https://wa.me/34667574895?text={encoded_message}')],
        [InlineKeyboardButton(button_texts[language][2], url='https://www.instagram.com/picnicsalicante')]
    ]

    return InlineKeyboardMarkup(keyboard)

def yes_no_keyboard(language):
    texts = {
        'en': {'yes': 'Yes', 'no': 'No'},
        'ru': {'yes': 'Да', 'no': 'Нет'},
        'es': {'yes': 'Sí', 'no': 'No'},
        'fr': {'yes': 'Oui', 'no': 'Non'},
        'uk': {'yes': 'Так', 'no': 'Ні'},
        'pl': {'yes': 'Tak', 'no': 'Nie'},
        'de': {'yes': 'Ja', 'no': 'Nein'},
        'it': {'yes': 'Sì', 'no': 'No'}
    }

    # Создаем клавиатуру с двумя кнопками "Да" и "Нет"
    keyboard = [
        [
            InlineKeyboardButton(texts[language]['yes'], callback_data='yes'),
            InlineKeyboardButton(texts[language]['no'], callback_data='no')
        ]
    ]

    # Возвращаем клавиатуру
    return InlineKeyboardMarkup(keyboard)