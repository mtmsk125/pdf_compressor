from flask import Flask, render_template, request, send_file
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
            # ضغط قوي Ghostscript زي Online-Convert
            subprocess.run([
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={output_path}', input_path
            ], check=True, timeout=120)

            size_in = os.path.getsize(input_path) / 1024
            size_out = os.path.getsize(output_path) / 1024
            saved = ((size_in - size_out) / size_in) * 100 if size_in > 0 else 0

            # نستخدم result.html بدل HTML جوا الكود
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
    paths = []
    for f in files:
        path = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
        f.save(path)
        paths.append(path)
    out = os.path.join(UPLOAD_FOLDER, 'merged_falcon.pdf')
    merge_pdf(paths, out)
    return send_file(out, as_attachment=True, download_name='merged.pdf')

@app.route('/split', methods=['POST'])
def split():
    file = request.files['file']
    pages = request.form['pages']
    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)
    out = os.path.join(UPLOAD_FOLDER, 'split_falcon.pdf')
    split_pdf(path, pages, out)
    return send_file(out, as_attachment=True, download_name='split.pdf')

@app.route('/download/<name>')
def download(name):
    return send_file(os.path.join(UPLOAD_FOLDER, name), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    


