import asyncpg
import os


async def create_db_pool():
    return await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))


# get user conversation
async def get_user_conversation(pool, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow()
        return row["conversation_state"] if row else None


# update user conversation
async def save_user_conversation(pool, user_id):
    async with pool.acquire() as conn:
        await conn.execute(
            """ 
            INSERT INTO user_conversations (user_id, conversation_state) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET conversation_state = $2""",
            user_id,
            state,
        )
