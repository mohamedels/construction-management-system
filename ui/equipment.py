from tkinter import ttk, messagebox, Toplevel
import tkinter as tk

from database import (
    add_equipment,
    add_equipment_record,
    get_equipment,
    get_equipment_records,
    get_equipment_totals,
    list_equipment,
)


class EquipmentFormDialog(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("إضافة معدة")
        self.geometry("500x420")
        self.transient(master)
        self.grab_set()
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("اسم المعدة", "name"),
            ("النوع", "equipment_type"),
            ("رقم المعدة", "equipment_number"),
            ("المشغل", "operator_name"),
            ("المشروع", "project"),
            ("سعر الساعة", "hourly_rate"),
        ]
        self.values = {}
        for index, (label_text, key) in enumerate(fields):
            tk.Label(form, text=label_text, font=("Tahoma", 10, "bold")).grid(row=index, column=0, sticky="w", pady=6)
            entry = tk.Entry(form, width=30, font=("Tahoma", 10))
            entry.grid(row=index, column=1, padx=8, pady=6)
            self.values[key] = entry

        tk.Label(form, text="الحالة", font=("Tahoma", 10, "bold")).grid(row=6, column=0, sticky="w", pady=6)
        status = ttk.Combobox(form, values=["نشط", "متوقف", "صيانة"], state="readonly", width=27)
        status.grid(row=6, column=1, padx=8, pady=6)
        status.current(0)
        self.values["status"] = status

        ttk.Button(form, text="حفظ", command=self.save).grid(row=7, column=0, columnspan=2, pady=16)

    def save(self):
        try:
            data = {key: widget.get().strip() for key, widget in self.values.items()}
            if not data["name"]:
                raise ValueError("اسم المعدة مطلوب")
            add_equipment(data)
            messagebox.showinfo("نجاح", "تم إضافة المعدة بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ: {exc}")


class EquipmentPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.build()

    def build(self):
        toolbar = tk.Frame(self, bg="#F3F6FA")
        toolbar.pack(fill="x", pady=(10, 5), padx=10)
        ttk.Button(toolbar, text="إضافة معدة", command=self.app.add_equipment).pack(side="right")
        ttk.Button(toolbar, text="تحديث", command=self.refresh).pack(side="left")

        columns = ("الكود", "اسم المعدة", "النوع", "رقم المعدة", "المشغل", "المشروع", "سعر الساعة", "الحالة")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.bind("<Double-1>", self.open_equipment)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in list_equipment():
            self.tree.insert("", "end", values=(
                item["code"], item["name"], item["equipment_type"], item["equipment_number"],
                item["operator_name"], item["project"], item["hourly_rate"], item["status"],
            ))

    def open_equipment(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        code = values[0]
        for equipment in list_equipment():
            if equipment["code"] == code:
                EquipmentDetailWindow(self.app, equipment)
                break


class EquipmentDetailWindow(Toplevel):
    def __init__(self, master, equipment):
        super().__init__(master)
        self.title(f"سجل المعدة: {equipment['name']}")
        self.geometry("1150x700")
        self.equipment = equipment
        self.build()

    def build(self):
        info = tk.Frame(self, padx=20, pady=20)
        info.pack(fill="x")
        data = [
            ("الكود", self.equipment["code"]),
            ("اسم المعدة", self.equipment["name"]),
            ("النوع", self.equipment["equipment_type"]),
            ("رقم المعدة", self.equipment["equipment_number"]),
            ("المشغل", self.equipment["operator_name"]),
            ("المشروع", self.equipment["project"]),
            ("سعر الساعة", self.equipment["hourly_rate"]),
        ]
        for i, (label, value) in enumerate(data):
            tk.Label(info, text=f"{label}:", font=("Tahoma", 10, "bold")).grid(row=i, column=0, sticky="w", padx=8, pady=6)
            tk.Label(info, text=str(value), font=("Tahoma", 10)).grid(row=i, column=1, sticky="w", padx=8, pady=6)

        totals = get_equipment_totals(self.equipment["id"])
        totals_frame = tk.Frame(self, padx=20, pady=10)
        totals_frame.pack(fill="x")
        tk.Label(totals_frame, text=f"إجمالي ساعات التشغيل: {totals['total_hours']}", font=("Tahoma", 10, "bold"), fg="#2E7D32").pack(side="left", padx=10)
        tk.Label(totals_frame, text=f"إجمالي المستحق: {totals['total_amount']}", font=("Tahoma", 10, "bold"), fg="#2E7D32").pack(side="left", padx=10)

        ttk.Button(self, text="إضافة سجل تشغيل", command=self.add_record).pack(anchor="e", padx=20, pady=(0, 10))

        columns = ("التاريخ", "المشروع", "بداية التشغيل", "نهاية التشغيل", "عدد الساعات", "سعر الساعة", "إجمالي المستحق", "ملاحظات")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_records()

    def refresh_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in get_equipment_records(self.equipment["id"]):
            self.tree.insert("", "end", values=(
                rec["record_date"], rec["project"], rec["start_time"], rec["end_time"], rec["hours"], rec["hourly_rate"], rec["total_amount"], rec["notes"],
            ))

    def add_record(self):
        EquipmentRecordDialog(self, self.equipment, self.refresh_records)


class EquipmentRecordDialog(Toplevel):
    def __init__(self, master, equipment, refresh_callback):
        super().__init__(master)
        self.title("إضافة سجل تشغيل للمعدة")
        self.geometry("520x420")
        self.equipment = equipment
        self.refresh_callback = refresh_callback
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        fields = [
            ("التاريخ", "record_date"),
            ("المشروع", "project"),
            ("بداية التشغيل", "start_time"),
            ("نهاية التشغيل", "end_time"),
            ("سعر الساعة", "hourly_rate"),
            ("ملاحظات", "notes"),
        ]
        self.values = {}
        for index, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=("Tahoma", 10, "bold")).grid(row=index, column=0, sticky="w", pady=6)
            entry = tk.Entry(form, width=30, font=("Tahoma", 10))
            entry.grid(row=index, column=1, padx=8, pady=6)
            self.values[key] = entry

        ttk.Button(form, text="حفظ", command=self.save).grid(row=6, column=0, columnspan=2, pady=16)

    def save(self):
        try:
            data = {key: widget.get().strip() for key, widget in self.values.items()}
            data["equipment_id"] = self.equipment["id"]
            data["hourly_rate"] = data["hourly_rate"] or str(self.equipment["hourly_rate"])
            add_equipment_record(data)
            self.refresh_callback()
            messagebox.showinfo("نجاح", "تم حفظ سجل التشغيل بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {exc}")
