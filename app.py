import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
app.secret_key = 'secret-key-change-me'

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_pdf(input_path, output_path, quality='screen'):
    gs_command = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS=/{quality}',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path
    ]
    try:
        subprocess.run(gs_command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لا يوجد ملف')
            return redirect(request.url)

        file = request.files['file']
        quality = request.form.get('quality', 'screen')

        if file.filename == '':
            flash('لم يتم اختيار ملف')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_filename = f'compressed_{filename}'
            output_path = os.path.join(app.config['COMPRESSED_FOLDER'], output_filename)

            file.save(input_path)

            if compress_pdf(input_path, output_path, quality):
                original_size = os.path.getsize(input_path) / (1024 * 1024)
                compressed_size = os.path.getsize(output_path) / (1024 * 1024)
                saved = ((original_size - compressed_size) / original_size) * 100

                return render_template('index.html',
                                     filename=output_filename,
                                     original_size='%.2f' % original_size,
                                     compressed_size='%.2f' % compressed_size,
                                     saved='%.0f' % saved)
            else:
                flash('فشل ضغط الملف')
                return redirect(request.url)
        else:
            flash('PDF فقط مسموح')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['COMPRESSED_FOLDER'], filename), as_attachment=True)

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
