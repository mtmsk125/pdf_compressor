from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os, subprocess, threading, time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

compression_time = 0

def do_compress(input_path, temp_path, output_path):
    global compression_time
    start = time.time()
    try:
        # مرحلة 1: ضغط خفيف DPI 150 عشان ما يقع السيرفر
        subprocess.run([
            'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dQUIET', '-dBATCH',
            '-dColorImageResolution=150', f'-sOutputFile={temp_path}', input_path
        ], check=True)
        
        # مرحلة 2: ضغط قوي DPI 100
        subprocess.run([
            'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
            '-dColorImageResolution=100', f'-sOutputFile={output_path}', temp_path
        ], check=True)
        
        os.remove(temp_path)
        compression_time = round(time.time() - start, 2)
    except Exception as e:
        compression_time = -1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{filename}')
    output_path = os.path.join(COMPRESSED_FOLDER, f'compressed_{filename}')
    file.save(input_path)
    
    # شغل الضغط بالخلفية وارجع صفحة التحميل فوراً
    thread = threading.Thread(target=do_compress, args=(input_path, temp_path, output_path))
    thread.start()
    
    return render_template('processing.html', filename=filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(COMPRESSED_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
