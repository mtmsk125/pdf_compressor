import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import hashlib

st.set_page_config(page_title="ضاغط PDF Pro", layout="centered")

st.title("📦 ضاغط ملفات PDF Pro")
st.write("ادفع 5$ مرة وحدة = استخدام مدى الحياة")

GUMROAD_LINK = "https://mtmsk125.gumroad.com/l/uyecq"

# نظام الكود البسيط - انت بتغير الكود هون
VALID_CODES = ["MT2026", "COMPRESS5", "GUMROAD123"]  # غير هاي الأكواد وقت ما بدك

uploaded_file = st.file_uploader("اسحب ملف PDF هون", type="pdf")

if uploaded_file:
    original_size = len(uploaded_file.getvalue()) / 1024 / 1024
    st.info(f"الحجم الأصلي: {original_size:.2f} MB")
    
    # خانة كود التفعيل
    st.subheader("🔑 تفعيل النسخة الكاملة")
    activation_code = st.text_input("أدخل كود التفعيل اللي وصلك بعد الدفع", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**المجاني**")
        st.write("✅ 3 صفحات أولى")
        st.write("✅ علامة مائية")
        if st.button("اضغط مجاناً"):
            # ضغط 3 صفحات فقط
            reader = PdfReader(uploaded_file)
            writer = PdfWriter()
            for i, page in enumerate(reader.pages[:3]):
                page.compress_content_streams()
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            st.download_button("⬇️ نزّل المجاني", output.getvalue(), "compressed_free.pdf")
    
    with col2:
        st.markdown("**النسخة الكاملة 5$**")
        st.write("✅ الملف كامل")
        st.write("✅ بدون علامة مائية")
        st.link_button("🔒 اشتري الكود بـ 5$", GUMROAD_LINK, type="primary")
        
        if st.button("تفعيل واضغط الملف كامل"):
            if activation_code in VALID_CODES:
                st.success("تم التفعيل! جاري الضغط...")
                reader = PdfReader(uploaded_file)
                writer = PdfWriter()
                for page in reader.pages:
                    page.compress_content_streams()
                    writer.add_page(page)
                output = io.BytesIO()
                writer.write(output)
                compressed_size = len(output.getvalue()) / 1024 / 1024
                st.metric("الحجم الجديد", f"{compressed_size:.2f} MB")
                st.download_button("⬇️ نزّل النسخة الكاملة", output.getvalue(), "compressed_pro.pdf")
            else:
                st.error("الكود غلط. اشتري الكود من الرابط فوق")
else:
    st.info("ارفع ملف PDF للبدء")
