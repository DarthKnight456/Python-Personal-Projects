import os
import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from numpy import dot
from numpy.linalg import norm

load_dotenv()

llm = OpenAIEmbeddings(api_key = os.getenv('E_KEY'))


def get_similarity(vector1, vector2):
    cosine_sim = dot(vector1, vector2) / norm(vector1) * norm(vector2)

    return cosine_sim

text1 = input("Enter a sentence: ")
text2 = input("Enter another sentence: ")
vector1 = llm.embed_query(text1)
vector2 = llm.embed_query(text2)

result = get_similarity(vector1, vector2)

print(f"The semantic analysis returns the following value: {result}" )
