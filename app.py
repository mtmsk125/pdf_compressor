@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return "اختر ملف", 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(UPLOAD_FOLDER, 'falcon_' + filename)
        file.save(input_path)

        try:
            subprocess.run([
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={output_path}', input_path
            ], check=True, timeout=180)

            size_in = os.path.getsize(input_path) / 1024
            size_out = os.path.getsize(output_path) / 1024
            saved = ((size_in - size_out) / size_in) * 100 if size_in > 0 else 0

            # هاي السطر لازم يكون داخل try ومع 4 مسافات اندنت
            return render_template('result.html',
                orig_size=f"{size_in:.2f}",
                comp_size=f"{size_out:.2f}",
                saved=f"{saved:.2f}",
                filename='falcon_' + filename)

        except Exception as e:
            return f"خطأ بالضغط: {str(e)}", 500

    # هاي السطر لازم يكون برا الـ if وبنفس مستوى الدالة
    return render_template('index.html')

