import os
from flask import request

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def remove_background():
    return "<h2>إزالة خلفية الصورة</h2><p>قريباً...</p><a href='/'>رجوع</a>"

def image_to_webp():
    return "<h2>تحويل ل WebP</h2><p>قريباً...</p><a href='/'>رجوع</a>"
