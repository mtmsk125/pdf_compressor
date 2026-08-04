import sys
import os

# إضافة مجلد المشروع الرئيسي إلى المسارات
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

# التصدير لـ Vercel Serverless
app = app
