import chromadb
import os
import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from numpy import dot
from numpy.linalg import norm
import chromadb.utils.embedding_functions as embedding_functions


load_dotenv()

import chromadb
chroma_client = chromadb.Client()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key = os.getenv('E_KEY'),
    model_name="text-embedding-3-small"
)

collection = chroma_client.create_collection(name="text_collection", embedding_function= openai_ef, metadata={"hnsw:space": "cosine"} )



text1 = """The James Webb Space Telescope (JWST), launched in December 2021, represents a monumental leap in infrared astronomy. 
Located at the second Lagrange point (L2) approximately 1.5 million kilometers from Earth, JWST uses a primary mirror composed of 18 hexagonal segments made of gold-plated beryllium. 
By detecting light in the infrared spectrum, the observatory can look back over 13.5 billion years to observe the formation of the first stars and galaxies after the Big Bang. 
Its primary instruments must be kept at ultra-cold operating temperatures below 40 Kelvin (-233°C) using a five-layer tennis-court-sized sunshield to prevent thermal radiation from interfering with cosmic readings.
"""

text2 = """Offshore wind farms harness oceanic winds to generate renewable electricity at significantly higher capacities than land-based turbines. 
Because sea winds are stronger and much more consistent, marine wind farms can produce high energy yields with lower atmospheric turbulence. 
Engineers deploy two main structural types: fixed-bottom foundations for shallow coastal waters up to 60 meters deep, and floating platform systems anchored by mooring lines for deepwater ocean installations. 
High-voltage direct current (HVDC) subsea cables then transmit the captured electrical power back to onshore substations, minimizing power dissipation across long nautical distances."""

collection.add(
    ids=["t1", "t2"],
    documents= [text1, text2]
)

info = input("What would you like to know? ")
number = int(input("How many results do you want? "))



results = collection.query(
    query_texts=[info], # Chroma will embed this for you
    n_results= number # how many results to return
)
print(results)