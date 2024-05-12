import asyncpg
import os
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Configure logging to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set handler level to INFO

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)

# Set the logging level of the logger to INFO
logger.setLevel(logging.INFO)

# global variable
pool = None


async def create_db_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
        logger.info("Database connection established")
    else:
        logger.info("Using existing database connection pool.")

    # Test database connection
    async with pool.acquire() as conn:
        await conn.execute("SELECT 1")


# Create a new user or update an existing one
async def ensure_user_exists(user_data):
    """
    Creates a new user profile or updates an existing one
    :param user_data:
    :return:
    """
    schema = "staging" if os.getenv("ENV") == "dev" else "public"
    global pool

    if not pool:  # Check if the pool has been initialized
        await create_db_pool()
    async with pool.acquire() as conn:
        # check if user exists
        user_exists = await conn.fetchval(
            f"SELECT EXISTS(SELECT 1 FROM {schema}.users WHERE telegram_id = $1)", user_data[
                "id"]
        )
        if not user_exists:
            # Create a new user with UUID generation
            await conn.execute(
                f"""
                  INSERT INTO {schema}.users (user_id, telegram_id, is_bot, first_name, username, language_code, is_premium)
                      VALUES (uuid_generate_v4(), $1, $2, $3, $4, $5, $6)""",
                user_data["id"],
                user_data["is_bot"],
                user_data["first_name"],
                user_data["username"],
                user_data["language_code"],
                user_data["is_premium"],
            )
            print("User created with new UUID.")
        else:
            # Update existing user (if needed)
            await conn.execute(
                f"""
                  UPDATE {schema}.users SET first_name = $1, username = $2, language_code = $3, is_premium = $4 WHERE telegram_id = $5""",
                user_data["first_name"],
                user_data["username"],
                user_data["language_code"],
                user_data["is_premium"],
                user_data["id"],
            )
            print("User updated.")
