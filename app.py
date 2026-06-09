import os
from pdf2image import convert_from_path
from PIL import Image
import io
from flask import Flask, request, send_file, render_template_string
from PyPDF2 import PdfWriter, PdfReader

app = Flask(__name__)

HTML = '''
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>ضغط PDF المصور</title>
<style>
body{font-family:Tahoma;max-width:600px;margin:50px auto;padding:20px;text-align:center;background:#f5f5f5}
.box{background:white;padding:40px;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
input[type=file]{margin:20px 0}
button{background:#4CAF50;color:white;padding:12px 30px;border:none;border-radius:8px;cursor:pointer;font-size:16px}
button:hover{background:#45a049}
</style>
</head>
<body>
<div class="box">
<h2>ضغط ملفات PDF المصورة 📄</h2>
<form method=post enctype=multipart/form-data>
<input type=file name=file accept=.pdf required><br>
<button type=submit>اضغط الملف</button>
</form>
</div>
</body>
</html>
'''

def compress_pdf(input_path, output_path, quality=60, dpi=150):
    images = convert_from_path(input_path, dpi=dpi)
    writer = PdfWriter()

    for img in images:
        img_buffer = io.BytesIO()
        img.convert('RGB').save(img_buffer, format='JPEG', quality=quality, optimize=True)
        img_buffer.seek(0)

        img_pdf = PdfReader(img_buffer)
        writer.add_page(img_pdf.pages[0])

    with open(output_path, 'wb') as f:
        writer.write(f)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        input_path = 'input.pdf'
        output_path = 'compressed.pdf'
        file.save(input_path)

        compress_pdf(input_path, output_path, quality=60, dpi=150)

        os.remove(input_path)
        return send_file(output_path, as_attachment=True, download_name=f'compressed_{file.filename}')

    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
