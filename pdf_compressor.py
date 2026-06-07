import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(page_title="ضاغط PDF Pro", layout="centered")

st.title("📦 ضاغط ملفات PDF Pro")
st.write("ادفع 5$ مرة وحدة = استخدام مدى الحياة")

GUMROAD_LINK = "https://mtmsk125.gumroad.com/l/uyecq"

# الأكواد اللي انت بتتحكم فيها
VALID_CODES = ["MT2026", "COMPRESS5", "GUMROAD123"]

uploaded_file = st.file_uploader("اسحب ملف PDF هون", type="pdf")

if uploaded_file:
    original_size = len(uploaded_file.getvalue()) / 1024 / 1024
    st.info(f"الحجم الأصلي: {original_size:.2f} MB")
    
    # خانة كود التفعيل
    st.subheader("🔑 تفعيل النسخة الكاملة")
    activation_code = st.text_input("أدخل كود التفع
    
