import io
import os
from langchain_core import messages
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pypdf import PdfReader
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
st.title("PDF Input Test")

output_language = st.text_input("Enter the language you want to translate the text to (e.g., French, Spanish, German):")

uploaded_file = st.file_uploader("Upload a PDF file")

if uploaded_file is None:
    st.warning("Please upload a PDF file.")
    st.stop()

reader = PdfReader(uploaded_file)
text = reader.pages[0].extract_text()

#bytes_data = uploaded_file.getvalue()
#st.write(bytes_data)

#stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
#st.write(stringio)

#string_data = stringio.read()
#st.write(string_data)

#dataframe = pd.read_csv(uploaded_file)
#st.write(dataframe)



send = st.button("Send to OpenAI")

if send:
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("SECRET_KEY"))
    template = f"You are a helpful assistant that translates text to {output_language}. Translate the following text to {output_language}:\n\n{{text}}"  
    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("user", "{text}")
    ])
    chain = prompt | llm
    result = chain.invoke({"output_language": output_language, "text": text})
    st.write(result.content)