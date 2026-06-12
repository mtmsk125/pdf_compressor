from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import fitz # PyMuPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50MB

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    # شلنا linear=True عشان pymupdf الجديدة
    doc.save(output_path, deflate=True, garbage=4, clean=True,
             deflate_images=True, deflate_fonts=True)
    doc.close()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
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
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_path = os.path.join(COMPRESSED_FOLDER, 'compressed_' + filename)

            file.save(input_path)

            try:
                compress_pdf(input_path, output_path)
                return send_file(output_path, as_attachment=True)
            except Exception as e:
                flash(f'صار خطأ: {str(e)}')
                return redirect(request.url)
            finally:
                if os.path.exists(input_path):
                    os.remove(input_path)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
