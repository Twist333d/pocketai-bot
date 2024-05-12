CREATE TABLE public.users(
    telegram_id BIGINT PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    is_bot BOOLEAN NOT NULL,
    first_name VARCHAR(255),
    username VARCHAR(255) UNIQUE,
    language_code VARCHAR(10),
    is_premium BOOLEAN,
    last_active TIMESTAMP WITH TIME ZONE
);

CREATE TABLE staging.users(
    telegram_id BIGINT PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    is_bot BOOLEAN NOT NULL,
    first_name VARCHAR(255),
    username VARCHAR(255) UNIQUE,
    language_code VARCHAR(10),
    is_premium BOOLEAN,
    last_active TIMESTAMP WITH TIME ZONE
)