import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="PDF Analyzer", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 100%);
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .hero-card {
        background: linear-gradient(135deg, #0f4c81 0%, #2f80ed 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        box-shadow: 0 8px 24px rgba(15, 76, 129, 0.25);
        margin-bottom: 1.5rem;
    }
    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        height: 100%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .sidebar .block-container {
        background: #f8fafc;
        border-radius: 14px;
    }
    .nav-heading {
        font-size: 1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.success("Select a page above")

"""page = st.sidebar.radio(
    "Sections",
    ["Home", "Upload Files", "Chatbot", "View Files"],
    index=0,
    label_visibility="collapsed",
)"""

#if page != "Home":
    #st.sidebar.info(f"{page} is styled as a dedicated section for your future page design.")

st.markdown(
    """
    <div class="hero-card">
        <h1 style="margin-bottom: 0.3rem;">PDF Analyzer</h1>
        <p style="margin: 0; font-size: 1.05rem; opacity: 0.95;">
            Explore your uploaded documents with a clean, modern experience designed for quick understanding and easy navigation.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="font-size: 1.05rem; color: #334155; margin-bottom: 1rem;">
        This main page introduces the app with a polished overview and guides you toward the key areas of the experience.
    </p>
    """,
    unsafe_allow_html=True,
)

cols = st.columns(3)
features = [
    ("📤", "Upload Files", "Add your PDFs to begin organizing and analyzing your content."),
    ("🤖", "Chatbot", "Start conversations around the document content in a simple, focused workspace."),
    ("📂", "View Files", "Review uploaded documents at a glance with a tidy and structured layout."),
]

for col, (icon, title, description) in zip(cols, features):
    with col:
        st.markdown(
            f"""
            <div class="feature-card">
                <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">{icon}</div>
                <h4 style="margin: 0 0 0.25rem 0; color: #0f172a;">{title}</h4>
                <p style="margin: 0; color: #475569;">{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("")
