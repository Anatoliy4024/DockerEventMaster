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
        'delivery_info': "If the event zone is within Alicante (15 km zone), the delivery of equipment is free. "
                         "If further, the cost is 0.5 euros per km.\n"
                         "Event extension - 30 euros per additional hour.\n"
                         # "To send a message to the organizer and view details — select in the menu above.\n"
                         # "To change the language — press the button with the corresponding flag.\n"
                         "Thank you for using the automatic booking service!",
        'currency': "euros",
        'whatsapp_message': "I have a question about my order",
        'whatsapp_footer': "(Write below what you would like to inquire about the administrator)",
        'instagram_message': 'Go to the gallery',
        'return_home': 'Return to homepage for next order',
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
        'delivery_info': "Если зона мероприятия в пределах Аликанте (15 км зона), доставка реквизита бесплатна. "
                         "Если дальше, стоимость 0.5 евро за км.\n"
                         "Продление ивента - 30 евро за дополнительный час.\n"
                         # "Для отправления сообщения организатору и просмотра — выберите в меню выше. "
                         # "Для изменения языка — нажмите кнопку с соответствующим флагом.\n"
                         "Благодарим вас за использование сервиса автоматического бронирования!",
        'currency': "евро",
        'whatsapp_message': "У меня есть вопрос по поводу моего заказа",
        'whatsapp_footer': "(напишите ниже, что вы хотите выяснить у администратора)",
        'instagram_message': 'Перейти в галерею',
        'return_home': 'Вернуться на страницу входа для следующего заказа',
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
        'delivery_info': "Wenn die Veranstaltungszone innerhalb von Alicante (15-km-Zone) liegt, ist die Lieferung der Ausrüstung kostenlos. "
                         "Wenn weiter entfernt, betragen die Kosten 0,5 Euro pro km.\n"
                         "Verlängerung des Events - 30 Euro pro zusätzliche Stunde.\n"
                         # "Um dem Veranstalter eine Nachricht zu senden und Details zu sehen — wählen Sie im obigen Menü.\n"
                         # "Um die Sprache zu ändern — drücken Sie die Schaltfläche mit der entsprechenden Flagge.\n"
                         "Vielen Dank, dass Sie den automatischen Buchungsservice nutzen!",
        'currency': "Euro",
        'whatsapp_message': "Ich habe eine Frage zu meiner Bestellung",
        'whatsapp_footer': "(Schreiben Sie unten, was Sie den Administrator fragen möchten)",
        'instagram_message': 'Zur Galerie gehen',
        'return_home': 'Zur Startseite zurückkehren für die nächste Bestellung',
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
        'delivery_info': "Si la zona del evento está dentro de Alicante (zona de 15 km), la entrega del equipo es gratuita. "
                         "Si está más lejos, el coste es de 0,5 euros por km.\n"
                         "Extensión del evento: 30 euros por hora adicional.\n"
                         # "Para enviar un mensaje al organizador y ver detalles — seleccione en el menú de arriba.\n"
                         # "Para cambiar el idioma — presione el botón con la bandera correspondiente.\n"
                         "Gracias por utilizar el servicio de reserva automática!",
        'currency': "euros",
        'whatsapp_message': "Tengo una pregunta sobre mi pedido",
        'whatsapp_footer': "(Escriba a continuación lo que desea preguntar al administrador)",
        'instagram_message': 'Ir a la galería',
        'return_home': 'Regresar a la página de inicio para el siguiente pedido',
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
        'delivery_info': "Si la zone de l'événement est à moins de 15 km d'Alicante, la livraison du matériel est gratuite. "
                         "Si c'est plus loin, le coût est de 0,5 euros par km.\n"
                         "Prolongation de l'événement : 30 euros par heure supplémentaire.\n"
                         # "Pour envoyer un message à l'organisateur et voir les détails — sélectionnez dans le menu ci-dessus.\n"
                         # "Pour changer la langue — appuyez sur le bouton avec le drapeau correspondant.\n"
                         "Merci d'utiliser le service de réservation automatique!",
        'currency': "euros",
        'whatsapp_message': "J'ai une question concernant ma commande",
        'whatsapp_footer': "(Écrivez ci-dessous ce que vous souhaitez demander à l'administrateur)",
        'instagram_message': 'Aller à la galerie',
        'return_home': 'Retour à la page d\'accueil pour la prochaine commande',
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
        'delivery_info': "Якщо зона заходу знаходиться в межах Аліканте (зона 15 км), доставка реквізиту безкоштовна. "
                         "Якщо далі, вартість становить 0,5 євро за км.\n"
                         "Продовження заходу - 30 євро за додаткову годину.\n"
                         # "Щоб надіслати повідомлення організатору та переглянути інформацію — виберіть у меню вище.\n"
                         # "Для зміни мови — натисніть кнопку з відповідним прапором.\n"
                         "Дякуємо за використання сервісу автоматичного бронювання!",
        'currency': "євро",
        'whatsapp_message': "У мене є питання щодо мого замовлення",
        'whatsapp_footer': "(Напишіть нижче, що ви хочете дізнатися у адміністратора)",
        'instagram_message': 'Перейти до галереї',
        'return_home': 'Повернутися на головну сторінку для наступного замовлення',
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
        'delivery_info': "Jeśli strefa wydarzenia znajduje się w obrębie Alicante (strefa 15 km), dostawa sprzętu jest bezpłatna. "
                         "Jeśli dalej, koszt wynosi 0,5 euro za km.\n"
                         "Przedłużenie wydarzenia - 30 euro za dodatkową godzinę.\n"
                         # "Aby wysłać wiadomość do organizatora i zobaczyć szczegóły — wybierz z menu powyżej.\n"
                         # "Aby zmienić język — naciśnij przycisk z odpowiednią flagą.\n"
                         "Dziękujemy za korzystanie z usługi automatycznej rezerwacji!",
        'currency': "euro",
        'whatsapp_message': "Mam pytanie dotyczące mojego zamówienia",
        'whatsapp_footer': "(Napisz poniżej, co chcesz zapytać administratora)",
        'instagram_message': 'Ir para a galeria',
        'return_home': 'Voltar para a página inicial para o próximo pedido',
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
        'delivery_info': "Se la zona dell'evento è entro 15 km da Alicante, la consegna dell'attrezzatura è gratuita. "
                         "Se più lontano, il costo è di 0,5 euro per km.\n"
                         "Prolungamento dell'evento - 30 euro per ogni ora aggiuntiva. Pagamento finale - dopo l'evento.\n"
                         # "Per inviare un messaggio all'organizzatore e visualizzare i dettagli — selezionare nel menu sopra.\n"
                         # "Per cambiare la lingua — premere il pulsante con la bandiera corrispondente.\n"
                         "Grazie per aver utilizzato il servizio di prenotazione automatica.",
        'currency': "euro",
        'whatsapp_message': "Ho una domanda sul mio ordine",
        'whatsapp_footer': "(Scrivi qui sotto cosa desideri chiedere all'amministratore)",
        'instagram_message': 'Vai alla galleria',
        'return_home': 'Torna alla pagina iniziale per il prossimo ordine',
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
