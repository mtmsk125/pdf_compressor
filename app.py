from flask import Flask, request, render_template_string, send_file
import PyPDF2
from io import BytesIO

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>ضغط ملفات PDF</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }
        .box { background: white; padding: 40px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input[type="file"] { margin: 20px 0; }
        button { background: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <div class="box">
        <h1>📄 ضغط ملفات PDF</h1>
        <p>ارفع ملف PDF وهيتم ضغطه فوراً</p>
        <form action="/pdf/compress" method="post" enctype="multipart
