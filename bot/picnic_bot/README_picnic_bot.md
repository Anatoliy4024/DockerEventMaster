# TelegramBot_PicnicAlicante

## Версия 6.0 от 20.09.2024

### 1. Описание проекта
Проект **TelegramBot_PicnicAlicante** предназначен для автоматического администрирования и организации ивентов. 
Пользователи взаимодействуют с ботом в Telegram, выбирая дату, время, количество участников, стиль мероприятия
и другие параметры. В результате формируется заказ с возможностью расчета стоимости и бронирования.

### 2. Файловая структура проекта
### Структура директорий и файлов проекта:

```plaintext
picnic_bot/
│
├── media/                              # Медиафайлы, используемые ботом
│   ├── IMG_4077_1 (online-video-cutter.com).mp4
│   ├── IMG_5981 (online-video-cutter.com).mp4
│   ├── IMG_6156 (online-video-cutter.com).mp4
│   ├── IMG_6412 (online-video-cutter.com).mp4
│   └── __init__.py
│
├── __init__.py
├── abstract_functions.py               # Вспомогательные функции для работы с базой данных и выполнения запросов
├── calculations.py                     # Логика расчета стоимости мероприятия
├── calendar_reserve.py                 # Функции для работы с календарем и резервированием дат
├── constants.py                        # Константы и временные данные, используемые в проекте
├── data_reserve.py                     # Управление зарезервированными данными
├── database_logger.py                  # Логирование операций с базой данных
├── db_operations.log                   # Лог-файл для записей событий работы с базой данных
├── keyboards.py                        # Модуль для создания клавиатур для взаимодействия с пользователями
├── main.py                             # Основной файл проекта, запускающий бота и обрабатывающий пользовательские запросы
├── message_handlers.py                 # Модуль для обработки сообщений и команд от пользователей
├── order_info_sender.py                # Логика отправки информации о заказах сервисной службе и администратору
├── README_picnic_bot.md                # Документация проекта

### 3. Архитектура

#### 3.1 Принцип каскадности
В проекте используется принцип каскадности, который разделяет модули на **переменные** и **постоянные** абстракции:
- **Переменные абстракции** — это модули, которые учитывают предпочтения пользователей, позволяя выбирать
 различные опции (например, язык, дата, время).
- **Постоянные абстракции** — это модули, выполняющие однотипные задачи, такие как запросы подтверждения, 
приветствия или ввод имени, а также кнопки "Да" и "Нет".

На момент создания документации (09.09.2024) проект включает:
- Переменных абстракций: **9**
- Постоянных абстракций: **8**

#### 3.2 Перечень модулей и их функций

1. **`language_selection`** (переменный) — выбор языка.
   - Функция: `language_selection_keyboard()`

2. **`greeting`** (постоянный) — приветствие и запрос имени.
   - Функция: `handle_name()`

3. **`date_selection`** (переменный) — выбор даты мероприятия.
   - Функции: `generate_calendar_keyboard()`, `show_calendar()`

4. **`date_confirmation`** (постоянный) — подтверждение даты.
   - Функция: `disable_calendar_buttons()`

5. **`time_selection`** (переменный) — выбор времени мероприятия.
   - Функция: `generate_time_selection_keyboard()`

6. **`time_confirmation`** (постоянный) — подтверждение времени.
   - Функция: `disable_time_buttons()`

7. **`people_selection`** (переменный) — выбор количества участников.
   - Функция: `generate_person_selection_keyboard()`

8. **`people_confirmation`** (постоянный) — подтверждение количества участников.
   - Функция: `disable_person_buttons()`

9. **`style_selection`** (переменный) — выбор стиля мероприятия.
   - Функция: `generate_party_styles_keyboard()`

10. **`style_confirmation`** (постоянный) — подтверждение выбранного стиля.
    - Функция: `disable_style_buttons()`

11. **`preferences_request`** (переменный) — запрос предпочтений пользователя.
    - Функция: `handle_preferences()`

12. **`city_request`** (переменный) — запрос города для проведения мероприятия.
    - Функция: `handle_city()`

13. **`order_calculation`** (переменный) — формирование заказа и расчёт стоимости мероприятия.
    - Функция: `calculate_order_cost()`

14. **`bank_payment`** (переменный) — имитация процесса оплаты и переход к проформе.
    - Функция: `show_payment_page()`

15. **`confirmation_buttons`** (постоянный) — генерация кнопок "Да/Нет" для подтверждения действий.
    - Функция: `generate_confirmation_buttons()`

16. **`proforma_generator`** (переменный) — генерация проформы и возможность её сохранения.
    - Функции: `generate_proforma()`, `save_proforma()`

17. **`final_confirmation_buttons`** (постоянный) — генерация финальных кнопок для завершения или продолжения работы бота.
    - Функция: `generate_final_confirmation_buttons()`

### 4. Нововведения версии 5.0

#### 4.1 Новые модули

1. **`order_info_sender.py`** — отправка информации о заказе Сервисной службе и админу.
   - Назначение: отправка уведомлений о новом заказе.

2. **`calculations.py`** — расчёт стоимости заказа.
   - Назначение: расчёт общей стоимости мероприятия на основе введённых данных.

3. **`abstract_functions.py`** — вспомогательные функции для работы с базой данных.
   - Назначение: создание соединений с базой данных и повторные попытки при ошибках выполнения SQL-запросов.

4. **`proforma_generator.py`** — генерация и сохранение проформы.
   - Назначение: создание проформы на основе данных заказа с возможностью её сохранения.

### 5. Примечания

- В новой версии 5.0 добавлены модули для обработки платежей и создания проформ.
- Улучшена структура работы с языковыми предпочтениями пользователей, оптимизированы функции для взаимодействия с базой данных.
- Логирование и обработка ошибок улучшены для упрощения отладки и мониторинга работы бота.

# 6. Алфавитный указатель всех функций

### A

- **async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE)**  
  Асинхронная функция для обработки нажатий кнопок пользователем. Управляет взаимодействиями с клавиатурами и обновлением данных.

- **async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE)**  
  Логирует ошибки, возникающие в процессе работы бота, и отправляет уведомление пользователю.

- **async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE)**  
  Обрабатывает входящие текстовые сообщения от пользователей в зависимости от текущего шага их сессии.

- **async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE)**  
  Обрабатывает ввод имени пользователя и обновляет его данные в базе данных.

### C

- **create_connection()**  
  Создает соединение с базой данных PostgreSQL. Используется для выполнения запросов к базе данных.

- **calculate_total_cost(duration, people_count)**  
  Выполняет расчет общей стоимости мероприятия на основе длительности и количества участников.

- **create_connection()**  
  Создает соединение с базой данных PostgreSQL.

- **check_if_order_exists(user_id)**  
  Проверяет, существует ли заказ для данного пользователя в базе данных.

### D

- **disable_calendar_buttons(reply_markup, selected_date)**  
  Деактивирует кнопки выбора даты в календаре после того, как пользователь сделал выбор.

- **disable_time_buttons(reply_markup, selected_time)**  
  Деактивирует кнопки выбора времени после того, как пользователь сделал выбор.

- **disable_person_buttons(reply_markup, selected_person)**  
  Деактивирует кнопки выбора количества участников после выбора.

- **disable_style_buttons(reply_markup, selected_style)**  
  Деактивирует кнопки выбора стиля после выбора.

### E

- **execute_query(conn, query, params=())**  
  Выполняет SQL-запрос с логированием выполнения. Применяется для взаимодействия с базой данных.

- **execute_query_with_retry(conn, query, params=(), max_retries=5)**  
  Выполняет SQL-запрос с повторными попытками в случае ошибок базы данных.

### G

- **generate_calendar_keyboard(month_offset=0, language='en')**  
  Генерирует интерактивную клавиатуру для выбора даты мероприятия.

- **generate_time_selection_keyboard(language, time_type, selected_date, start_time=None)**  
  Генерирует интерактивную клавиатуру для выбора времени мероприятия.

- **generate_person_selection_keyboard(language)**  
  Генерирует клавиатуру для выбора количества участников.

- **generate_party_styles_keyboard(language)**  
  Создает клавиатуру для выбора стиля мероприятия.

### H

- **handle_date_selection(update, context)**  
  Обрабатывает выбор даты пользователем и обновляет данные в базе данных.

- **handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE)**  
  Обрабатывает ввод города пользователем.

- **handle_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE)**  
  Обрабатывает ввод предпочтений пользователем для мероприятия.

- **handle_city_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE)**  
  Подтверждение выбора города и переход к расчёту заказа.

### L

- **language_selection_keyboard()**  
  Генерирует клавиатуру для выбора языка пользователем. Поддерживает несколько языков.

### S

- **send_order_info_to_servis(user_id, session_num)**  
  Отправляет информацию о новом заказе сервисной службе через бота.

- **send_message_to_admin(user_id, session_num)**  
  Отправляет информацию о новом заказе администратору (Ирине) через бота.

### T

- **to_superscript(num_str)**  
  Преобразует цифры в строке в верхний индекс (суперскрипт). Используется для форматирования дат в календаре.

### U

- **update_order_data(query, params, user_id)**  
  Обновляет данные заказа в базе данных по запросу и с учетом проверок.

- **user_data_initialization(update: Update, context: ContextTypes.DEFAULT_TYPE)**  
  Инициализирует данные пользователя и его сессию при первом взаимодействии.