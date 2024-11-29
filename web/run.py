# run.py
import logging

from web.myapp import create_app
from web.myapp.auth import auth

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='logs.log',
    filemode='w'
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

app = create_app()
app.register_blueprint(auth, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
