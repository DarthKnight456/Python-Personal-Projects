import streamlit as st
from pathlib import Path
from streamlit_pdf_viewer import pdf_viewer





st.set_page_config(page_title= "File Library", page_icon= "📂" )

st.title("File Library")

st.sidebar.header("View Files")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

#for pdf_path in DATA_DIR.glob("*.pdf"):
    #st.write(pdf_path.name)  # e.g., "sample.pdf"
    #st.write(pdf_path)
pdf_names = [file.name for file in DATA_DIR.glob("*.pdf")]
pdf_names.insert(0, "Select a document")
if pdf_names:

# Use in Streamlit dropdown
    selected_pdf_name = st.selectbox("Choose a PDF to view", pdf_names)

    if selected_pdf_name == "Select a document":
        st.warning("View uploaded documents above")

    else:
        selected_pdf_path = DATA_DIR / selected_pdf_name
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Opening document...")
        with st.spinner(f"Loading {selected_pdf_name}..."):
            pdf_viewer(str(selected_pdf_path))
        

        progress_bar.progress(75)
        status_text.text("Almost done...")

        progress_bar.progress(100)
        status_text.text("Done!")
else:
    st.info("No PDFs were found")