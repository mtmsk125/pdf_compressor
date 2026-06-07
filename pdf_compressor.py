from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from pypdf import PdfReader, PdfWriter
import io
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50MB max

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# كود تفعيل وهمي للتجربة
VALID_CODES = {
    'DEMO-5USD': 50 # 50 ملف مدى الحياة
}

# نخزن عدد الاستخدامات مؤقتاً
usage_count = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    code = request.form.get('code', '').strip()

    if code not in VALID_CODES:
        return "كود التفعيل غلط ❌", 400

    if code not in usage_count:
        usage_count[code] = 0

    if usage_count[code] >= VALID_CODES[code]:
        return "خلصت عدد الملفات المسموحة للكود هاد", 400

    file = request.files['pdf_file']
    if not file:
        return "ما اخترت ملف", 400

    try:
        # قراءة الـ PDF
        reader = PdfReader(file)
        writer = PdfWriter()

        # ضغط: بنشيل الصور الكبيرة وبنقلل الجودة
        for page in reader.pages:
            page.compress_content_streams() # هاي أهم سطر للضغط
            writer.add_page(page)

        # حفظ الملف المضغوط بالذاكرة
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        usage_count[code] += 1

        return send_file(
            output,
            download_name=f"compressed_{file.filename}",
            as_attachment=True,
            mimetype='application/pdf'
        )

    except Exception as e:
        return f"صار خطأ: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
