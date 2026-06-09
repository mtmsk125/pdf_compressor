from flask import Flask, render_template, request, send_file
import os
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf/compress', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return "ما في ملف", 400
    
    file = request.files['file']
    if file.filename == '':
        return "ما اخترت ملف", 400
    
    if file and file.filename.endswith('.pdf'):
        # اسم ملف مؤقت
        input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + '.pdf')
        output_path = os.path.join(COMPRESSED_FOLDER, 'compressed_' + file.filename)
        
        file.save(input_path)
        
        # ضغط باستخدام ghostscript
