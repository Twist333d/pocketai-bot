from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain


async def setup_llm_conversation(llm):
    """
    Sets the conversation class from langchain.
    :param llm: llm class from langchain
    :return: conversation class from langchain
    """
    conversation = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(),
        verbose=False)
    return conversation


async def get_llm_response(conversation, user_input):
    """
    Gets response from user input from langchain llm.
    :param user_input: user message extracted from telegram
    :return: returns a response from llm
    """
    response = await conversation.ainvoke(user_input)
    return response["response"]
