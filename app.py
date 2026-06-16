from flask import Flask, render_template, request, send_file, redirect
import os, subprocess
from werkzeug.utils import secure_filename
from pdf_tools import merge_pdf, split_pdf

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024 # 200MB

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return "اختر ملف", 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(UPLOAD_FOLDER, 'falcon_' + filename)
        file.save(input_path)

        try:
            subprocess.run([
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={output_path}', input_path
            ], check=True, timeout=180)

            size_in = os.path.getsize(input_path) / 1024
            size_out = os.path.getsize(output_path) / 1024
            saved = ((size_in - size_out) / size_in) * 100 if size_in > 0 else 0

            return render_template('result.html',
                orig_size=f"{size_in:.2f}",
                comp_size=f"{size_out:.2f}",
                saved=f"{saved:.2f}",
                filename='falcon_' + filename)

        except Exception as e:
            return f"خطأ بالضغط: {str(e)}", 500

    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('files')
    if len(files) < 2:
        return "ارفع ملفين على الأقل للدمج", 400

    paths = []
    for f in files:
        if f and f.filename.endswith('.pdf'):
            path = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
            f.save(path)
            paths.append(path)

    if not paths:
        return "لا يوجد ملفات PDF صالحة", 400

    out = os.path.join(UPLOAD_FOLDER, 'merged_falcon.pdf')
    merge_pdf(paths, out)
    return send_file(out, as_attachment=True, download_name='merged_falcon.pdf')

@app.route('/split', methods=['POST'])
def split():
    file = request.files.get('file')
    pages = request.form.get('pages', '')

    if not file or not pages:
        return "اختر ملف واكتب أرقام الصفحات", 400

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    out = os.path.join(UPLOAD_FOLDER, 'split_falcon.pdf')
    try:
        split_pdf(path, pages, out)
        return send_file(out, as_attachment=True, download_name='split_falcon.pdf')
    except Exception as e:
        return f"خطأ بالفصل: {str(e)} - تأكد من صيغة الصفحات: 1-3,5", 400

@app.route('/download/<name>')
def download(name):
    return send_file(os.path.join(UPLOAD_FOLDER, name), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)

