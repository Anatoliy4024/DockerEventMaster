import os
import stripe
from flask import Flask, request, jsonify, redirect

from dotenv import load_dotenv
load_dotenv()

print(os.getenv('STRIPE_SECRET_KEY'))

# Инициализация Flask
app = Flask(__name__)

# Получаем ключи Stripe из переменных окружения
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

print(f"Loaded Stripe API Key: {stripe.api_key}")

publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
success_url = os.getenv('SUCCESS_URL')
cancel_url = os.getenv('CANCEL_URL')


# Маршрут для корневого пути
@app.route('/')
def index():
    return '''
        <h1>Welcome to the Stripe Payment Gateway</h1>
        <p>To initiate a payment, please click the button below:</p>
        <form action="/create-checkout-session" method="POST">
            <button type="submit">Create Checkout Session</button>
        </form>
    '''


# Маршрут для создания платежной сессии
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # Здесь ты можешь указать сумму и валюту (например, 20 евро = 2000 евроцентов)
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
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

# Маршрут для обработки успешной оплаты
@app.route('/payment-success')
def payment_success():
    # Здесь происходит возврат в бота с сообщением об успешной оплате
    return "Оплата прошла успешно! Можете вернуться в бот."

# Маршрут для обработки отмены платежа
@app.route('/payment-cancelled')
def payment_cancelled():
    # Сообщение об отмене платежа
    return "Платеж был отменен. Можете вернуться в бот."

# Вебхук для получения уведомлений от Stripe
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
        # Невалидные данные
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Неверная подпись
        return jsonify({'error': str(e)}), 400

    # Обрабатываем событие
    if event['type'] == 'checkout.session.completed':
        # Здесь можно добавить логику для успешной оплаты
        print('Оплата прошла успешно!')

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
