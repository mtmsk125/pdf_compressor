import os
from PyPDF2 import PdfReader, PdfWriter
from flask import request, send_file

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def compress_pdf():
    if 'file' not in request.files:
        return "لا يوجد ملف", 400
    
    file = request.files['file']
    if file.filename == '':
        return "لم يتم اختيار ملف", 400
    
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(UPLOAD_FOLDER, 'compressed.pdf')
    
    file.save(input_path)
    
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    return send_file(output_path, as_attachment=True)

def merge_pdf():
    return "قريباً - دمج ملفات PDF", 200

def split_pdf():
    return "قريباً - تقسيم PDF", 200

def pdf_to_word():
    return "قريباً - تحويل PDF لوورد", 200

def word_to_pdf():
    return "قريباً - تحويل وورد لـ PDF", 200
