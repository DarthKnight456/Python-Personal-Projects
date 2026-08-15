import os
import textwrap
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

# --- LangChain Imports ---
from langchain_classic.retrievers import EnsembleRetriever, BM25Retriever
from langchain_chroma import Chroma
#from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title= "Analyzer Chatbot", page_icon= "🤖" )

st.title("Analyzer Chatbot")


st.sidebar.header("Chatbot")

target_language = st.sidebar.selectbox(
    "Preferred Language:",
    ["English", "Spanish", "French", "German", "Japanese", "Mandarin"]
)

st.sidebar.header("⚙️ Deliverable Configuration")

deliverable_type = st.sidebar.radio(
    "Choose Deliverable Format:",
    options=[
        "📊 Executive Briefing & Strategic Overview",
        "📅 Cross-Document Chronological Timeline",
        "📑 Key Figures, Entities & Metrics Table",
        "⚖️ Comparative Analysis Matrix",
        "🤖 Auto-Detect Best Fit",
    ],
    index=0,
)
FORMAT_DIRECTIVES = {
    "📊 Executive Briefing & Strategic Overview": (
        "Generate an Executive Briefing with an Executive Summary, Key"
        " Findings (bulleted), and Strategic Conclusions."
    ),
    "📅 Cross-Document Chronological Timeline": (
        "Construct a Chronological Timeline in a Markdown table or list"
        " ordered by Date/Year."
    ),
    "📑 Key Figures, Entities & Metrics Table": (
        "Extract key figures, organizations, dates, and quantitative metrics"
        " into summary tables."
    ),
    "⚖️ Comparative Analysis Matrix": (
        "Build a Markdown Comparison Matrix contrasting themes, facts, and"
        " viewpoints across documents."
    ),
    "🤖 Auto-Detect Best Fit": (
        "Analyze the user query and retrieved context to automatically select"
        " and generate the best-fitting structured deliverable."
    ),
}

if "history" not in st.session_state:
    st.session_state.history = []

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


CHROMA_PATH = r"chroma_path"

chroma_client = chromadb.PersistentClient(path = CHROMA_PATH)


def hybrid_retriever():

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key = os.getenv('E_KEY'),
            model_name="text-embedding-3-small"
        )

    collection = chroma_client.get_or_create_collection(name="document_collection", embedding_function= openai_ef, 
            metadata={"hnsw:space": "cosine"} )

    raw_chroma = collection.get()
    texts = raw_chroma.get("documents", [])
    metadatas = raw_chroma.get("metadatas", [])

    if not texts:
        texts = ["No document has been submitted"]
        metadatas = [{}]

    bm25_retriever = BM25Retriever.from_texts(texts=texts, metadatas=metadatas)
    bm25_retriever.k = 5

    langchain_embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv('E_KEY')  # Same API key and model!
    )

    chroma_vectorstore = Chroma(
        client=chroma_client,
        collection_name="document_collection",
        embedding_function= langchain_embeddings
    )

    chroma_retriever = chroma_vectorstore.as_retriever(search_kwargs={"k": 5})

    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.4, 0.6]
    )

    return ensemble_retriever

