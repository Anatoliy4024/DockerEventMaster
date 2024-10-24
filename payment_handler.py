import os
import stripe
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

from bot.picnic_bot.status_3 import update_order_status_to_paid, get_last_order_id  # Подключаем функцию обновления статуса

# Загрузка переменных окружения
load_dotenv()

# Инициализация Flask
app = Flask(__name__)

# Настройка Stripe с использованием ключей из переменных окружения
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
success_url = os.getenv('SUCCESS_URL')
cancel_url = os.getenv('CANCEL_URL')




# Новый корневой маршрут для непосредственного создания платежной сессии
@app.route('/', methods=['GET','POST'])
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
