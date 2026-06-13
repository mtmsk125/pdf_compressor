سأعطيك نسخة محسنة من الكود الحالي تعالج أهم المشاكل:

* تحديد حجم الملفات المرفوعة.
* التحقق من أن الملف PDF.
* إضافة مهلة زمنية لـ Ghostscript.
* معالجة الأخطاء.
* حذف الملفات المؤقتة دائماً.
* حذف الملف المضغوط بعد إرساله للمستخدم.
* استخدام إعداد ضغط أفضل.

```python
from flask import Flask, render_template, request, send_file, redirect
import subprocess
import tempfile
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "compressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# الحد الأقصى لحجم الملف (100MB)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


def compress_pdf(input_pdf, output_pdf):
    subprocess.run(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_pdf}",
            input_pdf,
        ],
        check=True,
        timeout=180,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compress", methods=["POST"])
def compress():

    if "pdf_file" not in request.files:
        return "لم يتم اختيار ملف"

    file = request.files["pdf_file"]

    if file.filename == "":
        return "لم يتم اختيار ملف"

    if not file.filename.lower().endswith(".pdf"):
        return "يسمح فقط بملفات PDF"

    uid = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{uid}.pdf"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"{uid}_compressed.pdf"
    )

    try:
        file.save(input_path)

        compress_pdf(input_path, output_path)

        response = send_file(
            output_path,
            as_attachment=True,
            download_name="compressed.pdf"
        )

        return response

    except subprocess.TimeoutExpired:
        return "انتهت مهلة الضغط، الملف كبير جداً"

    except subprocess.CalledProcessError:
        return "حدث خطأ أثناء ضغط الملف"

    except Exception as e:
        return f"خطأ: {str(e)}"

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

        # حذف الملفات المضغوطة القديمة
        try:
            for file_name in os.listdir(OUTPUT_FOLDER):
                file_path = os.path.join(
                    OUTPUT_FOLDER,
                    file_name
                )

                if os.path.isfile(file_path):
                    age = (
                        os.path.getmtime(file_path)
                    )

                    if (
                        age
                        < (
                            __import__("time").time()
                            - 3600
                        )
                    ):
                        os.remove(file_path)

        except:
            pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
```

لكن إذا كان هدفك دعم ملفات كبيرة (200MB–1GB) فلا أنصح بـ Render المجاني إطلاقاً. الأفضل إعادة بناء الخدمة باستخدام **FastAPI + Background Workers** لأن Flask الحالي سيبقى يعاني من التهنيج والتوقف عند الملفات الكبيرة أو كثرة المستخدمين.

