# import os
# from datetime import timedelta
# import stripe
# from flask import Flask, request, jsonify, redirect
# import psycopg2  # Библиотека для работы с PostgreSQL
# from dotenv import load_dotenv
#
# from bot.picnic_bot.data_reserve import get_reserved_times_for_date, check_time_reserved
# from bot.picnic_bot.status_3 import update_order_status_to_paid, get_last_order_id
#
# # Загрузка переменных окружения
# load_dotenv()
#
# # Инициализация Flask и Stripe
# app = Flask(__name__)
# stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
# publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
# success_url = os.getenv('SUCCESS_URL')
# cancel_url = os.getenv('CANCEL_URL')
#
#
# # Функция для подключения к базе данных
# def get_db_connection():
#     return psycopg2.connect(
#         host=os.getenv('DB_HOST'),
#         database=os.getenv('DB_NAME'),
#         user=os.getenv('DB_USER'),
#         password=os.getenv('DB_PASSWORD')
#     )
#
#
# # Маршрут для создания платежной сессии
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     try:
#         user_id = request.args.get("c")
#         if not user_id:
#             return jsonify(error="Не указан user ID"), 400
#
#         # Получаем последний order_id для этого пользователя
#         order = get_last_order_id(int(user_id))
#         if order is None:
#             return jsonify({"error": "Order ID не найден"}), 400
#
#         selected_date = order[1]
#         start_time = order[2]
#         end_time = order[3]
#
#         # Проверка доступности времени перед оплатой
#         reserved_intervals = get_reserved_times_for_date(selected_date)
#
#         start = timedelta(hours=start_time.hour, minutes=start_time.minute) - timedelta(hours=4, minutes=30)
#         end = timedelta(hours=end_time.hour, minutes=end_time.minute) + timedelta(hours=5, minutes=30)
#
#         while start < end:
#             hours = int(start.total_seconds() // 3600)
#             minutes = int((start.total_seconds() % 3600) // 60)
#             start_time_str = f"{hours:02d}:{minutes:02d}"
#             if check_time_reserved(start_time_str, reserved_intervals):
#                 return redirect('https://t.me/PicnicsAlicanteBot?start=expired_date')
#
#             start += timedelta(minutes=30)
#
#         # Создание сессии Stripe
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'eur',
#                     'product_data': {
#                         'name': 'Оплата заказа',
#                     },
#                     'unit_amount': 2000,  # 20 EUR
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url=success_url,
#             cancel_url=cancel_url,
#             metadata={
#                 'order_id': order[0],
#                 'user_id': user_id  # Передаем user_id в метаданных для связи
#             }
#         )
#         return redirect(session.url, code=303)
#     except Exception as e:
#         return jsonify(error=str(e)), 403
#
#
# # Webhook для обработки событий от Stripe
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     payload = request.get_data(as_text=True)
#     sig_header = request.headers.get('Stripe-Signature')
#     endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
#
#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except stripe.error.SignatureVerificationError as e:
#         return jsonify({'error': str(e)}), 400
#
#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#
#         # Извлекаем order_id и user_id из метаданных
#         order_id = session['metadata']['order_id']
#         user_id = session['metadata']['user_id']
#         customer_email = session['customer_details']['email']  # Получаем email пользователя
#
#         # Обновляем статус заказа и email пользователя в базе данных
#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()
#
#             # Обновляем статус заказа на "оплачено"
#             update_order_status_to_paid(order_id)
#
#             # Обновляем email в таблице users
#             cursor.execute("""
#                 UPDATE users
#                 SET email = %s, updated_at = NOW()
#                 WHERE user_id = %s
#             """, (customer_email, user_id))
#
#             conn.commit()
#             cursor.close()
#             conn.close()
#         except Exception as e:
#             print(f"Ошибка базы данных: {e}")
#             return jsonify({'error': 'Не удалось обновить базу данных'}), 500
#
#     return jsonify({'status': 'success'}), 200
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
#






# это предыдущая версия без выкачки mail в таблицу users БД
import os
from datetime import timedelta, datetime
import logging

import psycopg2
import stripe
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

from bot.picnic_bot.data_reserve import get_reserved_times_for_date, check_time_reserved
from bot.picnic_bot.status_3 import update_order_status_to_paid, get_last_order_id  # Подключаем функцию обновления статуса

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация Flask
app = Flask(__name__)

# Настройка Stripe с использованием ключей из переменных окружения
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
success_url = os.getenv('SUCCESS_URL')
cancel_url = os.getenv('CANCEL_URL')

# Функция для подключения к базе данных
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )


# Новый корневой маршрут для непосредственного создания платежной сессии
@app.route('/', methods=['GET','POST'])
def index():
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
                'order_id': order[0]  # Передаем order_id в метаданные
            }
        )
        # Перенаправляем пользователя на страницу оплаты Stripe
        return redirect(session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/payment-success')
def payment_success():
    # Возвращаемся в бота после успешной оплаты
    return redirect('https://t.me/PicnicsAlicanteBot?start=payment_success')

# Маршрут для обработки отмены платежа
@app.route('/payment-cancelled')
def payment_cancelled():
    # Возвращаемся в бота после отмены платежа
    return redirect('https://t.me/PicnicsAlicanteBot?start=payment_cancelled')

# Вебхук для обработки уведомлений от Stripe
@app.route('/webhook', methods=['POST','GET'])
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

    # if event['type'] == 'checkout.session.completed':
    #     session = event['data']['object']
    #
    #     # Получаем order_id из метаданных платежной сессии
    #     order_id = session['metadata']['order_id']
    #     print(f"Оплата прошла успешно для order_id: {order_id}")
    #
    #     # Обновляем статус заказа на "оплачено"
    #     update_order_status_to_paid(order_id)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Извлекаем order_id и user_id из метаданных
        order_id = session['metadata']['order_id']
        user_id = session['metadata']['user_id']
        customer_email = session['customer_details']['email']  # Получаем email пользователя

        # Обновляем статус заказа и email пользователя в базе данных
        try:
            conn = get_db_connection()
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
