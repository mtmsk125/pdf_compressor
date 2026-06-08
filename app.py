from flask import Flask, render_template, request, send_file
from pypdf import PdfReader, PdfWriter
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # حد أقصى 50MB

# أكواد تجريبية - بعدين بنربطها Payoneer
VALID_CODES = {
    'DEMO-5USD': 50,
    'TEST10': 10
}
usage_count = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    code = request.form.get('code', '').strip()

    if code not in VALID_CODES:
        return "كود التفعيل غلط ❌", 400

    if usage_count.get(code, 0) >= VALID_CODES[code]:
        return "خلصت عدد الملفات للكود هاد", 400

    file = request.files['pdf_file']
    if not file or file.filename == '':
        return "ما اخترت ملف", 400

    try:
        reader = PdfReader(file)
        writer = PdfWriter()

        for page in reader.pages:
            page.compress_content_streams() # ضغط الصفحات
            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        usage_count[code] = usage_count.get(code, 0) + 1

        return send_file(
            output,
            download_name=f"compressed_{file.filename}",
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"صار خطأ: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
