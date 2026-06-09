            file.save(input_path)

            # === التعديل الذكي: اختيار الجودة حسب الحجم ===
            file_size_mb = os.path.getsize(input_path) / (1024 * 1024)

            if file_size_mb <= 30:
                quality = '/ebook' # جودة عالية للطباعة
                quality_msg = 'جودة عالية - مناسب للطباعة'
            else:
                quality = '/screen' # جودة شاشة للملفات الكبيرة
                quality_msg = 'جودة شاشة - تم التقليل عشان الملف كبير'

            try:
                subprocess.run([
                    'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    f'-dPDFSETTINGS={quality}', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    f'-sOutputFile={output_path}', input_path
                ], check=True)

                original_size = os.path.getsize(input_path) / (1024 * 1024)
                compressed_size = os.path.getsize(output_path) / (1024 * 1024)
                saved = ((original_size - compressed_size) / original_size) * 100

                return render_template('index.html',
                    filename=output_filename,
                    original
