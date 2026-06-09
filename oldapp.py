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
