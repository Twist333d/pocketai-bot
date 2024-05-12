-- Insert into users table
INSERT INTO public.users (telegram_id, user_id, is_bot, first_name, username, language_code, is_premium, last_active)
VALUES (123456789, uuid_generate_v4(), FALSE, 'John', 'john_doe', 'en', FALSE, now());

-- Insert into conversations table
INSERT INTO public.conversations (conversation_id, user_id, start_time, conversation_status)
VALUES (uuid_generate_v4(), (SELECT user_id FROM public.users WHERE username='john_doe'), now(), 'active');

-- Insert into messages table
INSERT INTO public.messages (message_uuid, message_id, user_id, conversation_id, message_timestamp, sender_type)
VALUES (uuid_generate_v4(), 1, (SELECT user_id FROM public.users WHERE username='john_doe'), (SELECT conversation_id FROM public.conversations WHERE user_id=(SELECT user_id FROM public.users WHERE username='john_doe')), now(), 'user');
