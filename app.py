from flask import Flask, render_template, request, send_file, jsonify
import os
import subprocess
import uuid
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB حد أقصى
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# دالة الضغط الذكية - 40MB → 25MB
def compress_pdf(input_path, output_path):
    try:
        cmd = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/screen', # ضغط قوي
            '-dColorImageResolution=100', # 100 DPI = سرعة + حجم صغير
            '-dGrayImageResolution=100',
            '-dMonoImageResolution=300',
            '-dColorImageDownsampleType=/Bicubic',
            '-dGrayImageDownsampleType=/Bicubic',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ]

        # 25 ثانية بس عشان Render المجاني ما يقتله
        subprocess.run(cmd, check=True, timeout=25)
        return True

    except subprocess.TimeoutExpired:
        print("Timeout: الملف كبير زيادة، استخدم /ebook")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# دالة الدمج
def merge_pdfs(files, output_path):
    writer = PdfWriter()
    for file in files:
        reader = PdfReader(file)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, 'wb') as f:
        writer.write(f)

# دالة الفصل
def split_pdf(input_path, pages_str, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    pages = []
    for part in pages_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start-1, end))
        else:
            pages.append(int(part)-1)

    for p in pages:
        if 0 <= p < len(reader.pages):
            writer.add_page(reader.pages[p])

    with open(output_path, 'wb') as f:
        writer.write(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    if 'file' not in request.files:
        return jsonify({'error': 'لا يوجد ملف'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400

    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())[:8]
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{filename}")
    output_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{filename}")

    file.save(input_path)

    if compress_pdf(input_path, output_path):
        os.remove(input_path)
        return send_file(output_path, as_attachment=True)
    else:
        os.remove(input_path)
        return jsonify({'error': 'فشل الضغط - الملف كبير زيادة'}), 500

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('files')
    if len(files) < 2:
        return jsonify({'error': 'اختار ملفين على الأقل'}), 400

    output_path = os.path.join(COMPRESSED_FOLDER, f"merged_{uuid.uuid4()[:8]}.pdf")
    temp_files = []

    for file in files:
        temp_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(temp_path)
        temp_files.append(temp_path)

    merge_pdfs(temp_files, output_path)

    for f in temp_files:
        os.remove(f)

    return send_file(output_path, as_attachment=True)

@app.route('/split', methods=['POST'])
def split():
    if 'file' not in request.files or 'pages' not in request.form:
        return jsonify({'error': 'ملف أو صفحات ناقصة'}), 400

    file = request.files['file']
    pages = request.form['pages']

    input_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    output_path = os.path.join(COMPRESSED_FOLDER, f"split_{uuid.uuid4()[:8]}.pdf")

    file.save(input_path)
    split_pdf(input_path, pages, output_path)
    os.remove(input_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
   
