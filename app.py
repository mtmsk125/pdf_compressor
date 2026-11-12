from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify, Response
from werkzeug.utils import secure_filename
import os, time
from pdf_engine import (
    compress_pdf_file, merge_pdf_files, split_pdf_file,
    protect_pdf_file, images_to_pdf_file, convert_image_to_webp,
    extract_and_summarize_pdf, UPLOAD_FOLDER, COMPRESSED_FOLDER
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max

@app.route('/tools')
def browser_tools():
    """Client-side PDF tools that avoid sending document contents to Flask."""
    return render_template('tools.html')

@app.route('/image_tools')
def image_tools():
    """Client-side image tools; image contents stay in the user's browser."""
    return render_template('image_tools.html')

@app.route('/text_tools')
def text_tools():
    """Client-side text tools; text stays in the user's browser."""
    return render_template('text_tools.html')

@app.route('/google211db57d92a6b10e.html')
def google_site_verification():
    """Serve the Google Search Console HTML verification token."""
    return Response('google-site-verification: google211db57d92a6b10e.html', mimetype='text/html')

@app.route('/sitemap.xml')
def sitemap():
    """Generate an XML sitemap for the public site pages."""
    public_endpoints = ['index', 'browser_tools', 'image_tools', 'text_tools', 'privacy', 'terms', 'about', 'contact', 'blog']
    urls = ''.join(
        f'<url><loc>{url_for(endpoint, _external=True)}</loc></url>'
        for endpoint in public_endpoints
    )
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' \
          f'{urls}</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots_txt():
    """Allow crawling and advertise the sitemap location."""
    sitemap_url = url_for('sitemap', _external=True)
    return Response(f'User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n', mimetype='text/plain')

@app.route('/')
def index():
    ref = request.args.get('ref', '')
    return render_template('index.html', ref=ref)

@app.route('/compress', methods=['POST'])
def compress():
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(url_for('index'))

    file = request.files['file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_filename = f"compressed_{filename}"
    output_path = os.path.join(COMPRESSED_FOLDER, output_filename)
    
    file.save(input_path)
    success, savings, orig_size, new_size = compress_pdf_file(input_path, output_path)

    return render_template('download.html', filename=output_filename, savings=savings)

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return redirect(url_for('index'))

    saved_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        saved_paths.append(path)

    output_filename = f"merged_{int(time.time())}.pdf"
    output_path = os.path.join(COMPRESSED_FOLDER, output_filename)
    
    success, msg = merge_pdf_files(saved_paths, output_path)
    return render_template('download.html', filename=output_filename, message=msg)

@app.route('/split', methods=['POST'])
def split():
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(url_for('index'))

    file = request.files['file']
    pages = request.form.get('pages', '1')
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_filename = f"split_{filename}"
    output_path = os.path.join(COMPRESSED_FOLDER, output_filename)

    file.save(input_path)
    success, msg = split_pdf_file(input_path, pages, output_path)
    return render_template('download.html', filename=output_filename, message=msg)

@app.route('/protect', methods=['POST'])
def protect():
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(url_for('index'))

    file = request.files['file']
    password = request.form.get('password', '123456')
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_filename = f"protected_{filename}"
    output_path = os.path.join(COMPRESSED_FOLDER, output_filename)

    file.save(input_path)
    success, msg = protect_pdf_file(input_path, password, output_path)
    return render_template('download.html', filename=output_filename, message=msg)

@app.route('/img2pdf', methods=['POST'])
def img2pdf():
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return redirect(url_for('index'))

    saved_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        saved_paths.append(path)

    output_filename = f"images_{int(time.time())}.pdf"
    output_path = os.path.join(COMPRESSED_FOLDER, output_filename)

    success, msg = images_to_pdf_file(saved_paths, output_path)
    return render_template('download.html', filename=output_filename, message=msg)

@app.route('/img2webp', methods=['POST'])
def img2webp():
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(url_for('index'))

    file = request.files['file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    base_name = os.path.splitext(filename)[0]
    output_filename = f"{base_name}.webp"
    output_path = os.path.join(COMPRESSED_FOLDER, output_filename)

    file.save(input_path)
    success, msg = convert_image_to_webp(input_path, output_path)
    return render_template('download.html', filename=output_filename, message=msg)

@app.route('/ocr', methods=['POST'])
@app.route('/summarize', methods=['POST'])
def ocr_summarize():
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(url_for('index'))

    file = request.files['file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    success, preview_text, points = extract_and_summarize_pdf(input_path)
    msg = f"تم التلخيص واستخراج النصوص بنجاح!\n\nأهم النقاط:\n- " + "\n- ".join(points) if points else "تم المعالجة بنجاح!"

    return render_template('download.html', filename=filename, message=msg)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(COMPRESSED_FOLDER, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return redirect(url_for('index'))

# AdSense Compliance Pages
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
