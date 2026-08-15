import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from langchain_community.document_loaders import PyMuPDFLoader
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
import uuid





load_dotenv()

st.set_page_config(page_title= "File Upload", page_icon= "📄" )

st.markdown("File Upload")
st.sidebar.header("File Upload")

st.title("PDF Upload")


uploaded_files = st.file_uploader("Upload a PDF file", accept_multiple_files= True )

upload_file = st.button("Upload File")

st.warning("The loader doesn't accept other file formats and scanned image PDFs won't work")

if uploaded_files is None:
    st.warning("Please upload a PDF file.")
    st.stop()


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = str(DATA_DIR)
CHROMA_PATH = r"chroma_path"


if upload_file:

    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Starting upload...")

    saved_file_paths = []

    for file in uploaded_files:
        file_path = DATA_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        saved_file_paths.append(file_path)
   

    progress_bar.progress(25)
    status_text.text("Files saved! Loading PDFs...")

    documents = []
    for path in saved_file_paths:
        loader = PyMuPDFLoader(str(path))
        documents.extend(loader.load())

    progress_bar.progress(50)
    status_text.text("PDFs loaded! Chunking text...")

    
    chroma_client = chromadb.PersistentClient(path = CHROMA_PATH)

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key = os.getenv('E_KEY'),
        model_name="text-embedding-3-small"
    )

    collection = chroma_client.get_or_create_collection(name="document_collection", embedding_function= openai_ef )

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, length_function = len,  is_separator_regex=False,)

    chunks = text_splitter.split_documents(documents)


    progress_bar.progress(75)
    status_text.text("Text chunked! Sending to ChromaDB...")

    chunks_text = []
    ids = []
    metadata = []
  

    for chunk in chunks:
        sid = uuid.uuid4()
        unique_id = str(sid)

        chunks_text.append(chunk.page_content)
        ids.append(unique_id)
        metadata.append(chunk.metadata)

        

    collection.upsert(
        documents=chunks_text,
        ids= ids,
        metadatas=metadata

    )
    progress_bar.progress(100)
    status_text.text("Processing complete!")
    st.success("Successfully processed and indexed all files!")
    st.toast("Files saved!", icon="🚀")
    












