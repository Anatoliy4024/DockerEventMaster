# run.py
# Точка входа для запуска приложения Flask
#from web.myapp import create_app
# from web.myapp import create_app
#
# app = create_app()
#
# if __name__ == '__main__':
#     app.run(debug=True)
#
from web.myapp import create_app
from web.myapp.auth import auth

app = create_app()
app.register_blueprint(auth, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
