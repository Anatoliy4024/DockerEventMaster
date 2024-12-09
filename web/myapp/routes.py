import os
import sys
import urllib.parse
from datetime import timedelta, datetime
import logging

from dotenv import load_dotenv
from flask import Blueprint, request, render_template, flash, redirect, jsonify, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from web.myapp.email_utils import send_email
from web.myapp.forms import RegistrationForm
from web.utils.calculations import get_duration, calculate_total_cost
from web.utils.db import create_connection, insert_order, get_order_info  # Подключаем базу данных
from web.myapp.translations import translations, field_labels, ORDER_STATUS, \
    order_field_labels  # Импортируем оба словаря
from bot.admin_bot.translations import translations as bot_translations
import stripe

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from bot.picnic_bot.data_reserve import get_reserved_times_for_date, check_time_reserved
from bot.picnic_bot.status_3 import update_order_status_to_paid, get_last_order_id  # Подключаем функцию обновления статуса

from datetime import datetime



# Загрузка переменных окружения
load_dotenv()

# Настройка Stripe с использованием ключей из переменных окружения
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
success_url = os.getenv('SUCCESS_URL')
cancel_url = os.getenv('CANCEL_URL')

WA_URL = os.getenv('WA_URL')  # Получаем ссылку из .env файла
INSTAGRAM_URL = os.getenv('INSTAGRAM_URL')  # Получаем ссылку из .env файла


main = Blueprint('main', __name__)

# Новый корневой маршрут для непосредственного создания платежной сессии
@main.route('/create-payment', methods=['GET','POST'])
def create_payment():
    try:
        user_id = request.args.get("c")
        if not user_id:
            return jsonify(error="no user_id"), 400

        order_type = request.args.get("type", 1)
        lang = request.args.get("lang", "en")

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
            success_url=success_url + f"?type={order_type}&user_id={user_id}&lang={lang}",
            cancel_url=cancel_url + f"?type={order_type}&user_id={user_id}&lang={lang}",
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
    order_type = request.args.get("type", 1)

    if order_type == "2":
        lang = request.args.get('lang', 'en')  # Получаем выбранный язык или устанавливаем 'en' по умолчанию
        user_id = request.args.get('user_id', None)  # Получаем выбранный язык или устанавливаем 'en' по умолчанию
        return redirect(url_for('main.proforma', user_id=user_id,  lang=lang))

    return redirect('https://t.me/PicnicsAlicanteBot?start=payment_success')

# Маршрут для обработки отмены платежа
@main.route('/payment-cancelled')
def payment_cancelled():
    order_type = request.args.get("type", 1)

    if order_type == "2":
        lang = request.args.get('lang', 'en')  # Получаем выбранный язык или устанавливаем 'en' по умолчанию
        user_id = request.args.get('user_id', None)  # Получаем выбранный язык или устанавливаем 'en' по умолчанию
        return redirect(url_for('main.booking_page', user_id=user_id,  lang=lang))

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

@main.route('/ver1.0/select-language')
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
                    return redirect(url_for('main.booking_page', lang=lang, user_id=user_id))

                else:
                    # Неверный пароль
                    flash((translations[lang]['incorrect_password'], 'danger'))  # Используем перевод для сообщения
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

            flash((translations[lang]['registration_successful'], 'success', user_id))
            return redirect(url_for('main.index', lang=lang))

        except Exception as e:
            conn.rollback()  # Отмена транзакции при ошибке
            flash(f"{translations[lang]['database_error']} ({e})", 'danger')  # Перевод + текст ошибки
            return redirect(url_for('main.index', lang=lang, translations=translations[lang]))


        finally:
            cursor.close()
            conn.close()

    return render_template('register.html', lang=lang, translations=translations[lang], labels=field_labels[lang])

