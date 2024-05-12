-- Create ENUM for status
CREATE TYPE public.status_type AS ENUM ('active', 'ended');

CREATE TABLE public.conversations(
    conversation_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(user_id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP  WITH TIME ZONE,
    conversation_status public.status_type
);

-- Create ENUM for status
CREATE TYPE staging.status_type AS ENUM ('active', 'ended');

CREATE TABLE staging.conversations(
    conversation_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES staging.users(user_id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP  WITH TIME ZONE,
    conversation_status staging.status_type
)