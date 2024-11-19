--- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT,
    status INTEGER,
    number_of_events INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email TEXT,
    registration_email TEXT,
    registration_passw TEXT
);

-- Таблица заказов
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,  -- SERIAL используется для автоинкремента
    user_id BIGINT,
    session_number INTEGER,  -- Номер сессии
    user_name TEXT,  -- Имя пользователя
    language TEXT,  -- Язык
    selected_date TIMESTAMP,
    start_time TIME,  -- Время начала в формате TIME
    end_time TIME,  -- Время окончания в формате TIME
    duration INTEGER,
    people_count INTEGER,
    selected_style TEXT,
    preferences TEXT,
    city TEXT,
    status INTEGER,
    calculated_cost INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(user_id)  -- Внешний ключ
);
