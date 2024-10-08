# shared/constants.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import os


# Статусы заказов, используемые в системе. Каждое значение представляет определенный этап обработки заказа.
ORDER_STATUS = {
    "1-не заполнено - невозможно выполнить расчет стоимости": 1,
    "2-заполнено для расчета": 2,
    "3-зарезервировано - заказчик оплатил аванс": 3,
    "4-Ирина и Сервисная служба получили сообщение о новой ПРОФОРМЕ": 4,
    "5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ": 5,
    "6-Администратор зашел в АдминБот и просмотрел новую ПРОФОРМУ": 6,
    "0-Администратор удалил ПРОФОРМУ в календаре (статус 0 )": 0

}

# Заголовки для различных шагов выбора времени, представленные на разных языках.
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

# Заголовки для выбора количества людей, участвующих в мероприятии, на разных языках.
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

# Заголовки для выбора стиля мероприятия на разных языках.
party_styles_headers = {
    'en': "What style do you choose?",
    'ru': "Какой стиль вы выбираете?",
    'es': "¿Cuál es tu событие?",
    'fr': "Quel style choisissez-vous?",
    'uk': "Який стиль ви обираєте?",
    'pl': "Jaki styl wybierasz?",
    'de': "Welchen Stil wählen Sie?",
    'it': "Che stile scegli?"
}

# Заголовки для выбора города проведения мероприятия на разных языках.
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

# Заголовки для указания предпочтений на разных языках.
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

# Словарь, объединяющий все возможные заголовки, для удобства использования.
all_headers = {
    'time_selection': time_selection_headers,
    'people_selection': people_selection_headers,
    'party_styles': party_styles_headers,
    'city_selection': city_selection_headers,
    'preferences': preferences_headers
}

# Тексты для установки времени на разных языках, которые показываются пользователю при выборе времени начала и окончания.
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

# -------------------- Классы --------------------

# Класс для хранения временных данных пользователя, таких как имя, город, предпочтения и язык.
class TemporaryData:
    def __init__(self):
        self.user_name = None  # Имя пользователя
        self.city = None  # Город пользователя
        self.preferences = None  # Предпочтения пользователя
        self.language = None  # Язык, выбранный пользователем

    # Метод для установки имени пользователя
    def set_user_name(self, user_name):
        self.user_name = user_name

    # Метод для получения имени пользователя
    def get_user_name(self):
        return self.user_name

    # Метод для очистки имени пользователя
    def clear_user_name(self):
        self.user_name = None

    # Метод для установки города пользователя
    def set_city(self, city):
        self.city = city

    # Метод для получения города пользователя
    def get_city(self):
        return self.city

    # Метод для очистки города пользователя
    def clear_city(self):
        self.city = None

    # Метод для установки предпочтений пользователя
    def set_preferences(self, preferences):
        self.preferences = preferences

    # Метод для получения предпочтений пользователя
    def get_preferences(self):
        return self.preferences

    # Метод для очистки предпочтений пользователя
    def clear_preferences(self):
        self.preferences = None

    # Метод для установки языка пользователя
    def set_language(self, language):
        self.language = language

    # Метод для получения языка пользователя
    def get_language(self):
        return self.language

    # Метод для очистки языка пользователя
    def clear_language(self):
        self.language = None