if user_entry := st.chat_input("What would you like to know?"):
    st.session_state.history.append({"role": "user", "content" : user_entry})
    with st.chat_message("user"):
        st.markdown(user_entry)


    chat_history = st.session_state.get("history", [])


    formatted_history = [
        f"{msg['role'].capitalize()}: {msg['content']}" 
        for msg in chat_history
    ]

    history_string = "\n".join(formatted_history)

    ensemble = hybrid_retriever()
    retrieved_docs = ensemble.invoke(user_entry)

    context_list = []

    for doc in retrieved_docs:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        content = doc.page_content
        context_list.append(f"Source: {source} (Page {page})\nContent: {content}")

    # Join everything into a single string
    final_context = "\n\n---\n\n".join(context_list)


    model = ChatOpenAI(model='gpt-5.4-mini', api_key= os.getenv('R_KEY'), temperature=0.2)

    prompt = textwrap.dedent("""# ROLE & PURPOSE
You are an expert Multilingual Executive Briefing Analyst. Your mission is to synthesize multi-document context chunks into structured, high-value executive deliverables (Executive Briefings, Chronological Timelines, Key Metrics Tables, or Comparative Analysis Matrices), translate them accurately into the target language, and iteratively refine these deliverables through ongoing chat.

# INPUT DATA STRUCTURE
For every task, you will receive:
1. DELIVERABLE & TRANSLATION CONFIGURATION: Target output format and target output language.
2. PAST CONVERSATION HISTORY: Prior turns containing previous deliverables and user edit requests.
3. DOCUMENT CONTEXT: Text chunks retrieved across the uploaded PDF library.
4. METADATA: Source document titles, file names, page numbers, and chunk identifiers.
5. VECTOR DISTANCES: Cosine similarity scores indicating document relevance.

# CORE RESPONSIBILITIES & EXECUTION RULES

1. CONTINUAL REFINEMENT & ON-TOPIC FOLLOW-UPS
- Treat follow-up questions as instructions to refine, expand, modify, or update the existing deliverable.
- Continuously evaluate past conversation history alongside newly retrieved document chunks to seamlessly edit details, add missing facts, or restructure sections without dropping context.
- Ensure all follow-up responses remain strictly on-topic, tethered to the uploaded documents and the evolving deliverable.

2. AUTOMATIC DELIVERABLE SELECTION
- If a specific deliverable format is provided in the configuration, strictly follow its directive.
- AUTOMATIC FALLBACK: If NO specific deliverable format is selected or if the configuration is blank/ambiguous, analyze the user's intent and context chunks to automatically select and generate the best-fit deliverable format (e.g., Timeline for chronological queries, Matrix for comparisons, Briefing for broad overviews).

3. MULTILINGUAL SYNTHESIS & TRANSLATION
- Translate all generated insights, briefs, and timelines directly into the requested TARGET OUTPUT LANGUAGE.
- Perform cross-lingual synthesis: seamlessly process source text chunks regardless of whether they are in English or another language, and unify them in the output language.
- Provide a side-by-side dual comparison of the document in the output language and the original language ONLY if explicitly requested by the user.
- TERMINOLOGY PRESERVATION: When translating key proper nouns, legal terms, or technical names from source documents, preserve the original term in brackets next to the translation (e.g., "Federal Council [Bundesrat]").

4. STRUCTURED DELIVERABLES OVER CONVERSATIONAL FILLER
- Do NOT act as a pure conversational chat partner. Clearly and concisely redirect the focus if an off-topic conversational prompt is given.
- Focus entirely on delivering structured, production-ready briefings using clear Markdown headers, bullet points, and data tables.
- Synthesize implicit themes, logical connections, and overarching patterns across all uploaded documents rather than expecting exact keyword matches.
- State clearly that relevant information is unavailable ONLY if the retrieved chunks have zero thematic or factual connection to the request.

5. METADATA & EXACT SOURCE CITATION
- Every key insight, fact, timeline event, or extracted metric MUST be explicitly cited with its source document name and page number (e.g., [Document Name, Page X]).
- Draw information evenly across all provided document sources to prevent single-document bias.

6. VECTOR DISTANCE INTERPRETATION
- Use provided vector distances internally to prioritize higher-relevance chunks (scores closer to 0.0).
- CRITICAL RULE: NEVER display, explain, or discuss raw vector distances or cosine scores in the final output unless the user explicitly requests a technical retrieval analysis.

7. ACTIONABLE NEXT STEPS
- Conclude every deliverable with a dedicated section titled "### Recommended Follow-Up Analytical Actions" containing 2 to 3 high-value next steps based on gaps or key themes in the document set.

# OUTPUT STYLE & TONE
- Professional, objective, executive-level, and formatted for rapid scanning.
- No conversational filler (e.g., avoid "Sure, I can help with that!", "Here is your updated briefing:"). 
- Jump straight into the title and structured content.""").strip()

    user_payload = textwrap.dedent(f"""
        Below is the relevant context from uploaded documents, past chat history, and the user's current question.
        === DELIVERABLE CONFIGURATION ===
        Target Output Language: {target_language}
        Deliverable Selected: {deliverable_type}
        Deliverable Directive: {FORMAT_DIRECTIVES[deliverable_type]}

        === PAST CHAT HISTORY ===
        {history_string}

        === RETRIEVED DOCUMENT CONTEXT & METADATA ===
        {final_context}


        === CURRENT USER QUESTION ===
        {user_entry}

       
    """).strip()

    messages = [
        SystemMessage(content= prompt),
        HumanMessage(content=user_payload)
                ]

    response = model.invoke(messages)
    with st.chat_message("assistant"):
        st.markdown(response.content)
    st.session_state.history.append({"role":"assistant", "content": response.content})
    st.rerun()

