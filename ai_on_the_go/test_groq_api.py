from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import logging
import asyncio

GROQ_API_KEY = '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'

# Setup the client
chat = ChatGroq(temperature=0.0, groq_api_key=GROQ_API_KEY, model_name='llama3-70b-8192')

# Initialize an llm
conversation = ConversationChain(
    llm=chat,
    memory=ConversationBufferMemory(),
    verbose=False,
)

async def chat_with_llama():
    while True:
        user_input = input("Please input your message: ")
        if user_input == 'quit':
            print("Good bye!")
            break
        else:
            response = await conversation.ainvoke(user_input)
            print(response['response'])

chat_with_llama()