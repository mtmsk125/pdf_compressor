from flask import Flask, render_template, request, send_file
import subprocess
import os
import uuid
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "compressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


# 🎯 اختيار مستوى الضغط
def get_pdfsettings(level):
    if level == "low":
        return "/ebook"
    elif level == "medium":
        return "/screen"
    elif level == "high":
        return "/screen"
    return "/ebook"


def compress_pdf(input_pdf, output_pdf, level="medium"):

    pdfset = get_pdfsettings(level)

    result = subprocess.run(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={pdfset}",

            "-dDetectDuplicateImages=true",
            "-dCompressFonts=true",

            "-dDownsampleColorImages=true",
            "-dDownsampleGrayImages=true",
            "-dDownsampleMonoImages=true",

            "-dColorImageResolution=120",
            "-dGrayImageResolution=120",
            "-dMonoImageResolution=120",

            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",

            f"-sOutputFile={output_pdf}",
            input_pdf,
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode != 0:
        raise Exception(result.stderr)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compress", methods=["POST"])
def compress():

    files = request.files.getlist("file")
    level = request.form.get("level", "medium")

    output_files = []

    for file in files:
        if file.filename == "":
            continue

        uid = str(uuid.uuid4())

        input_path = os.path.join(UPLOAD_FOLDER, uid + ".pdf")
        output_path = os.path.join(OUTPUT_FOLDER, uid + "_compressed.pdf")

        file.save(input_path)

        compress_pdf(input_path, output_path, level)

        output_files.append(output_path)

    # 📦 لو أكثر من ملف → ZIP
    if len(output_files) > 1:

        zip_path = os.path.join(OUTPUT_FOLDER, "compressed.zip")

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for f in output_files:
                zipf.write(f, os.path.basename(f))

        return send_file(zip_path, as_attachment=True)

    return send_file(output_files[0], as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
