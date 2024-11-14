-- init.sql
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT,
    status INTEGER,
    number_of_events INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email TEXT,
    registration_email TEXT,
    registration_password TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    session_number INTEGER,
    user_name TEXT,
    language TEXT,
    selected_date TIMESTAMP,
    start_time TIME,
    end_time TIME,
    duration INTEGER,
    people_count INTEGER,
    selected_style TEXT,
    preferences TEXT,
    city TEXT,
    status INTEGER,
    calculated_cost INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
