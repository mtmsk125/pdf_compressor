import os
import fitz
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

HTML = '''
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>ضغط PDF ثابت</title>
<style>
body{font-family:Tahoma;max-width:600px;margin:50px auto;padding:20px;text-align:center;background:#f5f5f5}
.box{background:white;padding:40px;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
input[type=file]{margin:20px 0}
button{background:#2ecc71;color:white;padding:12px 30px;border:none;border-radius:8px;cursor:pointer;font-size:16px;font-weight:bold}
button:hover{background:#27ae60}
.note{color:#7f8c8d;font-size:13px;margin-top:15px}
</style>
</head>
<body>
<div class="box">
<h2>ضغط PDF ثابت ⚙️</h2>
<p>إعداد واحد لكل الملفات</p>
<form method=post enctype=multipart/form-data>
<input type=file name=file accept=.pdf required><br>
<button type=submit>اضغط</button>
</form>
<p class="note">7 ميجا → 3-4 ميجا تقريباً لكل الملفات</p>
</div>
</body>
</html>
'''

def compress_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    # إعداد ثابت لكل الملفات: ضغط متوسط
    doc.save(output_path, deflate=True, garbage=4, clean=True, 
             deflate_images=True, deflate_fonts=True, 
             linear=True)
    doc.close()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        input_path = 'input.pdf'
        output_path = 'compressed.pdf'
        file.save(input_path)
        
        compress_pdf(input_path, output_path)
        
        os.remove(input_path)
        return send_file(output_path, as_attachment=True, download_name=f'compressed_{file.filename}')
    
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
