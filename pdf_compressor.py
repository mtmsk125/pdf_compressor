import os
import io
import fitz # PyMuPDF
from PIL import Image
import uuid
import json
from flask import Flask, request, send_file, render_template_string, jsonify

app = Flask(__name__)

# ملف لتخزين الأكواد والعداد - بسيط للبداية
DB_FILE = "users_db.json"

# HTML كامل مع صفحة الأسعار الجديدة
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF Compressor Pro - ضغط PDF مدى الحياة 5$</title>
<style>
    body { font-family: 'Tahoma', sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }
   .container { max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
    h1 { color: #2c3e50; text-align: center; }
   .pricing { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }
   .plan { border: 2px solid #ddd; border-radius: 12px; padding: 25px; text-align: center; transition: 0.3s; }
   .plan:hover { border-color: #3498db; transform: translateY(-5px); }
   .plan.popular { border-color: #e74c3c; position: relative; }
   .badge { position: absolute; top: -12px; right: 20px; background: #e74c3c; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; }
   .price { font-size: 40px; color: #2c3e50; font-weight: bold; margin: 15px 0; }
   .price span { font-size: 16px; color: #7f8c8d; }
    button { background: #3498db; color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; }
    button:hover { background: #2980b9; }
   .compress-box { background: #ecf0f1; padding: 25px; border-radius: 10px; margin-top: 30px; }
    input[type=file] { margin: 15px 0; }
    #result { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 8px; display: none; }
   .counter { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center; }
</style>
</head>
<body>
<div class="container">
    <h1>📦 PDF Compressor Pro</h1>
    <p style="text-align:center; color:#7f8c8d">اضغط ملفات PDF 70% بدون ما تخرب الجودة. جرّب 3 صفحات مجاناً</p>

    <div class="pricing">
        <div class="plan">
            <h3>جرّب مجاناً</h3>
            <div class="price">0$<span>/للأبد</span></div>
            <p>✓ 3 صفحات لكل ملف<br>✓ علامة مائية صغيرة<br>✓ بدون تسجيل</p>
            <button onclick="scrollToCompress()">ابدأ الضغط</button>
        </div>

        <div class="plan popular">
            <span class="badge">الأكثر مبيعاً</span>
            <h3>Lifetime Starter</h3>
            <div class="price">5$<span> مرة وحدة</span></div>
            <p>✓ 50 ملف كامل مدى الحياة<br>✓ بدون علامة مائية<br>✓ سرعة أولوية<br>✓ أرخص من سندويشة</p>
            <button onclick="buyPlan('starter')">اشتري الآن</button>
        </div>

        <div class="plan">
            <h3>Lifetime Pro</h3>
            <div class="price">14.99$<span> مرة وحدة</span></div>
            <p>✓ ملفات غير محدودة<br>✓ بدون علامة مائية<br>✓ API للمطورين<br>✓ دعم 24/7</p>
            <button onclick="buyPlan('pro')">اشتري الآن</button>
        </div>
    </div>

    <div class="compress-box" id="compress">
        <h3>ارفع ملف PDF للتجربة المجانية</h3>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="pdf" accept=".pdf" required>
            <button type="submit">اضغط 3 صفحات مجاناً</button>
        </form>
        <div id="result"></div>
    </div>
</div>

<script>
document.getElementById('uploadForm').onsubmit = async (e) => {
    e.preventDefault();
    let formData = new FormData(e.target);
    let res = await fetch('/compress', {method: 'POST', body: formData});
    let data = await res.json();
    document.getElementById('result').style.display = 'block';
    document.getElementById('result').innerHTML = `
        <b>النتيجة:</b><br>
        الحجم قبل: ${data.before} MB<br>
        الحجم بعد: ${data.after} MB<br>
        نسبة الضغط: ${data.ratio}%<br>
        <a href="${data.download}">نزّل الملف المضغوط</a>
    `;
};

function scrollToCompress() {
    document.getElementById('compress').scrollIntoView({behavior: 'smooth'});
}

function buyPlan(plan) {
    // هون بنحط رابط الدفع Payoneer/Stripe لاحقاً
    alert('الدفع رح يتفعل لما تربط Payoneer. هسا انسخ الكود: LIFETIME-' + plan.toUpperCase() + '-DEMO');
}
</script>
</body>
</html>
"""

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/compress', methods=['POST'])
def compress():
    file = request.files['pdf']
    pdf_bytes = file.read()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    output = fitz.open()

    # نضغط أول 3 صفحات بس للتجربة المجانية
    for i in range(min(3, len(doc))):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # ضغط متوسط
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_byte = io.BytesIO()
        img.save(img_byte, format='JPEG', quality=70)
        new_page = output.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_byte.getvalue())

    output_bytes = io.BytesIO()
    output.save(output_bytes)
    output.close()
    doc.close()

    before = len(pdf_bytes) / 1024 / 1024
    after = output_bytes.tell() / 1024 / 1024
    ratio = round((1 - after/before) * 100, 1)

    # حفظ الملف مؤقتاً
    filename = f"compressed_{uuid.uuid4().hex[:8]}.pdf"
    with open(filename, 'wb') as f:
        f.write(output_bytes.getvalue())

    return jsonify({
        'before': round(before, 2),
        'after': round(after, 2),
        'ratio': ratio,
        'download': f'/download/{filename}'
    })

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

@app.route('/activate', methods=['POST'])
def activate():
    code = request.json.get('code')
    # هون بنتحقق من الكود ونعطيه 50 ملف
    db = load_db()
    db[code] = {'files_left': 50, 'plan': 'starter'}
    save_db(db)
    return jsonify({'status': 'ok', 'files_left': 50})

if __name__ == '__main__':
    app.run(debug=True)
