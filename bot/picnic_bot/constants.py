import os
from datetime import datetime

# Путь к базе данных SQLite
# DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'sqlite.db')

# Заголовки для выбора времени
time_selection_headers = {
    'start': {
        'en': "Select start and end time (minimum duration 2 hours)",
        'ru': "Выберите начальное и конечное время (минимальная продолжительность 2 часа)",
        'es': "Seleccione la hora de inicio y fin (duración mínima de 2 horas)",
        'fr': "Sélectionnez l'heure de début et de fin (durée minimale de 2 heures)",
        'uk': "Виберіть час початку та закінчення (мінімальна тривалість 2 години)",
        'pl': "Wybierz czas rozpoczęcia i zakończenia (minimalny czas trwania 2 godziny)",
        'de': "Wählen Sie Start- und Endzeit (Mindestdauer 2 Stunden)",
        'it': "Seleziona l'ora di inizio e di fine (durata minima di 2 ore)"
    },
    'end': {
        'en': "Select the end time",
        'ru': "Выберите конечное время",
        'es': "Seleccione la hora de finalización",
        'fr': "Sélectionnez l'heure de fin",
        'uk': "Виберіть час закінчення",
        'pl': "Wybierz czas zakończenia",
        'de': "Wählen Sie die Endzeit",
        'it': "Seleziona l'ora di fine"
    }
}

# Заголовки для выбора количества людей
people_selection_headers = {
    'en': "How many people are attending?",
    'ru': "Сколько человек будет присутствовать?",
    'es': "¿Cuántas personas asistirán?",
    'fr': "Combien de personnes seront présentes?",
    'uk': "Скільки людей буде присутніх?",
    'pl': "Ile osób będzie obecnych?",
    'de': "Wie viele Personen nehmen teil?",
    'it': "Quante persone saranno presenti?"
}

# Заголовки для выбора стиля мероприятия
party_styles_headers = {
    'en': "What style do you choose?",
    'ru': "Какой стиль вы выбираете?",
    'es': "¿Cuál es tu evento?",
    'fr': "Quel style choisissez-vous?",
    'uk': "Який стиль ви обираєте?",
    'pl': "Jaki styl wybierasz?",
    'de': "Welchen Stil wählen Sie?",
    'it': "Che stile scegli?"
}

# Заголовки для выбора города
city_selection_headers = {
    'en': "Select your city",
    'ru': "Выберите ваш город",
    'es': "Seleccione su ciudad",
    'fr': "Sélectionnez votre ville",
    'uk': "Виберіть ваше місто",
    'pl': "Wybierz swoje miasto",
    'de': "Wählen Sie Ihre Stadt",
    'it': "Seleziona la tua città"
}

# Заголовки для выбора предпочтений
preferences_headers = {
    'en': "Please specify your preferences",
    'ru': "Укажите ваши предпочтения",
    'es': "Especifique sus preferencias",
    'fr': "Veuillez préciser vos préférences",
    'uk': "Вкажіть ваші уподобання",
    'pl': "Określ swoje preferencje",
    'de': "Bitte geben Sie Ihre Vorlieben an",
    'it': "Specifica le tue preferenze"
}

# Словарь всех возможных заголовков для удобства
all_headers = {
    'time_selection': time_selection_headers,
    'people_selection': people_selection_headers,
    'party_styles': party_styles_headers,
    'city_selection': city_selection_headers,
    'preferences': preferences_headers
}

# Тексты для установки времени
time_set_texts = {
    'start_time': {
        'en': 'Start time set to {}. Now select end time.',
        'ru': 'Время начала установлено на {}. Теперь выберите время окончания.',
        'es': 'La hora de inicio se ha establecido en {}. Ahora selecciona la hora de finalización.',
        'fr': 'L\'heure de début est fixée à {}. Maintenant, sélectionnez l\'heure de fin.',
        'uk': 'Час початку встановлено на {}. Тепер виберіть час закінчення.',
        'pl': 'Czas rozpoczęcia ustawiono na {}. Teraz wybierz czas zakończenia.',
        'de': 'Startzeit auf {} gesetzt. Wählen Sie nun die Endzeit.',
        'it': 'L\'ora di inizio è stata impostata su {}. Ora seleziona l\'ora di fine.'
    },
    'end_time': {
        'en': 'End time set to {}. Confirm your selection.',
        'ru': 'Время окончания установлено на {}. Подтвердите свой выбор.',
        'es': 'La hora de finalización se ha establecido en {}. Confirma tu selección.',
        'fr': 'L\'heure de fin est fixée à {}. Confirmez votre sélection.',
        'uk': 'Час закінчення встановлено на {}. Підтвердіть свій вибір.',
        'pl': 'Czas zakończenia ustawiono na {}. Potwierdź swój wybór.',
        'de': 'Endzeit auf {} gesetzt. Bestätigen Sie Ihre Auswahl.',
        'it': 'L\'ora di fine è stata impostata su {}. Conferma la tua selezione.'
    }
}

