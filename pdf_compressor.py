import os
import io
import fitz
from PIL import Image
import uuid
import json
from flask import Flask, request, send_file, render_template_string, jsonify

app = Flask(__name__)
DB_FILE = "users_db.json"

HTML_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF Compressor Pro - 5$ مدى الحياة</title>
<style>
    body { font-family: 'Tahoma', sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }
    .container { max-width: 950px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
    h1 { color: #2c3e50; text-align: center; }
    .pricing { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 20px; margin: 40px 0; }
    .plan { border: 2px solid #ddd; border-radius: 12px; padding: 25px; text-align: center; position: relative; }
    .plan.popular { border-color: #e74c3c; box-shadow: 0 0 20px rgba(231,76,60,0.2); }
    .badge { position: absolute; top: -12px; right: 20px; background: #e74c3c; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    .price { font-size: 42px; color: #2c3e50; font-weight: bold; margin: 15px 0; }
    .price span { font-size: 16px; color: #7f8c8d; }
    button { background: #3498db; color: white; border: none; padding: 14px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; }
    button:hover { background: #2980b9; }
    .compress-box, .activate-box { background: #ecf0f1; padding: 25px; border-radius: 10px; margin-top: 30px; }
    input[type=file], input[type=text] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
    #result { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 8px; display: none; }
    .counter { background: #fff3cd; padding: 12px; border-radius: 6px; margin: 10px 0; text-align: center; font-weight: bold; }
    .note { font-size: 13px; color: #7f8c8d; text-align: center; margin-top: 10px; }
</style>
</head>
<body>
<div class="container">
    <h1>📦 PDF Compressor Pro</h1>
    <p style="text-align:center; color:#7f8c8d; font-size:18px">اضغط ملفات PDF حتى 70% بدون ما تخرب الجودة</p>

    <div class="pricing">
        <div class="plan">
            <h3>جرّب مجاناً</h3>
            <div class="price">0$<span>/للأبد</span></div>
            <p>✓ 3 صفحات لكل ملف<br>✓ علامة مائية صغيرة<br>✓ بدون تسجيل</p>
            <button onclick="scrollToCompress()">ابدأ الضغط</button>
        </div>

        <div class="plan popular">
            <span class="badge">الأكثر مبيعاً</span>
            <h3>Lifetime Starter</h3>
            <div class="price">5$<span> مرة وحدة</span></div>
            <p>✓ 50 ملف كامل مدى الحياة<br>✓ بدون علامة مائية<br>✓ سرعة أولوية<br>✓ أرخص من سندويشة</p>
            <button onclick="alert('لما تربط Payoneer، زر الدفع رح يتحول تلقائي. هسا للتجربة: الكود DEMO-5USD')">اشتري الآن</button>
        </div>

        <div class="plan">
            <h3>Lifetime Pro</h3>
            <div class="price">14.99$<span> مرة وحدة</span></div>
            <p>✓ ملفات غير محدودة<br>✓ بدون علامة مائية<br>✓ API للمطورين<br>✓ دعم 24/7</p>
            <button onclick="alert('للشركات والمكاتب')">اشتري الآن</button>
        </div>
    </div>

    <div class="activate-box">
        <h3>🔑 عندك كود تفعيل؟</h3>
        <p>بعد الدفع رح يوصلك كود. الصقه هون عشان تفعل الـ 50 ملف:</p>
        <input type="text" id="codeInput" placeholder="مثال: LIFETIME-ABCD-1234">
        <button onclick="activateCode()">فعّل الكود</button>
        <div id="activateResult"></div>
        <p class="note">لسا ما ربطت Payoneer؟ استخدم كود التجربة: DEMO-5USD</p>
    </div>

    <div class="compress-box" id="compress">
        
