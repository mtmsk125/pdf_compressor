from flask import Flask, render_template, request, send_file, redirect
import fitz
import subprocess
import tempfile
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "compressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def compress_pdf(input_pdf, output_pdf):

    temp_pdf = tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ).name

    doc = fitz.open(input_pdf)

    doc.save(
        temp_pdf,
        garbage=4,
        clean=True,
        deflate=True
    )

    doc.close()

    subprocess.run([
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        temp_pdf
    ])

    os.remove(temp_pdf)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/compress', methods=['POST'])
def compress():

    if 'pdf_file' not in request.files:
        return redirect('/')

    file = request.files['pdf_file']

    if file.filename == '':
        return redirect('/')

    uid = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        uid + ".pdf"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        uid + "_compressed.pdf"
    )

    file.save(input_path)

    compress_pdf(input_path, output_path)

    os.remove(input_path)

    return send_file(
        output_path,
        as_attachment=True,
        download_name="compressed.pdf"
    )


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host='0.0.0.0',
        port=port
    )
