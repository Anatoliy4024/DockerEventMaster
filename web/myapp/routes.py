import os
import sys
from datetime import timedelta, datetime
import logging

from dotenv import load_dotenv
from flask import Blueprint, request, render_template, flash, redirect, jsonify, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from web.myapp.email_utils import send_email
from web.utils.db import create_connection  # Подключаем базу данных
from web.myapp.translations import translations, field_labels  # Импортируем оба словаря

import stripe

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from bot.picnic_bot.data_reserve import get_reserved_times_for_date, check_time_reserved
from bot.picnic_bot.status_3 import update_order_status_to_paid, get_last_order_id  # Подключаем функцию обновления статуса

from datetime import datetime



# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Настройка Stripe с использованием ключей из переменных окружения
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
success_url = os.getenv('SUCCESS_URL')
cancel_url = os.getenv('CANCEL_URL')




main = Blueprint('main', __name__)

# Новый корневой маршрут для непосредственного создания платежной сессии
@main.route('/create-payment', methods=['GET','POST'])
def create_payment():
    try:
        user_id = request.args.get("c")
        if not user_id:
            return jsonify(error="no user_id"), 400

        # Получаем последний order_id из базы данных
        order = get_last_order_id(int(user_id))

        if order is None:
            return jsonify({"error": "Order ID not found"}), 400

        selected_date = order[1]
        start_time = order[2]
        end_time = order[3]

        # Проверка доступности времени перед оплатой
        reserved_intervals = get_reserved_times_for_date(selected_date)

        start = timedelta(hours=start_time.hour, minutes=start_time.minute)
        end = timedelta(hours=end_time.hour, minutes=end_time.minute)

        while start < end:
            hours = int(start.total_seconds() // 3600)
            minutes = int((start.total_seconds() % 3600) // 60)
            start_time_str = (f"{hours:02d}:{minutes:02d}")

            if check_time_reserved(start_time_str, reserved_intervals):
                return redirect('https://t.me/PicnicsAlicanteBot?start=expired_date')

            start += timedelta(minutes=30)

        # Создаем платежную сессию Stripe с передачей order_id в метаданных
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Оплата заказа',
                    },
                    'unit_amount': 2000,  # 20 евро
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'order_id': order[0],
                'user_id': user_id  # Передаем user_id в метаданных для связи
            }
        )
        # Перенаправляем пользователя на страницу оплаты Stripe
        return redirect(session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

@main.route('/payment-success')
def payment_success():
    # Возвращаемся в бота после успешной оплаты
    return redirect('https://t.me/PicnicsAlicanteBot?start=payment_success')

# Маршрут для обработки отмены платежа
@main.route('/payment-cancelled')
def payment_cancelled():
    # Возвращаемся в бота после отмены платежа
    return redirect('https://t.me/PicnicsAlicanteBot?start=payment_cancelled')

# Вебхук для обработки уведомлений от Stripe
@main.route('/webhook', methods=['POST','GET'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': str(e)}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Извлекаем order_id и user_id из метаданных
        order_id = session['metadata']['order_id']
        user_id = session['metadata']['user_id']
        customer_email = session['customer_details']['email']  # Получаем email пользователя

        # Обновляем статус заказа и email пользователя в базе данных
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Обновляем статус заказа на "оплачено"
            update_order_status_to_paid(order_id)

            # Обновляем email в таблице users
            cursor.execute("""
                UPDATE users
                SET email = %s, updated_at = NOW()
                WHERE user_id = %s
            """, (customer_email, user_id))

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка базы данных: {e}")
            return jsonify({'error': 'Не удалось обновить базу данных'}), 500

    return jsonify({'status': 'success'}), 200

@main.route('/ver1.0/')
def index():
 """Главная страница с выбором языка и флагами."""
 lang = request.args.get('lang', 'en')
 return render_template('index.html', translations=translations[lang], labels=field_labels[lang], lang=lang)

@main.route('/ver1.0/select_language')
def select_language():
    """Маршрут для выбора языка с отображением сообщения."""
    lang = request.args.get('lang', 'en')
    message = translations[lang]['language_selected']
    current_time = int(datetime.now().timestamp())  # Получаем текущую временную метку
    return render_template(
        'index.html',
        message=message,
        translations=translations[lang],
        labels=field_labels[lang],
        lang=lang,
        time=current_time
    )
@main.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя через email и пароль."""
    lang = request.args.get('lang', 'en')  # Получаем выбранный язык или устанавливаем 'en' по умолчанию

    # Проверка, что lang есть в translations и field_labels
    if lang not in translations or lang not in field_labels:
        flash(f"Invalid language selected: {lang}", "danger")
        return redirect(url_for('main.index', lang='en'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        lang = request.args.get('lang', 'en')  # Получаем выбранный язык

        conn = create_connection()
        cursor = conn.cursor()
        try:
            # Проверяем, есть ли уже такой email в базе данных
            cursor.execute("SELECT user_id, registration_passw FROM users WHERE registration_email = %s", (email,))
            user = cursor.fetchone()

            if user:
                user_id, hashed_password = user
                # Проверяем правильность пароля
                if check_password_hash(hashed_password, password):
                    # Обновляем номер сессии для существующего пользователя
                    cursor.execute("SELECT MAX(session_number) FROM orders WHERE user_id = %s", (user_id,))
                    result = cursor.fetchone()

                    if result and result[0] is not None:
                        current_session = result[0]
                        new_session_number = current_session + 1
                    else:
                        new_session_number = 1

                    # Создаем новую запись в таблице orders
                    cursor.execute("""
                        INSERT INTO orders (user_id, session_number, language, status, selected_date, start_time, end_time,
                                            duration, people_count, selected_style, city, preferences, calculated_cost, 
                                            created_at, updated_at)
                        VALUES (%s, %s, %s, %s, null, null, null, null, null, null, null, null, null, NOW(), NOW())
                    """, (user_id, new_session_number, lang, 1))  # status = 1 (pending)

                    conn.commit()
                    flash(translations[lang]['login_successful'], 'success')  # Используем перевод для сообщения
                    return redirect(url_for('main.booking_page', lang=lang))

                else:
                    # Неверный пароль
                    flash(translations[lang]['incorrect_password'], 'danger')  # Используем перевод для сообщения
                    return redirect(url_for('main.index', lang=lang))

            # Если пользователя нет, создаем нового
            hashed_password = generate_password_hash(password)

            # Добавляем нового пользователя в таблицу users
            cursor.execute(
                "INSERT INTO users (registration_email, registration_passw) VALUES (%s, %s) RETURNING user_id",
                (email, hashed_password)
            )
            user_id = cursor.fetchone()[0]  # Получаем ID нового пользователя

            # Для нового пользователя устанавливаем session_number = 1
            new_session_number = 1

            # Создаем новую запись в таблице orders
            cursor.execute("""
                INSERT INTO orders (user_id, session_number, language, status, selected_date, start_time, end_time,
                                    duration, people_count, selected_style, city, preferences, calculated_cost, 
                                    created_at, updated_at)
                VALUES (%s, %s, %s, %s, null, null, null, null, null, null, null, null, null, NOW(), NOW())
            """, (user_id, new_session_number, lang, 1))  # status = 1 (pending)

            conn.commit()
            flash(translations[lang]['registration_successful'], 'success')
            return redirect(url_for('main.index', lang=lang))

        except Exception as e:
            conn.rollback()  # Отмена транзакции при ошибке
            flash(f"{translations[lang]['database_error']} ({e})", 'danger')  # Перевод + текст ошибки
            return redirect(url_for('main.index', lang=lang, translations=translations[lang]))


        finally:
            cursor.close()
            conn.close()

    return render_template('register.html', lang=lang, translations=translations[lang], labels=field_labels[lang])


# @main.route('/ver1.0/booking_page')
# def booking_page():
#     """Страница для бронирования."""
#     lang = request.args.get('lang', 'en')
#     return render_template('booking.html', lang=lang)

@main.route('/ver1.0/booking_page', methods=['GET'])
def booking_page():
    lang = request.args.get('lang', 'en')  # Получаем выбранный язык или устанавливаем 'en' по умолчанию

    # Проверка, что lang есть в translations и field_labels
    if lang not in translations or lang not in field_labels:
        flash(f"Invalid language selected: {lang}", "danger")
        return redirect(url_for('main.index', lang='en'))

    return render_template(
        'booking.html',
        lang=lang,
        translations=translations[lang]  # Передаем переводы для выбранного языка
    )

@main.route('/ver1.0/error_page')
def error_page():
    """Страница ошибки с неверным паролем."""
    lang = request.args.get('lang', 'en')
    return render_template('error.html', lang=lang, message=translations[lang]['incorrect_password'])
