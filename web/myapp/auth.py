import os
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

        conn = create_connection()
        cursor = conn.cursor()
        try:
            # Проверяем, есть ли уже такой email в базе данных
            cursor.execute("SELECT user_id FROM users WHERE registration_email = %s", (email,))
            user = cursor.fetchone()

            if user:
                flash('Этот email уже зарегистрирован. Попробуйте войти.', 'danger')
                return redirect(url_for('auth.register'))

            # Хэшируем пароль
            hashed_password = generate_password_hash(password)

            # Добавляем нового пользователя в базу данных
            cursor.execute(
                "INSERT INTO users (registration_email, registration_passw) VALUES (%s, %s) RETURNING user_id",
                (email, hashed_password)
            )
            new_user_id = cursor.fetchone()[0]  # Получаем ID нового пользователя

            # Добавляем запись в таблицу orders
            cursor.execute("""
                INSERT INTO orders (
                    user_id, session_number, language, status,
                    selected_date, start_time, end_time, duration,
                    people_count, selected_style, city, preferences,
                    calculated_cost, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                new_user_id,  # user_id
                1,  # session_number (по умолчанию 1)
                None,  # language
                'pending',  # status (по умолчанию "ожидает заполнения")
                None,  # selected_date
                None,  # start_time
                None,  # end_time
                None,  # duration
                None,  # people_count
                None,  # selected_style
                None,  # city
                None,  # preferences
                None  # calculated_cost
            ))

            conn.commit()
            flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
            return redirect(url_for('auth.register'))

        except Exception as e:
            conn.rollback()  # Отмена транзакции при ошибке
            flash(f'Ошибка: {e}', 'danger')
            return redirect(url_for('auth.register'))

        finally:
            cursor.close()
            conn.close()

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
            reset_link = os.getenv('BASE_URL') + f"/auth/reset-password?token={token}"
            send_email(
                to_address=email,
                subject="Сброс пароля",
                body=f"Для сброса пароля перейдите по ссылке: {reset_link}"
            )
            flash('На вашу почту отправлено письмо для сброса пароля.', 'success')
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
        # return redirect(url_for('auth.login'))  # Предполагается, что есть маршрут для входа
        return redirect(url_for('main.index'))

    return render_template('reset_password.html', token=token)


