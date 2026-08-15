import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# --- CONFIGURATION ---
CHROMA_PATH = r"chroma_path"  # Your existing Chroma DB folder path
TEST_QUERY = "Montgomery Bus Boycott civil rights 1955"  # Change this to test your edge cases
TOP_K = 5

print("=" * 60)
print(f"🔍 TESTING HYBRID SEARCH ON EXISTING DB: '{CHROMA_PATH}'")
print(f"❓ TEST QUERY: '{TEST_QUERY}'")
print("=" * 60)

# 1. Connect to Existing Raw Chroma Collection
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("E_KEY"), model_name="text-embedding-3-small"
)
raw_collection = chroma_client.get_or_create_collection(
    name="document_collection",
    embedding_function=openai_ef,
    metadata={"hnsw:space": "cosine"},
)

# 2. Extract Existing Chunks for BM25 Keyword Search
all_data = raw_collection.get()
text_chunks = all_data.get("documents", [])
metadatas = all_data.get("metadatas", [])

print(f"📦 Total Chunks Loaded from ChromaDB: {len(text_chunks)}\n")

if not text_chunks:
  print("❌ Error: No document chunks found in ChromaDB. Upload files first!")
  exit()

# Build LangChain Document objects
documents = [
    Document(page_content=text, metadata=meta or {})
    for text, meta in zip(text_chunks, metadatas)
]

# 3. Setup BM25 Sparse Retriever (Keyword Match)
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = TOP_K

# 4. Setup Chroma Vector Retriever (Semantic Match)
lc_embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("E_KEY"), model="text-embedding-3-small"
)
vectorstore = Chroma(
    client=chroma_client,
    collection_name="document_collection",
    embedding_function=lc_embeddings,
)
chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

# 5. Combine both using EnsembleRetriever (RRF)
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, chroma_retriever], weights=[0.5, 0.5]
)

# --- RUN COMPARISON TESTS ---


def print_results(title, docs):
  print(f"\n--- {title} (Top {len(docs)}) ---")
  for i, doc in enumerate(docs, 1):
    source = doc.metadata.get("source", "Unknown")
    page = doc.metadata.get("page", "N/A")
    snippet = doc.page_content.replace("\n", " ")[:120]
    print(f"  {i}. [{source} - Pg {page}] {snippet}...")


# Run queries
bm25_results = bm25_retriever.invoke(TEST_QUERY)
vector_results = chroma_retriever.invoke(TEST_QUERY)
ensemble_results = ensemble_retriever.invoke(TEST_QUERY)

# Display comparisons
print_results("1. BM25 ONLY (Exact Keyword Matching)", bm25_results)
print_results("2. CHROMA VECTOR ONLY (Semantic Similarity)", vector_results)
print_results(
    "3. ENSEMBLE / HYBRID SEARCH (RRF Reranked Combination)", ensemble_results
)

print("\n" + "=" * 60)
print("✅ Test Complete! Check if Ensemble brings up your target document.")
print("=" * 60)