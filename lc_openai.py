from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI
from langchain.chains import ConversationChain

# setup the API key
OPENAI_API_KEY = 'sk-proj-ODkN1IjjLa7rRGuv3eWET3BlbkFJEGipPZ8PlIGx9KzqA6VO'

llm = OpenAI(temperature=0.0, openai_api_key=OPENAI_API_KEY)
conversation = ConversationChain(
    llm=llm,
    verbose=False,
    memory=ConversationBufferMemory()
)

# Setup the prompt question
#from langchain_core.prompts import PromptTemplate
#template = """Question: {question}.
#Answer: Let's think step by step"""
#prompt = PromptTemplate.from_template(template)

# Setup the chain
#llm_chain = prompt | llm

while True:
    question = input("Please input your question here:")
    if question == "exit":
        print("Exiting the application")
    response = conversation.predict(input=question)
    print(f"AI: {response}")
