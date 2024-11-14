# email_utils.py

import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

def send_email(to_address, subject, body):
    """Отправляет email с использованием SMTP через Gandi."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 465))  # Убедимся, что порт — это целое число
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Формирование сообщения
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_address

    # Подключение к SMTP серверу с использованием SSL
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_address, msg.as_string())
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")
