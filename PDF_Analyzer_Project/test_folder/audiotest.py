import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
from playsound3 import playsound
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

client = OpenAI(api_key = os.getenv('SECRET_KEY'))

language = input("Enter the language you want to translate the text to (e.g., French, Spanish, German): ")  
question = input("Enter the question you want to ask: ")


completion = client.chat.completions.create(
    model="gpt-audio-mini",
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "mp3"},
    messages=[
        {
            "role": "system",
            "content": f" You are a translator, always translate the following question in {language} and respond in {language}. Don't use any other language "
        },

        {
            "role": "user",
            "content": question
        }
    ]
)

audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
with open("question.mp3", "wb") as f:
    f.write(audio_bytes)
    playsound("question.mp3")
