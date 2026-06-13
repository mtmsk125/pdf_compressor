from flask import Flask, render_template, request, send_file, redirect, session
import subprocess
import os
import uuid
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "compressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =========================
# DB
# =========================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# =========================
# FILE SIZE
# =========================
def get_size(path):
    return os.path.getsize(path)


# =========================
# PDF COMPRESS
# =========================
def compress_pdf(input_pdf, output_pdf, level="medium"):

    original_size = get_size(input_pdf)

    if level == "low":
        pdfset = "/ebook"
    elif level == "high":
        pdfset = "/screen"
    else:
        pdfset = "/ebook"

    subprocess.run(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={pdfset}",
            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",
            f"-sOutputFile={output_pdf}",
            input_pdf,
        ],
        capture_output=True,
        text=True
    )

    compressed_size = get_size(output_pdf)
    savings = round((1 - compressed_size / original_size) * 100, 2)

    return original_size, compressed_size, savings


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, password))
            conn.commit()
        except:
            return "User exists"

        conn.close()
        return redirect("/login")

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = user[1]
            return redirect("/")
        else:
            return "Wrong login"

    return render_template("login.html")


# =========================
# HOME
# =========================
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", user=session["user"])


# =========================
# COMPRESS
# =========================
@app.route("/compress", methods=["POST"])
def compress():

    if "user" not in session:
        return redirect("/login")

    file = request.files["file"]
    level = request.form.get("level", "medium")

    uid = str(uuid.uuid4())

    input_path = os.path.join(UPLOAD_FOLDER, uid + ".pdf")
    output_path = os.path.join(OUTPUT_FOLDER, uid + "_compressed.pdf")

    file.save(input_path)

    original, compressed, savings = compress_pdf(input_path, output_path, level)

    return render_template(
        "result.html",
        original=round(original / 1024, 2),
        compressed=round(compressed / 1024, 2),
        savings=savings,
        filename=os.path.basename(output_path)
    )


# =========================
# DOWNLOAD
# =========================
@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