# Класс для хранения основной информации о пользователе, такой как ID, имя, язык, шаги в процессе выбора, и данные о мероприятии.
class UserData:
    def __init__(self, user_id=None, username=None, language='en'):
        self.user_id = user_id  # ID пользователя
        self.username = username  # Имя пользователя в системе
        self.language = language  # Язык пользователя
        self.name = None  # Имя пользователя (которое может отличаться от username)
        self.preferences = None  # Предпочтения пользователя
        self.city = None  # Город пользователя
        self.month_offset = 0  # Смещение месяца для выбора даты мероприятия
        self.step = None  # Текущий шаг в процессе взаимодействия с ботом
        self.start_time = None  # Время начала мероприятия
        self.end_time = None  # Время окончания мероприятия
        self.person_count = None  # Количество участников мероприятия
        self.style = None  # Стиль мероприятия, выбранный пользователем
        self.date = None  # Дата мероприятия
        self.session_number = None  # Номер сессии пользователя
        self.calculated_cost = None  # Рассчитанная стоимость мероприятия

    # Метод для установки значения session_number
    def set_session_number(self, session_number):
        self.session_number = session_number

    # Метод для получения значения session_number
    def get_session_number(self):
        return self.session_number

    # Метод для получения смещения месяца
    def get_month_offset(self):
        return self.month_offset

    # Метод для установки смещения месяца
    def set_month_offset(self, offset):
        self.month_offset = offset

    # Метод для установки ID пользователя
    def set_user_id(self, user_id):
        self.user_id = user_id

    # Метод для получения ID пользователя
    def get_user_id(self):
        return self.user_id

    # Метод для установки имени пользователя в системе
    def set_username(self, username):
        self.username = username

    # Метод для получения имени пользователя в системе
    def get_username(self):
        return self.username

    # Метод для установки языка пользователя
    def set_language(self, language):
        self.language = language

    # Метод для получения языка пользователя
    def get_language(self):
        return self.language

    # Метод для установки имени пользователя
    def set_name(self, name):
        self.name = name

    # Метод для получения имени пользователя
    def get_name(self):
        return self.name

    # Метод для установки предпочтений пользователя
    def set_preferences(self, preferences):
        self.preferences = preferences

    # Метод для получения предпочтений пользователя
    def get_preferences(self):
        return self.preferences

    # Метод для установки города пользователя
    def set_city(self, city):
        self.city = city

    # Метод для получения города пользователя
    def get_city(self):
        return self.city

    # Метод для установки текущего шага в процессе взаимодействия
    def set_step(self, step):
        self.step = step

    # Метод для получения текущего шага
    def get_step(self):
        return self.step

    # Метод для установки времени начала мероприятия
    def set_start_time(self, start_time):
        self.start_time = start_time

    # Метод для получения времени начала мероприятия
    def get_start_time(self):
        return self.start_time

    # Метод для установки времени окончания мероприятия
    def set_end_time(self, end_time):
        self.end_time = end_time

    # Метод для получения времени окончания мероприятия
    def get_end_time(self):
        return self.end_time

    # Метод для установки количества участников мероприятия
    def set_person_count(self, person_count):
        self.person_count = person_count

    # Метод для получения количества участников мероприятия
    def get_person_count(self):
        return self.person_count

    # Метод для установки стиля мероприятия
    def set_style(self, style):
        self.style = style

    # Метод для получения стиля мероприятия
    def get_style(self):
        return self.style

    # Метод для установки даты мероприятия
    def set_date(self, date):
        self.date = date

    # Метод для получения даты мероприятия
    def get_date(self):
        return self.date

    # Альтернативный метод для получения даты мероприятия
    def get_selected_date(self):
        return self.date

    # Метод для очистки времени начала и окончания мероприятия
    def clear_time(self):
        self.start_time = None
        self.end_time = None

    # Метод для установки рассчитанной стоимости мероприятия
    def set_calculated_cost(self, calculated_cost):
        self.calculated_cost = calculated_cost

    # Метод для получения рассчитанной стоимости мероприятия
    def get_calculated_cost(self):
        return self.calculated_cost

    # Метод для расчета длительности мероприятия в часах
    def get_duration(self):
        if self.start_time and self.end_time:
            start_time = datetime.strptime(self.start_time, '%H:%M')
            end_time = datetime.strptime(self.end_time, '%H:%M')
            duration_minutes = (end_time - start_time).seconds // 60
            duration_hours = (duration_minutes // 60) + (1 if duration_minutes % 60 != 0 else 0)
            return duration_hours
        return 0

# -------------------- Функции --------------------

# Функция для отключения кнопок выбора языка. Она делает кнопки неактивными, присваивая им callback_data='none'.
def disable_language_buttons(reply_markup):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            # Создаем новую кнопку с тем же текстом, но делаем ее неактивной.
            new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

# Здесь можно добавить другие вспомогательные функции, которые могут потребоваться в будущем.
