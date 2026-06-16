from flask import Flask, request, send_file
import os, subprocess
from werkzeug.utils import secure_filename
from pdf_tools import merge_pdf, split_pdf

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if not file or file.filename == '':
            return "اختر ملف", 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(UPLOAD_FOLDER, 'falcon_' + filename)
        file.save(input_path)

        try:
            # ضغط قوي Ghostscript
            subprocess.run([
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={output_path}', input_path
            ], check=True, timeout=120)

            size_in = os.path.getsize(input_path) / 1024
            size_out = os.path.getsize(output_path) / 1024
            saved = ((size_in - size_out) / size_in) * 100

            return f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="utf-8">
            <title>تم - Falcon</title><style>body{{background:#0a0f1e;color:#e2e8f0;
            font-family:tahoma;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}}
           .box{{background:#1e293b;padding:40px;border-radius:20px;border:2px solid #fbbf24;text-align:center}}
            h1{{color:#fbbf24}}.btn{{background:#22c55e;color:white;padding:15px 40px;border-radius:10px;
            text-decoration:none;display:inline-block;margin-top:20px;font-weight:bold}}</style></head>
            <body><div class="box"><h1>✅ تم ضغط الملف</h1>
            <p>قبل: {size_in:.0f} KB | بعد: {size_out:.0f} KB</p>
            <p style="font-size:28px;color:#22c55e;font-weight:bold">وفرت {saved:.1f}%</p>
            <a href="/download/falcon_{filename}" class="btn">تحميل الملف</a></div></body></html>'''
        except:
            return "فشل الضغط", 500

    return open('templates/index.html', encoding='utf-8').read()

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('files')
    paths = [os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)) for f in files]
    for f, p in zip(files, paths): f.save(p)
    out = os.path.join(UPLOAD_FOLDER, 'merged_falcon.pdf')
    merge_pdf(paths, out)
    return send_file(out, as_attachment=True)

@app.route('/split', methods=['POST'])
def split():
    file = request.files['file']
    pages = request.form['pages']
    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)
    out = os.path.join(UPLOAD_FOLDER, 'split_falcon.pdf')
    split_pdf(path, pages, out)
    return send_file(out, as_attachment=True)

@app.route('/download/<name>')
def download(name):
    return send_file(os.path.join(UPLOAD_FOLDER, name), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

      
    


