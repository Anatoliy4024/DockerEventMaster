import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from web.myapp.email_utils import send_email
from web.utils.db import create_connection

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя через email и пароль."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверяем, есть ли уже такой email в базе данных
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE registration_email = %s", (email,))
        user = cursor.fetchone()

        if user:
            # Если email уже существует, показываем сообщение об ошибке
            flash('Этот email уже зарегистрирован. Попробуйте войти.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('auth.register'))

        # Хэшируем пароль
        hashed_password = generate_password_hash(password)

        # Добавляем нового пользователя в базу данных
        cursor.execute(
            "INSERT INTO users (registration_email, registration_passw) VALUES (%s, %s)",
            (email, hashed_password)
        )
        conn.commit()

        # Закрываем соединение с базой данных
        cursor.close()
        conn.close()

        # Сообщение об успешной регистрации
        flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Обработка запроса на сброс пароля."""
    if request.method == 'POST':
        email = request.form.get('email')

        # Подключение к базе данных
        conn = create_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли email в базе
        cursor.execute("SELECT user_id FROM users WHERE registration_email = %s", (email,))
        user = cursor.fetchone()

        if user:
            # Генерация токена
            token = str(uuid.uuid4())

            # Сохранение токена в базе данных
            cursor.execute("""
                UPDATE users SET reset_token = %s, updated_at = NOW()
                WHERE registration_email = %s
            """, (token, email))
            conn.commit()

            # Отправка письма с ссылкой для сброса пароля
            reset_link = f"http://localhost:5000/auth/reset-password?token={token}"
            send_email(
                to_address=email,
                subject="Сброс пароля",
                body=f"Для сброса пароля перейдите по ссылке: {reset_link}"
            )
            flash('На вашу почту отправлено письмо для сброса пароля.', 'info')
        else:
            flash('Этот email не зарегистрирован в системе.', 'danger')

        cursor.close()
        conn.close()
        return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Сброс пароля через уникальную ссылку."""
    token = request.args.get('token')

    if request.method == 'POST':
        new_password = request.form.get('password')

        # Подключение к базе данных
        conn = create_connection()
        cursor = conn.cursor()

        # Проверяем токен и обновляем пароль
        cursor.execute("SELECT user_id FROM users WHERE reset_token = %s", (token,))
        user = cursor.fetchone()

        if user:
            hashed_password = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE users
                SET registration_passw = %s, reset_token = NULL, updated_at = NOW()
                WHERE reset_token = %s
            """, (hashed_password, token))
            conn.commit()
            flash('Пароль успешно обновлен. Теперь вы можете войти.', 'success')
        else:
            flash('Неверный или устаревший токен.', 'danger')

        cursor.close()
        conn.close()
        return redirect(url_for('auth.login'))  # Предполагается, что есть маршрут для входа

    return render_template('reset_password.html', token=token)


