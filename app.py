import os
import fitz  # PyMuPDF
from PIL import Image
import io
from flask import Flask, request, send_file, render_template_string

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
button{background:#e74c3c;color:white;padding:12px 30px;border:none;border-radius:8px;cursor:pointer;font-size:16px;font-weight:bold}
button:hover{background:#c0392b}
.note{color:#e74c3c;font-size:13px;margin-top:15px}
</style>
</head>
<body>
<div class="box">
<h2>ضغط PDF المصور بقوة 🔥</h2>
<p>للملفات الممسوحة سكانر</p>
<form method=post enctype=multipart/form-data>
<input type=file name=file accept=.pdf required><br>
<button type=submit>اضغط الملف</button>
</form>
<p class="note">ملاحظة: جودة الصور رح تقل شوي بس الحجم رح ينزل 70-80%</p>
</div>
</body>
</html>
'''

def compress_pdf(input_path, output_path, quality=40, dpi=100):
    doc = fitz.open(input_path)
    new_doc = fitz.open()
    
    for page in doc:
        # نحول الصفحة لصورة بدقة 100 DPI
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # نحول لـ JPEG بجودة 40% + أبيض وأسود لو الصفحة نصية
        img_buffer = io.BytesIO()
        img.convert('L').save(img_buffer, format="JPEG", quality=quality, optimize=True)
        img_buffer.seek(0)
        
        rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(rect, stream=img_buffer.read())
    
    new_doc.save(output_path, deflate=True, garbage=4, clean=True)
    doc.close()
    new_doc.close()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        input_path = 'input.pdf'
        output_path = 'compressed.pdf'
        file.save(input_path)
        
        # ضغط قوي: quality 40 + dpi 100
        compress_pdf(input_path, output_path, quality=40, dpi=100)
        
        os.remove(input_path)
        return send_file(output_path, as_attachment=True, download_name=f'compressed_{file.filename}')
    
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
