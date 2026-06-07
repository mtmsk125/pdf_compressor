import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(page_title="PDF Compressor Pro", layout="centered")
st.title("PDF Compressor Pro")
st.write("Pay 5$ once = lifetime access")

GUMROAD_LINK = "https://mtmsk125.gumroad.com/l/uyecq"
VALID_CODES = ["MT2026", "COMPRESS5", "GUMROAD123"]

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    original_size = len(uploaded_file.getvalue()) / 1024 / 1024
    st.info(f"Original: {original_size:.2f} MB")
    activation_code = st.text_input("Enter code", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Free - 3 pages")
        if st.button("Compress Free"):
            reader = PdfReader(uploaded_file)
            writer = PdfWriter()
            for page in reader.pages[:3]:
                writer.add_page(page)
                writer.pages[-1].compress_content_streams()
            output = io.BytesIO()
            writer.write(output)
            st.download_button("Download Free", output.getvalue(), "free.pdf")
    
    with col2:
        st.write("Full 5$")
        st.link_button("Buy", GUMROAD_LINK)
        if st.button("Activate Full"):
            if activation_code in VALID_CODES:
                reader = PdfReader(uploaded_file)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                    writer.pages[-1].compress_content_streams()
                output = io.BytesIO()
                writer.write(output)
                st.download_button("Download Full", output.getvalue(), "full.pdf")
            else:
                st.error("Wrong code")
