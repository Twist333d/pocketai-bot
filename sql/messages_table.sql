CREATE TYPE public.sender_types AS ENUM ('bot', 'user');

CREATE TABLE public.messages(
    message_uuid UUID PRIMARY KEY,
    message_id BIGINT,
    user_id UUID NOT NULL REFERENCES public.users(user_id),
    conversation_id UUID NOT NULL REFERENCES public.conversations(conversation_id),
    message_timestamp TIMESTAMP WITH TIME ZONE,
    sender_type public.sender_types
                            );

CREATE TYPE staging.sender_types AS ENUM ('bot', 'user');

CREATE TABLE staging.messages(
    message_uuid UUID PRIMARY KEY,
    message_id BIGINT,
    user_id UUID NOT NULL REFERENCES staging.users(user_id),
    conversation_id UUID NOT NULL REFERENCES public.conversations(conversation_id),
    message_timestamp TIMESTAMP WITH TIME ZONE,
    sender_type staging.sender_types
                            )