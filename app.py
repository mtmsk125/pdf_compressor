from flask import Flask, render_template, request, send_file, redirect, session
import subprocess
import os
import uuid
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# =========================
# SECRET KEY (مهم جداً للجلسات)
# =========================
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")


UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "compressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =========================
# DATABASE
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
# PDF COMPRESSION ENGINE
# =========================
def compress_pdf(input_pdf, output_pdf, level="medium"):

    if level == "low":
        pdfset = "/ebook"
    elif level == "high":
        pdfset = "/screen"
    else:
        pdfset = "/ebook"

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
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        raise Exception("Compression Failed")


# =========================
# HOME
# =========================
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", user=session["user"])


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
            return "اسم المستخدم موجود"

        conn.close()
        return redirect("/login")

    return """
    <h2>Register</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br>
        <input name="password" type="password" placeholder="Password"><br>
        <button>Register</button>
    </form>
    """


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
            return "بيانات غير صحيحة"

    return """
    <h2>Login</h2>
    <form method="post">
        <input name="username"><br>
        <input name="password" type="password"><br>
        <button>Login</button>
    </form>
    """


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# =========================
# COMPRESS PDF
# =========================
@app.route("/compress", methods=["POST"])
def compress():

    if "user" not in session:
        return redirect("/login")

    files = request.files.getlist("file")
    level = request.form.get("level", "medium")

    output_files = []

    for file in files:
        uid = str(uuid.uuid4())

        input_path = os.path.join(UPLOAD_FOLDER, uid + ".pdf")
        output_path = os.path.join(OUTPUT_FOLDER, uid + "_compressed.pdf")

        file.save(input_path)
        compress_pdf(input_path, output_path, level)

        output_files.append(output_path)

    return send_file(output_files[0], as_attachment=True)


# =========================
# RUN SERVER (Render Ready)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
