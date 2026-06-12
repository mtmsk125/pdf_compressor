import subprocess
import os
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret-key-123'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB سقف المجاني

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_pdf(input_path, output_path):
    # Ghostscript مباشرة - أخف شي عالرام 60MB بس
    cmd = [
        'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dQUIET', '-dBATCH',
        f'-sOutputFile={output_path}', input_path
    ]
    subprocess.run(cmd, check=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ما اخترت ملف')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('ما اخترت ملف')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed_' + filename)

            file.save(input_path)

            try:
                compress_pdf(input_path, output_path)
                return send_file(output_path, as_attachment=True, download_name='compressed_' + filename)
            except Exception as e:
                flash(f'صار خطأ أثناء الضغط: {str(e)}')
                return redirect(request.url)
        else:
            flash('نوع الملف غير مدعوم. ارفع PDF فقط')
            return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
       