# Статусы заказов
ORDER_STATUS = {
    "1-не заполнено - невозможно выполнить расчет стоимости": 1,
    "2-заполнено для расчета": 2,
    "3-зарезервировано - заказчик оплатил аванс": 3,
    "4-Админ и Сервисная служба получили сообщение о новой ПРОФОРМЕ": 4,
    "5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ": 5,
    "6-Админ зашел в АдминБот и просмотрела новую ПРОФОРМУ": 55,
    "0-Админ удалил ивент": 0
}

# Класс для хранения временных данных
class TemporaryData:
    def __init__(self):
        self.user_name = None
        self.city = None
        self.preferences = None
        self.language = None  # Поддержка языка

    def set_user_name(self, user_name):
        self.user_name = user_name

    def get_user_name(self):
        return self.user_name

    def clear_user_name(self):
        self.user_name = None

    def set_city(self, city):
        self.city = city

    def get_city(self):
        return self.city

    def clear_city(self):
        self.city = None

    def set_preferences(self, preferences):
        self.preferences = preferences

    def get_preferences(self):
        return self.preferences

    def clear_preferences(self):
        self.preferences = None

    def set_language(self, language):
        self.language = language  # Метод для установки языка

    def get_language(self):
        return self.language  # Метод для получения языка

    def clear_language(self):
        self.language = None  # Метод для очистки языка


# Класс для хранения пользовательских данных
class UserData:
    def __init__(self, user_id=None, username=None, language='en'):
        self.user_id = user_id
        self.username = username
        self.language = language
        self.name = None
        self.preferences = None
        self.city = None
        self.month_offset = 0
        self.step = None
        self.start_time = None
        self.end_time = None
        self.person_count = None
        self.style = None
        self.date = None
        self.session_number = None  # Добавляем свойство session_number
        self.calculated_cost = None  # Добавляем новое свойство

    # Метод для установки значения session_number
    def set_session_number(self, session_number):
        self.session_number = session_number

    # Метод для получения значения session_number
    def get_session_number(self):
        return self.session_number

    def get_month_offset(self):
        return self.month_offset

    def set_month_offset(self, offset):
        self.month_offset = offset

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_language(self, language):
        self.language = language

    def get_language(self):
        return self.language

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_preferences(self, preferences):
        self.preferences = preferences

    def get_preferences(self):
        return self.preferences

    def set_city(self, city):
        self.city = city

    def get_city(self):
        return self.city

    def set_step(self, step):
        self.step = step

    def get_step(self):
        return self.step

    def set_start_time(self, start_time):
        self.start_time = start_time

    def get_start_time(self):
        return self.start_time

    def set_end_time(self, end_time):
        self.end_time = end_time

    def get_end_time(self):
        return self.end_time

    def set_person_count(self, person_count):
        self.person_count = person_count

    def get_person_count(self):
        return self.person_count

    def set_style(self, style):
        self.style = style

    def get_style(self):
        return self.style

    def set_date(self, date):
        self.date = date

    def get_date(self):
        return self.date

    def get_selected_date(self):
        return self.date

    def clear_time(self):
        self.start_time = None
        self.end_time = None

    def set_calculated_cost(self, calculated_cost):
        self.calculated_cost = calculated_cost

    def get_calculated_cost(self):
        return self.calculated_cost



    # Метод для расчета длительности
    def get_duration(self):
        if self.start_time and self.end_time:
            start_time = datetime.strptime(self.start_time, '%H:%M')
            end_time = datetime.strptime(self.end_time, '%H:%M')
            duration_minutes = (end_time - start_time).seconds // 60
            duration_hours = (duration_minutes // 60) + (1 if duration_minutes % 60 != 0 else 0)
            return duration_hours
        return 0