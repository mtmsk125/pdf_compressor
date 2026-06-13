from flask import Flask, render_template, request, send_file, redirect
import subprocess
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "compressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# الحد الأقصى 100 ميجابايت
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
        return redirect("/")

    file = request.files["pdf_file"]

    if file.filename == "":
        return redirect("/")

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

    except subprocess.CalledProcessError as e:
        return f"خطأ أثناء الضغط: {e}"

    except Exception as e:
        return f"خطأ: {e}"

    finally:

        if os.path.exists(input_path):
            os.remove(input_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port
    )
