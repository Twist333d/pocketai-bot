from groq import AsyncGroq
import logging

GROQ_API_KEY = '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'


# Setup the client
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

logger = logging.getLogger(__name__)


# Send responses
async def query_groq_api(message):
    try:
        response = await groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": message}
            ],
            model="llama3-70b-8192",  # Choose the model as per your requirement
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("Failed to query groq api due to: %s", str(e))
        raise e

