# translations.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup



button_texts = {
    'en': ["GET/VIEW PROFORMA", "CONTACT ORGANIZER", "VISIT GALLERY"],
    'ru': ["ПОЛУЧИТЬ/ПОСМОТРЕТЬ ПРОФОРМУ", "НАПИСАТЬ ОРГАНИЗАТОРУ", "ПЕРЕЙТИ В ГАЛЕРЕЮ"],
    'es': ["OBTENER/VER PROFORMA", "CONTACTAR AL ORGANIZADOR", "VISITAR GALERÍA"],
    'fr': ["OBTENIR/VOIR PROFORMA", "CONTACTER L'ORGANISATEUR", "VISITER LA GALERIE"],
    'uk': ["ОТРИМАТИ/ПЕРЕГЛЯНУТИ ПРОФОРМУ", "ЗВ'ЯЗАТИСЯ З ОРГАНІЗАТОРОМ", "ПЕРЕЙТИ В ГАЛЕРЕЮ"],
    'pl': ["UZYSKAJ/ZOBACZ PROFORMĘ", "SKONTAKTUJ SIĘ Z ORGANIZATOREM", "PRZEJDŹ DO GALERII"],
    'de': ["PROFORMA ERHALTEN/ANSEHEN", "KONTAKT ZUM ORGANISATOR", "GALERIE BESUCHEN"],
    'it': ["OTTENERE/VEDERE PROFORMA", "CONTATTA L'ORGANIZZATORE", "VISITA LA GALLERIA"]
}

