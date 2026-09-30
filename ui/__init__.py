from tkinter import ttk, messagebox, Toplevel, StringVar
import tkinter as tk

from database import (
    add_employee,
    add_employee_record,
    get_employee,
    get_employee_records,
    get_employee_totals,
    list_employees,
)


class EmployeeFormDialog(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("إضافة عامل")
        self.geometry("460x430")
        self.transient(master)
        self.grab_set()
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("اسم العامل", "name"),
            ("الوظيفة", "job_title"),
            ("الهاتف", "phone"),
            ("الرقم القومي", "national_id"),
            ("المشروع", "project"),
            ("سعر اليومية", "daily_rate"),
        ]
        self.values = {}
        for index, (label_text, key) in enumerate(fields):
            tk.Label(form, text=label_text, font=("Tahoma", 10, "bold"), anchor="w").grid(row=index, column=0, sticky="w", pady=6)
            entry = tk.Entry(form, font=("Tahoma", 10), width=28)
            entry.grid(row=index, column=1, padx=8, pady=6)
            self.values[key] = entry

        tk.Label(form, text="الحالة", font=("Tahoma", 10, "bold")).grid(row=6, column=0, sticky="w", pady=6)
        status = ttk.Combobox(form, values=["يعمل", "متوقف", "إجازة"], state="readonly", width=25)
        status.grid(row=6, column=1, padx=8, pady=6)
        status.current(0)
        self.values["status"] = status

        ttk.Button(form, text="حفظ", command=self.save).grid(row=7, column=0, columnspan=2, pady=16)

    def save(self):
        try:
            data = {key: widget.get().strip() for key, widget in self.values.items()}
            if not data["name"]:
                raise ValueError("اسم العامل مطلوب")
            add_employee(data)
            messagebox.showinfo("نجاح", "تم إضافة العامل بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ: {exc}")


class EmployeesPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.build()

    def build(self):
        toolbar = tk.Frame(self, bg="#F3F6FA")
        toolbar.pack(fill="x", pady=(10, 5), padx=10)
        ttk.Button(toolbar, text="إضافة عامل", command=self.app.add_employee).pack(side="right")
        ttk.Button(toolbar, text="تحديث", command=self.refresh).pack(side="left")

        columns = ("الكود", "اسم العامل", "الوظيفة", "الهاتف", "المشروع", "سعر اليومية", "الحالة")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.open_employee)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for emp in list_employees():
            self.tree.insert("", "end", values=(
                emp["code"],
                emp["name"],
                emp["job_title"],
                emp["phone"],
                emp["project"],
                emp["daily_rate"],
                emp["status"],
            ))

    def open_employee(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        code = values[0]
        for emp in list_employees():
            if emp["code"] == code:
                EmployeeDetailWindow(self.app, emp)
                break


class EmployeeDetailWindow(Toplevel):
    def __init__(self, master, employee):
        super().__init__(master)
        self.title(f"سجل العامل: {employee['name']}")
        self.geometry("1100x700")
        self.employee = employee
        self.build()

    def build(self):
        info = tk.Frame(self, padx=20, pady=20)
        info.pack(fill="x")
        fields = [
            ("الكود", self.employee["code"]),
            ("اسم العامل", self.employee["name"]),
            ("الوظيفة", self.employee["job_title"]),
            ("الهاتف", self.employee["phone"]),
            ("المشروع", self.employee["project"]),
            ("سعر اليومية", self.employee["daily_rate"]),
        ]
        for index, (label, value) in enumerate(fields):
            tk.Label(info, text=f"{label}:", font=("Tahoma", 10, "bold")).grid(row=index, column=0, sticky="w", padx=8, pady=6)
            tk.Label(info, text=str(value), font=("Tahoma", 10)).grid(row=index, column=1, sticky="w", padx=8, pady=6)

        totals_frame = tk.Frame(self, padx=20, pady=10)
        totals_frame.pack(fill="x")
        totals = get_employee_totals(self.employee["id"])
        labels = [
            ("إجمالي أيام العمل", totals["work_days"]),
            ("إجمالي اليوميات", totals["total_daily"]),
            ("إجمالي الإضافي", totals["total_extra"]),
            ("إجمالي الخصومات", totals["total_discount"]),
            ("صافي المستحق", totals["net_total"]),
        ]
        for i, (label, value) in enumerate(labels):
            tk.Label(totals_frame, text=f"{label}: {value}", font=("Tahoma", 10, "bold"), fg="#0A6EBD").grid(row=0, column=i, padx=10, pady=6)

        add_btn = ttk.Button(self, text="إضافة سجل يومي", command=self.add_record)
        add_btn.pack(anchor="e", padx=20, pady=(0, 10))

        columns = ("التاريخ", "المشروع", "الحالة", "اليومية", "إضافي", "خصم", "صافي المستحق", "ملاحظات")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_records()

    def refresh_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in get_employee_records(self.employee["id"]):
            self.tree.insert("", "end", values=(
                rec["record_date"],
                rec["project"],
                rec["status"],
                rec["daily_amount"],
                rec["extra"],
                rec["discount"],
                rec["net_amount"],
                rec["notes"],
            ))

    def add_record(self):
        EmployeeRecordDialog(self, self.employee, self.refresh_records)


class EmployeeRecordDialog(Toplevel):
    def __init__(self, master, employee, refresh_callback):
        super().__init__(master)
        self.title("إضافة سجل يومي للعامل")
        self.geometry("500x400")
        self.employee = employee
        self.refresh_callback = refresh_callback
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        entries = {
            "التاريخ": tk.Entry(form, width=30),
            "المشروع": tk.Entry(form, width=30),
            "الحالة": ttk.Combobox(form, values=["حاضر", "غائب", "إجازة"], state="readonly", width=27),
            "اليومية": tk.Entry(form, width=30),
            "إضافي": tk.Entry(form, width=30),
            "خصم": tk.Entry(form, width=30),
            "ملاحظات": tk.Entry(form, width=30),
        }
        entries["الحالة"].current(0)

        for idx, (label, widget) in enumerate(entries.items()):
            tk.Label(form, text=label, font=("Tahoma", 10, "bold")).grid(row=idx, column=0, sticky="w", pady=6)
            widget.grid(row=idx, column=1, pady=6)

        ttk.Button(form, text="حفظ", command=self.save).grid(row=len(entries), column=0, columnspan=2, pady=14)
        self.entries = entries

    def save(self):
        try:
            data = {
                "employee_id": self.employee["id"],
                "record_date": self.entries["التاريخ"].get().strip() or "2024-01-01",
                "project": self.entries["المشروع"].get().strip(),
                "status": self.entries["الحالة"].get().strip(),
                "daily_amount": self.entries["اليومية"].get().strip() or "0",
                "extra": self.entries["إضافي"].get().strip() or "0",
                "discount": self.entries["خصم"].get().strip() or "0",
                "notes": self.entries["ملاحظات"].get().strip(),
            }
            add_employee_record(data)
            self.refresh_callback()
            messagebox.showinfo("نجاح", "تم حفظ سجل العامل بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {exc}")
