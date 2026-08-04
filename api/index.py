import sys
import os

# إضافة المجلد الرئيسي للمسار
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app

# Vercel Serverless Handler
handler = app