translations = {
    'en': {
        'order_confirmed': "Your order is confirmed!",
        'proforma_number': "PROFORMA №",
        'event_date': "Event date:",
        'time': "Time:",
        'people_count': "Number of people:",
        'event_style': "Event style:",
        'city': "City:",
        'amount_to_pay': "Amount to pay:",
        'status': "Status:",
        'delivery_info': "If the event zone is within Alicante (15 km zone), the delivery of equipment is free. If further, the cost is 0.5 euros per km.",
        'currency': "euros",
        'whatsapp_message': "Hi, Irina! I have a question about my order",
        'whatsapp_footer': "(please write your question here)"
    },
    'ru': {
        'order_confirmed': "Ваш заказ подтвержден!",
        'proforma_number': "ПРОФОРМА №",
        'event_date': "Дата мероприятия:",
        'time': "Время:",
        'people_count': "Количество персон:",
        'event_style': "Стиль мероприятия:",
        'city': "Город:",
        'amount_to_pay': "Сумма к оплате:",
        'status': "Статус:",
        'delivery_info': "Если зона мероприятия в пределах Аликанте (15 км зона), доставка реквизита бесплатна. Если дальше, стоимость 0.5 евро за км.",
        'currency': "евро",
        'whatsapp_message': "Привет, Ирина! У меня есть вопрос по поводу моего заказа",
        'whatsapp_footer': "(напишите ваш вопрос здесь)"
    },
    'de': {
        'order_confirmed': "Ihre Bestellung ist bestätigt!",
        'proforma_number': "PROFORMA-NR.",
        'event_date': "Veranstaltungsdatum:",
        'time': "Zeit:",
        'people_count': "Anzahl der Personen:",
        'event_style': "Veranstaltungsstil:",
        'city': "Stadt:",
        'amount_to_pay': "Zu zahlender Betrag:",
        'status': "Status:",
        'delivery_info': "Wenn die Veranstaltungszone innerhalb von Alicante (15 km Zone) liegt, ist die Lieferung der Ausrüstung kostenlos. Wenn weiter, betragen die Kosten 0,5 Euro pro km.",
        'currency': "Euro",
        'whatsapp_message': "Hallo, Irina! Ich habe eine Frage zu meiner Bestellung",
        'whatsapp_footer': "(bitte schreiben Sie hier Ihre Frage)"
    },
    'es': {
        'order_confirmed': "¡Su pedido está confirmado!",
        'proforma_number': "PROFORMA №",
        'event_date': "Fecha del evento:",
        'time': "Hora:",
        'people_count': "Número de personas:",
        'event_style': "Estilo del evento:",
        'city': "Ciudad:",
        'amount_to_pay': "Monto a pagar:",
        'status': "Estado:",
        'delivery_info': "Si la zona del evento está dentro de Alicante (zona de 15 km), la entrega del equipo es gratuita. Si está más lejos, el costo es de 0,5 euros por km.",
        'currency': "euros",
        'whatsapp_message': "Hola, Irina! Tengo una pregunta sobre mi pedido",
        'whatsapp_footer': "(por favor escribe tu pregunta aquí)"
    },
    'fr': {
        'order_confirmed': "Votre commande est confirmée!",
        'proforma_number': "PROFORMA №",
        'event_date': "Date de l'événement:",
        'time': "Heure:",
        'people_count': "Nombre de personnes:",
        'event_style': "Style de l'événement:",
        'city': "Ville:",
        'amount_to_pay': "Montant à payer:",
        'status': "Statut:",
        'delivery_info': "Si la zone de l'événement se trouve dans les environs d'Alicante (zone de 15 km), la livraison de l'équipement est gratuite. Sinon, le coût est de 0,5 euros par km.",
        'currency': "euros",
        'whatsapp_message': "Bonjour, Irina! J'ai une question concernant ma commande",
        'whatsapp_footer': "(veuillez écrire votre question ici)"
    },
    'uk': {
        'order_confirmed': "Ваше замовлення підтверджено!",
        'proforma_number': "ПРОФОРМА №",
        'event_date': "Дата події:",
        'time': "Час:",
        'people_count': "Кількість людей:",
        'event_style': "Стиль заходу:",
        'city': "Місто:",
        'amount_to_pay': "Сума до оплати:",
        'status': "Статус:",
        'delivery_info': "Якщо зона заходу знаходиться в межах Аліканте (зона 15 км), доставка обладнання безкоштовна. Якщо далі, вартість становить 0,5 євро за км.",
        'currency': "євро",
        'whatsapp_message': "Привіт, Ірино! У мене є питання щодо мого замовлення",
        'whatsapp_footer': "(будь ласка, напишіть своє питання тут)"
    },
    'pl': {
        'order_confirmed': "Twoje zamówienie zostało potwierdzone!",
        'proforma_number': "PROFORMA №",
        'event_date': "Data wydarzenia:",
        'time': "Czas:",
        'people_count': "Liczba osób:",
        'event_style': "Styl wydarzenia:",
        'city': "Miasto:",
        'amount_to_pay': "Kwota do zapłaty:",
        'status': "Status:",
        'delivery_info': "Jeśli strefa wydarzenia znajduje się w Alicante (strefa 15 km), dostawa sprzętu jest bezpłatna. Jeśli dalej, koszt wynosi 0,5 euro za km.",
        'currency': "euro",
        'whatsapp_message': "Cześć, Irina! Mam pytanie dotyczące mojego zamówienia",
        'whatsapp_footer': "(proszę napisz tutaj swoje pytanie)"
    },
    'it': {
        'order_confirmed': "Il tuo ordine è confermato!",
        'proforma_number': "PROFORMA №",
        'event_date': "Data dell'evento:",
        'time': "Ora:",
        'people_count': "Numero di persone:",
        'event_style': "Stile dell'evento:",
        'city': "Città:",
        'amount_to_pay': "Importo da pagare:",
        'status': "Stato:",
        'delivery_info': "Se la zona dell'evento è entro 15 km da Alicante, la consegna dell'attrezzatura è gratuita. Se più lontano, il costo è di 0,5 euro per km.",
        'currency': "euro",
        'whatsapp_message': "Ciao, Irina! Ho una domanda sul mio ordine",
        'whatsapp_footer': "(per favore scrivi qui la tua domanda)"
    }


}


translations_yes_no = {
    'confirmation_date': {
        'en': "You selected {date}, correct?",
        'ru': "Вы выбрали {date}, правильно?",
        'es': "Seleccionaste {date}, ¿correcto?",
        'fr': "Vous avez sélectionné {date}, correct ?",
        'uk': "Ви вибрали {date}, правильно?",
        'pl': "Wybrałeś {date}, правильно?",
        'de': "Sie haben {date} gewählt, richtig?",
        'it': "Hai selezionato {date}, corretto?"
    }
}


def language_selection_keyboard():
    """Генерирует клавиатуру для выбора языка."""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 EN", callback_data='lang_en'),
            InlineKeyboardButton("🇪🇸 ES", callback_data='lang_es'),
            InlineKeyboardButton("🇮🇹 IT", callback_data='lang_it'),
            InlineKeyboardButton("🇫🇷 FR", callback_data='lang_fr')
        ],
        [
            InlineKeyboardButton("🇺🇦 UA", callback_data='lang_uk'),
            InlineKeyboardButton("🇵🇱 PL", callback_data='lang_pl'),
            InlineKeyboardButton("🇩🇪 DE", callback_data='lang_de'),
            InlineKeyboardButton("🇷🇺 RU", callback_data='lang_ru')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
