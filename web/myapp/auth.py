import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from web.myapp.email_utils import send_email
from web.utils.db import create_connection
from web.myapp.translations import translations



auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя через email и пароль."""
    lang = request.args.get('lang', 'en')  # Определяем язык, по умолчанию 'en'

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
                flash(translations[lang]['email_not_registered'], 'danger')  # Используем перевод
                return redirect(url_for('auth.register', lang=lang))  # Передаем язык в редиректе

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
                lang,  # language
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
            flash(translations[lang]['registration_successful'], 'success')  # Используем перевод
            return redirect(url_for('auth.register', lang=lang))  # Передаем язык

        except Exception as e:
            conn.rollback()  # Отмена транзакции при ошибке
            flash(translations[lang]['database_error'], 'danger')  # Используем перевод
            return redirect(url_for('auth.register', lang=lang))

        finally:
            cursor.close()
            conn.close()

    return render_template('register.html', translations=translations[lang], lang=lang)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Обработка запроса на сброс пароля."""
    lang = request.args.get('lang', 'en')  # Получаем язык, по умолчанию 'en'
    if lang not in translations:  # Проверяем, что язык существует в словаре
        lang = 'en'

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
            reset_link = os.getenv('BASE_URL') + f"/auth/reset-password?token={token}&lang={lang}"
            send_email(
                to_address=email,
                subject=translations[lang]['forgot_password_title'],  # Используем перевод для темы письма
                body=f"{translations[lang]['email_sent']}\n{reset_link}"  # Используем перевод для текста письма
            )
            flash(translations[lang]['email_sent'], 'success')  # Используем переводы
        else:
            flash(translations[lang]['email_not_registered'], 'danger')

        cursor.close()
        conn.close()
        # Редирект с передачей языка
        return redirect(url_for('auth.forgot_password', lang=lang))

    return render_template('forgot_password.html', translations=translations[lang], lang=lang)


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Сброс пароля через уникальную ссылку."""
    token = request.args.get('token')
    lang = request.args.get('lang', 'en')  # Устанавливаем язык по умолчанию 'en'
    if lang not in translations:  # Проверяем, что указанный язык существует в словаре translations
        lang = 'en'

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
            flash(translations[lang]['password_updated'], 'success')  # Используем перевод
        else:
            flash(translations[lang]['invalid_or_expired_token'], 'danger')  # Используем перевод

        cursor.close()
        conn.close()
        return redirect(url_for('main.index', lang=lang))  # Передаем язык в редиректе

    return render_template('reset_password.html', token=token, lang=lang, translations=translations[lang])

