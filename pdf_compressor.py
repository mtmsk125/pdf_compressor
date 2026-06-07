
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
    
