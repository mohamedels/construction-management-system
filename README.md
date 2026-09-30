from pathlib import Path

# Project construction management system
# Requires Python 3.11+

README = """# نظام إدارة المقاولات

برنامج احترافي لإدارة العمال والمعدات وعربيات النقل وعربيات المياه باستخدام Python، SQLite، Tkinter، وExcel export.

## المميزات
- Dashboard رئيسية
- إدارة العمال
- إدارة المعدات
- إدارة عربيات النقل
- إدارة عربيات المياه
- تسجيل بيانات يومية
- البحث المركزي
- تقارير يومية/أسبوعية/شهرية
- تصدير Excel
- حفظ بيانات SQLite

## المتطلبات
- Python 3.11+
- pip

## التثبيت
1. افتح موجه الأوامر داخل المجلد.
2. نفّذ:
   python -m venv venv
   venv\\Scripts\\activate
   pip install -r requirements.txt
3. ابدأ التطبيق:
   python main.py

## هيكل المشروع
project/
├── main.py
├── database.py
├── calculations.py
├── excel_manager.py
├── reports.py
├── models.py
├── ui/
│   ├── dashboard.py
│   ├── employees.py
│   ├── equipment.py
│   ├── transport.py
│   └── water_trucks.py
├── data/
├── exports/
├── requirements.txt
└── README.md

## ملاحظات مهمة
- تم اعتماد SQLite كوحدة تخزين أساسية.
- يتم استخدام Excel فقط للتصدير والتقارير.
- لا يتم إنشاء Sheet جديد يوميًا؛ كل عنصر له Sheet واحد.
- يتم احتساب الوحدات وفقًا للقاعدة التالية:
  - العمال = يومية
  - المعدات = ساعة
  - عربيات النقل = نقلة
  - عربيات المياه = نقلة
"""

Path("README.md").write_text(README, encoding="utf-8")
