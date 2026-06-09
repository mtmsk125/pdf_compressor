            file.save(input_path)

            file_size_mb = os.path.getsize(input_path) / (1024 * 1024)

            if file_size_mb <= 30:
                quality = '/ebook'
                quality_msg = 'جودة عالية - مناسب للطباعة'
            else:
                quality = '/screen'
                quality_msg = 'جودة شاشة - تم التقليل عشان الملف كبير'

            try:
                subprocess.run([
                    'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS=' + quality, '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile=' + output_path, input_path
                ], check=True)

                original_size = os.path.getsize(input_path) / (1024 * 1024)
                compressed_size = os.path.getsize(output_path) / (1024 * 1024)
                saved = ((original_size - compressed_size) / original_size) * 100

                return render_template('index.html',
                    filename=output_filename,
                    original_size='%.1f' % original_size,
                    compressed_size='%.1f' % compressed_size,
                    saved='%.0f' % saved,
                    quality_msg=quality_msg)

            except subprocess.CalledProcessError:
                flash('فشل الضغط - جرب ملف أصغر')
                return redirect(request.url)

        else:
            flash('مسموح PDF بس')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(COMPRESSED_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
