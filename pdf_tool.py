import os
from flask import request, render_template, send_file, redirect, url_for
import pikepdf

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def compress_pdf():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return redirect(request.url)
        
        file = request.files['pdf_file']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            input_path = os.path.join(UPLOAD_FOLDER, 'input.pdf')
            output_path = os.path.join(UPLOAD_FOLDER, 'compressed.pdf')
            file.save(input_path)
            
            try:
                # ضغط قوي باستخدام pikepdf
                with pikepdf.open(input_path) as pdf:
                    pdf.save(output_path, compression_level=9)
                
                return send_file(output_path, as_attachment=True, download_name='compressed.pdf')
            except Exception as e:
                return f"خطأ بالضغط: {str(e)}"
    
    # صفحة الرفع
    return '''
    <h2>ضغط PDF</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="pdf_file" accept=".pdf" required>
        <button type="submit">اضغط الملف</button>
    </form>
    <br><a href="/">رجوع للرئيسية</a>
    '''

def merge_pdf():
    return "<h2>دمج PDF</h2><p>قريباً...</p><a href='/'>رجوع</a>"

def split_pdf():
    return "<h2>تقسيم PDF</h2><p>قريباً...</p><a href='/'>رجوع</a>"

def pdf_to_word():
    return "<h2>PDF الى Word</h2><p>قريباً...</p><a href='/'>رجوع</a>"

def word_to_pdf():
    return "<h2>Word الى PDF</h2><p>قريباً...</p><a href='/'>رجوع</a>"
