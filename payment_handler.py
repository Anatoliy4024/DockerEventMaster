import os
import stripe
import psycopg2
import logging
from flask import Flask, request, jsonify, redirect, url_for
from dotenv import load_dotenv

from status_3 import update_order_status_to_paid  # Подключаем функцию обновления статуса

# Загрузка переменных окружения
load_dotenv()

# Инициализация Flask
app = Flask(__name__)

# Настройка Stripe с использованием ключей из переменных окружения
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
success_url = os.getenv('SUCCESS_URL')
cancel_url = os.getenv('CANCEL_URL')

# Функция для получения последнего order_id из базы данных
def get_last_order_id():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    order_id = None
    try:
        cursor = conn.cursor()
        query = "SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            order_id = result[0]
        else:
            logging.error("Order ID not found")
    except psycopg2.Error as e:
        logging.error(f"Error fetching order_id: {e}")
    finally:
        cursor.close()
        conn.close()

    return order_id

@app.route('/', methods=['GET'])
def index():
    try:
        # Получаем последний order_id из базы данных
        order_id = get_last_order_id()

        if order_id is None:
            return jsonify({"error": "Order ID not found"}), 400

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
                'order_id': order_id  # Передаем order_id в метаданные
            }
        )
        # Перенаправляем пользователя на страницу оплаты Stripe
        return redirect(session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

# # Маршрут для создания платежной сессии
# @app.route('/create-checkout-session', methods=['POST'])
# def create_checkout_session():
#     try:
#         # Получаем последний order_id из базы данных
#         order_id = get_last_order_id()
#
#         if order_id is None:
#             return jsonify({"error": "Order ID not found"}), 400
#
#         # Создаем платежную сессию Stripe с передачей order_id в метаданных
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'eur',
#                     'product_data': {
#                         'name': 'Оплата заказа',
#                     },
#                     'unit_amount': 2000,  # 20 евро
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url=success_url,
#             cancel_url=cancel_url,
#             metadata={
#                 'order_id': order_id  # Передаем order_id в метаданные
#             }
#         )
#         # Перенаправляем пользователя на страницу оплаты Stripe
#         return redirect(session.url, code=303)
#     except Exception as e:
#         return jsonify(error=str(e)), 403

# Маршрут для обработки успешной оплаты
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
@app.route('/webhook', methods=['POST'])
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

        # Получаем order_id из метаданных платежной сессии
        order_id = session['metadata']['order_id']
        print(f"Оплата прошла успешно для order_id: {order_id}")

        # Обновляем статус заказа на "оплачено"
        update_order_status_to_paid(order_id)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
