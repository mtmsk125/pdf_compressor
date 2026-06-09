import os
import subprocess
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey' # ضروري للـ flash messages

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('ما في ملف مرفوع')
            return redirect(request.url)

        file = request.files['pdf_file']
        if file.filename == '':
            flash('ما اخترت ملف')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_filename = 'compressed_' + filename
            output_path = os.path.join(COMPRESSED_FOLDER, output_filename)

            file.save(input_path)

            # === التعديل الذكي: اختيار الجودة حسب الحجم ===
            file_size_mb = os.path.getsize(input_path) / (1024 * 1024)

            if file_size_mb <= 30:
                quality = '/ebook' # جودة عالية للطباعة
                quality_msg = 'جودة عالية - مناسب للطباعة'
            else:
                quality = '/screen' # جودة شاشة للملفات الكبيرة
                quality_msg = 'جودة شاشة - تم التقليل عشان الملف كبير'

            try:
                subprocess.run([
                    'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    f'-dPDFSETTINGS={quality}', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    f'-sOutputFile={output_path}', input_path
                ], check=True)

                original_size = os.path.getsize(input_path) / (1024 * 1024)
                compressed_size = os.path.getsize(output_path) / (1024 * 1024)
                saved = ((original_size - compressed_size) / original_size) * 100

                return render_template('index.html',
                    filename=output_filename,
                    original
