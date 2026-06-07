import streamlit as st
import os
import subprocess
import tempfile
from pathlib import Path

st.set_page_config(page_title="PDF Compressor Pro", page_icon="🗜️", layout="centered")

st.title("🗜️ PDF Compressor Pro")
st.markdown("اضغط أي PDF من 200MB إلى 5MB بنفس الجودة. مجاني لأول 3 ملفات يومياً")

if 'compress_count' not in st.session_state:
    st.session_state.compress_count = 0

uploaded_file = st.file_uploader("ارفع ملف PDF", type="pdf")

if uploaded_file is not None:
    if st.session_state.compress_count >= 3:
        st.warning("خلصت الضغط المجاني اليوم 🔒 اشترك عشان ضغط غير محدود")
        st.link_button("اشترك بـ $5/شهر", "https://gumroad.com", type="primary")
        st.stop()
    
    with st.spinner("جاري الضغط... 15-30 ثانية"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
            tmp_input.write(uploaded_file.getvalue())
            input_path = tmp_input.name
        
        output_path = input_path.replace(".pdf", "_compressed.pdf")
        
        gs_command = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ]
        
        try:
            subprocess.run(gs_command, check=True, timeout=60)
            
            original_size = os.path.getsize(input_path) / (1024*1024)
            compressed_size = os.path.getsize(output_path) / (1024*1024)
            saved = ((original_size - compressed_size) / original_size) * 100
            
            st.success(f"تم! من {original_size:.1f}MB إلى {compressed_size:.1f}MB")
            col1, col2, col3 = st.columns(3)
            col1.metric("الأصلي", f"{original_size:.1f}MB")
            col2.metric("بعد الضغط", f"{compressed_size:.1f}MB")
            col3.metric("التوفير", f"{saved:.0f}%")
            
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ نزل الملف المضغوط",
                    data=f,
                    file_name=f"compressed_{uploaded_file.name}",
                    mime="application/pdf",
                    type="primary"
                )
            
            st.session_state.compress_count += 1
            st.info(f"باقي لك {3 - st.session_state.compress_count} ضغط مجاني اليوم")
                
        except Exception as e:
            st.error("صار خطأ. جرب ملف أقل من 500MB")
        
        os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

st.markdown("---")
st.caption("صنع بواسطة QuantX Tools")
