import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # Эта строка подгружает переменные из .env файла

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')

    from .routes import main  # Импортируем ваш Blueprint
    app.register_blueprint(main)

    return app
