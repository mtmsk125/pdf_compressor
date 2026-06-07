import os
import io
import fitz
from PIL import Image
import uuid
import json
from flask import Flask, request, send_file, render_template, jsonify

app = Flask(__name__)
DB_FILE = "users_db.json"

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
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    file = request.files['pdf']
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    output = fitz.open()

    for i in range(min(3, len(doc))):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
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
    db = load_db()
    
    if code == 'DEMO-5USD':
        user_id = str(uuid.uuid4())
        db[user_id] = {'files_left': 50, 'plan': 'starter'}
        save_db(db)
        return jsonify({'status': 'ok', 'files_left': 50})
    
    return jsonify({'status': 'error', 'msg': 'كود غير صحيح'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
