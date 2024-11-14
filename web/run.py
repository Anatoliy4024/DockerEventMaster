# run.py
# Точка входа для запуска приложения Flask

from web.myapp import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
