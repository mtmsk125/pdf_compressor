import os
import time
import tempfile
from pypdf import PdfReader, PdfWriter
from PIL import Image
import io

# في بيئة Vercel Serverless يكون نظام الملفات للقراءة فقط عدا مجلد /tmp
BASE_TEMP = tempfile.gettempdir()
UPLOAD_FOLDER = os.path.join(BASE_TEMP, 'uploads')
COMPRESSED_FOLDER = os.path.join(BASE_TEMP, 'compressed')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def compress_pdf_file(input_path, output_path, quality_level='medium'):
    """ضغط ملف PDF وتقليل حجمه مع الحفاظ على جودته"""
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            for img in page.images:
                try:
                    img_data = img.data
                    image = Image.open(io.BytesIO(img_data))
                    
                    quality = 70 if quality_level == 'high' else (50 if quality_level == 'medium' else 30)
                    output_bytes = io.BytesIO()
                    
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")
                        
                    image.save(output_bytes, format='JPEG', quality=quality, optimize=True)
                    img.replace(image, quality=quality)
                except Exception:
                    continue

            writer.add_page(page)

        for page in writer.pages:
            page.compress_content_streams()

        with open(output_path, 'wb') as f:
            writer.write(f)

        orig_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        
        if new_size >= orig_size and orig_size > 0:
            with open(input_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
            new_size = orig_size

        savings = round(((orig_size - new_size) / orig_size) * 100, 1) if orig_size > 0 else 0
        return True, savings, orig_size, new_size
    except Exception as e:
        return False, str(e), 0, 0

def merge_pdf_files(file_paths, output_path):
    """دمج مجموعة ملفات PDF في ملف واحد"""
    try:
        writer = PdfWriter()
        for path in file_paths:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, 'wb') as f:
            writer.write(f)
        return True, "تم دمج الملفات بنجاح!"
    except Exception as e:
        return False, str(e)

def split_pdf_file(input_path, page_range_str, output_path):
    """تقسيم واستخراج صفحات محددة من الـ PDF"""
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        pages_to_extract = set()
        parts = page_range_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                s, e = map(int, part.split('-'))
                for i in range(max(1, s), min(total_pages, e) + 1):
                    pages_to_extract.add(i - 1)
            elif part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < total_pages:
                    pages_to_extract.add(idx)

        for idx in sorted(list(pages_to_extract)):
            writer.add_page(reader.pages[idx])

        with open(output_path, 'wb') as f:
            writer.write(f)
        return True, f"تم استخراج {len(pages_to_extract)} صفحة بنجاح!"
    except Exception as e:
        return False, str(e)

def protect_pdf_file(input_path, password, output_path):
    """حماية ملف PDF بكلمة سر وتشفيره"""
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(user_password=password, owner_password=password, use_128bit=True)

        with open(output_path, 'wb') as f:
            writer.write(f)
        return True, "تم قفل الملف بكلمة السر بنجاح!"
    except Exception as e:
        return False, str(e)

def images_to_pdf_file(image_paths, output_path):
    """تحويل مجموعة صور لملف PDF واحد"""
    try:
        images = []
        for p in image_paths:
            img = Image.open(p)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)

        if images:
            images[0].save(output_path, save_all=True, append_images=images[1:])
            return True, "تم تحويل الصور إلى PDF بنجاح!"
        return False, "لم يتم اختيار أي صور متوافقة."
    except Exception as e:
        return False, str(e)

def convert_image_to_webp(input_path, output_path, quality=80):
    """تحويل الصور وتصغير حجمها إلى صيغة WebP"""
    try:
        img = Image.open(input_path)
        img.save(output_path, 'WEBP', quality=quality, optimize=True)
        return True, "تم التحويل إلى WebP بنجاح!"
    except Exception as e:
        return False, str(e)

def extract_and_summarize_pdf(input_path):
    """استخراج النصوص من PDF وتلخيص أهم النقاط"""
    try:
        reader = PdfReader(input_path)
        text_content = ""
        for page in reader.pages[:10]:
            text = page.extract_text()
            if text:
                text_content += text + "\n"

        if not text_content.strip():
            return True, "لم يتم العثور على نص عادي قابل للقراءة مباشرة.", []

        lines = [line.strip() for line in text_content.split('\n') if len(line.strip()) > 20]
        summary_points = lines[:7]

        return True, text_content[:1500], summary_points
    except Exception as e:
        return False, str(e), []
