import os
from langchain_core import messages
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model = "gpt-4o-mini", api_key = os.getenv('SECRET_KEY'))

human_template = "{question}"

prompt_template = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name = "history"),(
            "human" , human_template 
        )
    ],

)

chain = prompt_template | llm

store = {}

def get_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

full_chain = RunnableWithMessageHistory(
    chain, 
    get_session_id,
    input_messages_key= "question",
    history_messages_key= "history",
    output_messages_key= "output"
)

while True:
    question = input("You: ")
    result = full_chain.invoke({"question": question}, config = {"configurable": {"session_id" : "foo"}})
    print(result.content)
    if question == "quit":
        print("Left chat")
        break