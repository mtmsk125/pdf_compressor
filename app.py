import os
import fitz
from flask import Flask, request, send_file, render_template_string, session, redirect
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # سر للجلسات عشان العداد

# هون حط إيميل PayPal تبعك
PAYPAL_EMAIL = "حط_ايميلك_هون@gmail.com"

HTML = '''
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>ضغط PDF + كل الأدوات مدى الحياة</title>
<style>
body{font-family:Tahoma;background:#0f172a;color:#fff;margin:0;padding:20px}
.box{max-width:800px;margin:auto}

.founder{background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#000;padding:30px 20px;border-radius:15px;text-align:center;margin-bottom:30px;box-shadow:0 10px 30px rgba(251,191,36,0.3)}
.founder h1{margin:0 0 10px;font-size:28px}
.founder p{margin:5px 0;font-size:16px}
.counter{font-size:48px;font-weight:bold;margin:15px 0}
.btn{background:#10b981;color:#fff;border:none;padding:16px 40px;border-radius:10px;cursor:pointer;font-size:18px;font-weight:bold;transition:0.2s}
.btn:hover{background:#059669;transform:scale(1.02)}
.btn.founder-btn{background:#000;color:#fbbf24;font-size:20px;padding:18px 50px}

.compress-box{background:white;color:#000;padding:40px;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.2);text-align:center;margin-bottom:30px}
.compress-box h2{margin-top:0;color:#1e293b}
input[type=file]{margin:20px 0;padding:10px;border:2px dashed #ccc;border-radius:8px;width:80%}
.btn-compress{background:#2ecc71;color:white;padding:14px 40px;border:none;border-radius:8px;cursor:pointer;font-size:18px;font-weight:bold;width:100%}
.btn-compress:hover{background:#27ae60}
.btn-compress:disabled{background:#95a5a6;cursor:not-allowed}
.note{color:#7f8c8d;font-size:13px;margin-top:15px}
.usage{color:#fbbf24;font-weight:bold;font-size:14px;margin-bottom:15px}

.tools-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:30px}
.tool-card{background:#1e293b;padding:20px;border-radius:12px;border:2px solid #334155;text-align:center}
.tool-card.premium{border-color:#fbbf24}
.tool-card h3{margin:0 0 8px;font-size:16px}
.badge{background:#fbbf24;color:#000;padding:3px 8px;border-radius:5px;font-size:11px}
.price{font-size:22px;color:#10b981;font-weight:bold;margin:8px 0}
.btn-small{background:#10b981;color:#fff;border:none;padding:10px;width:100%;border-radius:8px;cursor:pointer;font-size:14px;font-weight:bold}
.btn-small:hover{background:#059669}

.locked-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);display:flex;align-items:center;justify-content:center;z-index:999}
.locked-box{background:#1e293b;padding:50px;border-radius:20px;text-align:center;max-width:500px}
</style>
</head>
<body>
<div class="box">

<!-- باقة المؤس 75$ -->
<div class="founder">
<h1>👑 باقة المؤس مدى الحياة</h1>
<p>كل الأدوات العادية + كل أدوات AI للأبد</p>
<p>دفع مرة وحدة وانسى الاشتراكات</p>
<div class="counter" id="founderLeft">{{founder_left}}</div>
<p style="font-size:14px">مقعد متبقي من 100</p>
<button class="btn founder-btn" onclick="payFounder()">اشترك الآن 75$ مرة وحدة</button>
</div>

<!-- أداة الضغط -->
<div class="compress-box">
<h2>ضغط PDF ثابت ⚙️</h2>
{% if locked %}
<p style="color:#ef4444;font-weight:bold;font-size:18px">🔒 خلصت محاولاتك المجانية</p>
<p>اشترك مدى الحياة عشان تكمل</p>
<button class="btn" onclick="payFounder()">اشترك 75$</button>
{% else %}
<p class="usage">جربت {{count}} من 10 ملفات مجانية</p>
<p>إعداد واحد لكل الملفات</p>
<form method=post enctype=multipart/form-data>
<input type=file name=file accept=.pdf required><br>
<button class="btn-compress" type=submit>اضغط</button>
</form>
<p class="note">7 ميجا → 3-4 ميجا تقريباً</p>
{% endif %}
</div>

<!-- باقي الأدوات -->
<h2 style="text-align:center;color:#fbbf24;margin-top:40px">⚡ باقي الأدوات مدى الحياة</h2>
<div class="tools-grid">
  <div class="tool-card premium">
    <h3><span class="badge">AI</span> تلخيص PDF</h3>
    <div class="price">3$</div>
    <button class="btn-small" onclick="payTool('AI تلخيص', 3)">اشترك 3$</button>
  </div>
  <div class="tool-card premium">
    <h3><span class="badge">AI</span> محادثة مع PDF</h3>
    <div class="price">3$</div>
    <button class="btn-small" onclick="payTool('محادثة PDF', 3)">اشترك 3$</button>
  </div>
  <div class="tool-card">
    <h3>دمج PDF</h3>
    <div class="price">1$</div>
    <button class="btn-small" onclick="payTool('دمج PDF', 1)">اشترك 1$</button>
  </div>
  <div class="tool-card">
    <h3>PDF → Word</h3>
    <div class="price">1$</div>
    <button class="btn-small" onclick="payTool('PDF to Word', 1)">اشترك 1$</button>
  </div>
  <div class="tool-card">
    <h3>فصل PDF</h3>
    <div class="price">1$</div>
    <button class="btn-small" onclick="payTool('فصل PDF', 1)">اشترك 1$</button>
  </div>
  <div class="tool-card">
    <h3>حذف صفحات</h3>
    <div class="price">1$</div>
    <button class="btn-small" onclick="payTool('حذف صفحات', 1)">اشترك 1$</button>
  </div>
</div>

</div>

<script>
const PAYPAL_EMAIL = "{{paypal_email}}";

function payFounder(){
window.open(`https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=${PAYPAL_EMAIL}&item_name=مؤس+مدى+الحياة+كل+الأدوات&amount=75&currency_code=USD`,'_blank');
}

function payTool(name, price){
window.open(`https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=${PAYPAL_EMAIL}&item_name=${name}+مدى+الحياة&amount=${price}&currency_code=USD`,'_blank');
}
</script>
</body>
</html>
'''

def compress_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    doc.save(output_path, deflate=True, garbage=4, clean=True, 
             deflate_images=True, deflate_fonts=True, linear=True)
    doc.close()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # عداد الجلسة
    if 'count' not in session:
        session['count'] = 0
    if 'license' not in session:
        session['license'] = False
    
    locked = False
    # لو وصل 10 وما عنده ليسن
    if session['count'] >= 10 and not session['license']:
        locked = True
    
    if request.method == 'POST':
        if locked:
            return redirect('/')
        
        file = request.files['file']
        input_path = 'input.pdf'
        output_path = 'compressed.pdf'
        file.save(input_path)
        
        compress_pdf(input_path, output_path)
        
        os.remove(input_path)
        session['count'] += 1  # زيد العداد
        
        return send_file(output_path, as_attachment=True, download_name=f'compressed_{file.filename}')
    
    founder_left = max(0, 100 - session.get('count', 0))  # رقم وهمي للـ FOMO
    return render_template_string(HTML, 
        count=session['count'],
        locked=locked,
        founder_left=founder_left,
        paypal_email=PAYPAL_EMAIL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