@main.route('/ver1.0/booking-page/<int:user_id>', methods=['GET'])
# def booking_page(user_id):
#     lang = request.args.get('lang', 'en')  # Получаем выбранный язык или устанавливаем 'en' по умолчанию
#
#     # Проверка, что lang есть в translations и field_labels
#     if lang not in translations or lang not in field_labels:
#         flash(f"Invalid language selected: {lang}", "danger")
#         return redirect(url_for('main.index', lang='en'))
#
#     return render_template(
#         'booking.html',
#         lang=lang,
#         user_id=user_id,
#         form=RegistrationForm()
#     )

@main.route('/ver1.0/booking-page/<int:user_id>', methods=['GET'])
def booking_page(user_id):
    # Получение языка из параметров запроса

    lang = request.args.get('lang', 'en')  # Получаем выбранный язык

    # Проверка, что язык есть в словаре переводов
    if lang not in translations:
        lang = 'en'  # Устанавливаем язык по умолчанию, если выбранный язык не поддерживается

    # Передача перевода в шаблон
    current_translations = translations[lang]

    return render_template(
        'booking.html',
        lang=lang,
        translations=current_translations,  # Передаём переводы
        user_id=user_id,
        form=RegistrationForm()  # Передаём форму
    )

@main.route('/ver1.0/receive-booking/<int:user_id>', methods=['POST'])
def receive_booking(user_id):
    lang = request.args.get('lang', 'en')  # Получаем выбранный язык или устанавливаем 'en' по умолчанию

    # Проверка, что lang есть в translations и field_labels
    if lang not in translations or lang not in field_labels:
        flash(f"Invalid language selected: {lang}", "danger")
        return redirect(url_for('main.index', lang='en'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Получаем данные формы
        username = form.username.data
        selected_date = form.selected_date.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        people_count = form.people_count.data
        selected_style = form.selected_style.data
        preferences = form.preferences.data
        city = form.city.data

        # Вычисление общей стоимости
        duration = get_duration(start_time, end_time)
        total_cost = calculate_total_cost(duration, people_count)

        # Получаем session_number из базы
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(session_number) FROM orders WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        session_number = result[0] if result and result[0] is not None else 1

        # Вставляем данные в заказ
        order = (
        username, selected_date, start_time, end_time, duration, people_count, selected_style, city, preferences,
        total_cost, user_id, session_number)
        insert_order(order)

        # После успешной отправки формы, переходим на страницу оплаты
        return redirect(url_for('main.order_payment', user_id=user_id, lang=lang))
    else:
        # Если есть ошибки в форме, отобразим их
        for field, error_list in form.errors.items():
            for error in error_list:
                flash(f"Error in {field}: {error}", "danger")

    return render_template('booking.html', form=form, lang=lang)


@main.route('/ver1.0/booking-summary/<int:user_id>', methods=['GET'])
def generate_booking_summary(user_id):
    lang = request.args.get('lang', 'en')  # Получаем выбранный язык или устанавливаем 'en' по умолчанию

    # Проверка, что lang есть в translations и field_labels
    if lang not in translations or lang not in field_labels:
        flash(f"Invalid language selected: {lang}", "danger")
        return redirect(url_for('main.index', lang='en'))

    return render_template(
        'booking.html',
        lang=lang,
        user_id=user_id,
    )

@main.route('/ver1.0/order-payment/<int:user_id>', methods=['GET'])
def order_payment(user_id):
    # Получаем информацию о заказе из базы данных (в том числе язык)
    order_info = get_order_info(user_id)

    if not order_info:
        # Если ордер не найден, возвращаем ошибку или редирект на другую страницу
        return redirect(url_for('main.error_page', lang='en'))  # Можно по умолчанию вернуть на английский

    # Извлекаем язык из информации о заказе
    lang = order_info.get('language', 'en')  # Если язык не найден, по умолчанию будет 'en'

    # Проверка, что выбранный язык существует в переводах
    if lang not in translations or lang not in order_field_labels:
        lang = 'en'  # Устанавливаем язык по умолчанию, если языка нет в словарях

    # Генерация ссылки для перехода на страницу оплаты (например, Stripe)
    stripe_payment_link = os.getenv('BASE_URL') + f"/create-payment?c={user_id}&type=2&lang={lang}"

    # Ссылка для возврата на форму
    back_to_form_link = url_for('main.booking_page', user_id=user_id, lang=lang)

    # Передаем переводы для текущего языка и сам заказ
    return render_template(
        'order_payment.html',
        lang=lang,
        order=order_info,  # Передаем информацию о заказе
        stripe_payment_link=stripe_payment_link,
        back_to_form_link=back_to_form_link,
        order_field_labels=order_field_labels[lang]  # Передаем переводы для ордера
    )


# @main.route('/ver1.0/proforma/<int:user_id>', methods=['GET'])
# def proforma(user_id):
#     # Получаем язык из параметров запроса (по умолчанию 'en')
#     lang = request.args.get('lang', 'en')
#
#         # Проверка, что выбранный язык существует в переводах
#     if lang not in bot_translations:
#         lang = 'en'  # Устанавливаем язык по умолчанию, если языка нет в словарях
#
#     # Получаем информацию о заказе из базы данных на основе последней сессии пользователя
#     order_info = get_order_info(user_id)
#
#     if not order_info:
#         # Если ордер не найден, возвращаем ошибку или редирект на другую страницу
#         return redirect(url_for('main.error_page', lang=lang))
#
#     # Генерация текста ордера
#     order_text = f"""
#     <h3>{translations[lang]['order_confirmed']}</h3>
#     <strong>{translations[lang]['proforma_number']}:</strong> {order_info['order_id']} <br>
#     <hr>
#
#
#     <strong>{translations[lang]['client_name']}:</strong> {order_info['user_name']}<br>
#     <strong>{translations[lang]['preferences']}:</strong> {order_info['preferences']}<br>
#     <strong>{translations[lang]['selected_style']}:</strong> {order_info['selected_style']}<br>
#     <strong>{translations[lang]['city']}:</strong> {order_info['city']}<br>
#     <strong>{translations[lang]['people_count']}:</strong> {order_info['people_count']}<br>
#     <strong>{translations[lang]['selected_date']}:</strong> {order_info['selected_date']}<br>
#     <strong>{translations[lang]['start_time']}:</strong> {order_info['start_time']}<br>
#     <strong>{translations[lang]['duration']}:</strong> {order_info['duration']} hours<br>
#     <hr>
#     <strong>{translations[lang]['calculated_cost']}:</strong> {order_info['calculated_cost'] - 20} EUR
#     """
#
#     trans = bot_translations.get(lang, bot_translations['en'])  # Используем 'en' как язык по умолчанию
#
#     proforma_number = f"{order_info['user_id']}_{order_info['session_number']}_{order_info['status']}"
#     contact_message = f"{trans['whatsapp_message']} {proforma_number}. {trans['whatsapp_footer']}"
#
#     # Кодируем сообщение для использования в URL
#     encoded_message = urllib.parse.quote(contact_message)
#
#     # Генерация ссылки для перехода на страницу оплаты (например, Stripe)
#     wa_link = WA_URL + f"?text={encoded_message}"
#
#     # Ссылка для возврата на форму (если нужно вернуться)
#
#     return render_template(
#         'proforma.html',  # Шаблон, который рендерим
#         lang=lang,  # Передаем текущий язык
#         translations=translations[lang],  # Передаем переводы для выбранного языка
#         order=order_info,  # Передаем информацию о заказе
#         wa_link=wa_link,  # Ссылка на WhatsApp для связи
#         instagram_link=INSTAGRAM_URL  # Ссылка на Instagram
#     )
#
# @main.route('/ver1.0/proforma/<int:user_id>', methods=['GET'])
# def proforma(user_id):
#     # Получаем язык из параметров запроса (по умолчанию 'en')
#     lang = request.args.get('lang', 'en')
#
#     # Проверка, что выбранный язык существует в переводах
#     if lang not in bot_translations:
#         lang = 'en'  # Устанавливаем язык по умолчанию
#
#     # Получаем информацию о заказе
#     order_info = get_order_info(user_id)
#
#     if not order_info:
#         # Если ордер не найден, возвращаем ошибку или редирект на другую страницу
#         return redirect(url_for('main.error_page', lang=lang))
#
#     # Генерация текста проформы с использованием переводов из словаря бота
#     order_text = f"""
#     <h3>{bot_translations[lang]['order_confirmed']}</h3>
#     <strong>{bot_translations[lang]['proforma_number']}:</strong> {order_info['order_id']} <br>
#     <hr>
#
#     <strong>{bot_translations[lang]['event_date']}:</strong> {order_info['selected_date']} <br>
#     <strong>{bot_translations[lang]['time']}:</strong> {order_info['start_time']} - {order_info['end_time']} <br>
#     <strong>{bot_translations[lang]['people_count']}:</strong> {order_info['people_count']} <br>
#     <strong>{bot_translations[lang]['event_style']}:</strong> {order_info['selected_style']} <br>
#     <strong>{bot_translations[lang]['city']}:</strong> {order_info['city']} <br>
#     <strong>{bot_translations[lang]['amount_to_pay']}:</strong> {order_info['calculated_cost'] - 20} {bot_translations[lang]['currency']} <br>
#     <hr>
#     <strong>{bot_translations[lang]['delivery_info']}</strong>
#     """
#
#     # Создаем ссылку для WhatsApp сообщения
#     trans = bot_translations.get(lang, bot_translations['en'])  # Используем 'en' как язык по умолчанию
#
#     proforma_number = f"{order_info['user_id']}_{order_info['session_number']}_{order_info['status']}"
#     contact_message = f"{trans['whatsapp_message']} {proforma_number}. {trans['whatsapp_footer']}"
#
#     # Кодируем сообщение для использования в URL
#     encoded_message = urllib.parse.quote(contact_message)
#
#     # Генерация ссылки для перехода на WhatsApp
#     wa_link = WA_URL + f"?text={encoded_message}"
#
#     # Генерация ссылки для Instagram
#     instagram_link = INSTAGRAM_URL  # Уже передаем в шаблон
#
#     # Ссылка для возврата на главную страницу
#     home_link = url_for('main.index', lang=lang)
#
#     # Передаем переводы и информацию о заказе в шаблон
#     return render_template(
#         'proforma.html',  # Шаблон, который рендерим
#         lang=lang,  # Передаем текущий язык
#         translations=bot_translations[lang],  # Передаем переводы для выбранного языка из словаря бота
#         order=order_info,  # Передаем информацию о заказе
#         wa_link=wa_link,  # Ссылка на WhatsApp для связи
#         instagram_link=instagram_link,  # Ссылка на Instagram
#         home_link=home_link  # Ссылка на главную страницу
#     )
@main.route('/ver1.0/proforma/<int:user_id>', methods=['GET'])
def proforma(user_id):
    lang = request.args.get('lang', 'en')

    if lang not in bot_translations:
        lang = 'en'
    if lang not in translations or lang not in order_field_labels:
        lang = 'en'  # Устанавливаем язык по умолчанию, если языка нет в словарях

    # Получаем информацию о заказе
    order_info = get_order_info(user_id)

    if not order_info:
        return redirect(url_for('main.error_page', lang=lang))

    # Генерация номера проформы
    proforma_number = f"{order_info['user_id']}_{order_info['session_number']}_{order_info['status']}"

    # Ссылка на WhatsApp
    contact_message = f"{bot_translations[lang]['whatsapp_message']} {proforma_number}. {bot_translations[lang]['whatsapp_footer']}"
    encoded_message = urllib.parse.quote(contact_message)
    wa_link = WA_URL + f"?text={encoded_message}"

    return render_template(
        'proforma.html',
        lang=lang,
        bot_translations=bot_translations,
        order_info=order_info,
        proforma_number=proforma_number,
        wa_link=wa_link,
        instagram_link=INSTAGRAM_URL,
        order_field_labels=order_field_labels[lang]  # Добавляем передачу order_field_labels
    )

