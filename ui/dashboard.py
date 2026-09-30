from tkinter import ttk, messagebox, Toplevel
import tkinter as tk

from database import (
    add_water_truck,
    add_water_record,
    get_water_truck,
    get_water_records,
    get_water_totals,
    list_water_trucks,
)


class WaterTruckFormDialog(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("إضافة عربية مياه")
        self.geometry("500x430")
        self.transient(master)
        self.grab_set()
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("رقم العربية", "vehicle_number"),
            ("رقم اللوحة", "plate_number"),
            ("السائق", "driver_name"),
            ("السعة", "capacity"),
            ("المشروع", "project"),
            ("سعر النقلة", "trip_price"),
        ]
        self.values = {}
        for index, (label_text, key) in enumerate(fields):
            tk.Label(form, text=label_text, font=("Tahoma", 10, "bold")).grid(row=index, column=0, sticky="w", pady=6)
            entry = tk.Entry(form, width=30, font=("Tahoma", 10))
            entry.grid(row=index, column=1, padx=8, pady=6)
            self.values[key] = entry

        tk.Label(form, text="الحالة", font=("Tahoma", 10, "bold")).grid(row=6, column=0, sticky="w", pady=6)
        status = ttk.Combobox(form, values=["نشط", "متوقف", "إصلاح"], state="readonly", width=27)
        status.grid(row=6, column=1, padx=8, pady=6)
        status.current(0)
        self.values["status"] = status

        ttk.Button(form, text="حفظ", command=self.save).grid(row=7, column=0, columnspan=2, pady=16)

    def save(self):
        try:
            data = {key: widget.get().strip() for key, widget in self.values.items()}
            if not data["vehicle_number"]:
                raise ValueError("رقم العربية مطلوب")
            add_water_truck(data)
            messagebox.showinfo("نجاح", "تم إضافة عربية المياه بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ: {exc}")


class WaterTrucksPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.build()

    def build(self):
        toolbar = tk.Frame(self, bg="#F3F6FA")
        toolbar.pack(fill="x", pady=(10, 5), padx=10)
        ttk.Button(toolbar, text="إضافة عربية مياه", command=self.app.add_water_truck).pack(side="right")
        ttk.Button(toolbar, text="تحديث", command=self.refresh).pack(side="left")

        columns = ("الكود", "رقم العربية", "اللوحة", "السائق", "السعة", "المشروع", "سعر النقلة", "الحالة")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.bind("<Double-1>", self.open_truck)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in list_water_trucks():
            self.tree.insert("", "end", values=(
                item["code"], item["vehicle_number"], item["plate_number"], item["driver_name"],
                item["capacity"], item["project"], item["trip_price"], item["status"],
            ))

    def open_truck(self, event):
        item = self.tree.selection()[0]
        code = self.tree.item(item, "values")[0]
        for truck in list_water_trucks():
            if truck["code"] == code:
                WaterTruckDetailWindow(self.app, truck)
                break


class WaterTruckDetailWindow(Toplevel):
    def __init__(self, master, truck):
        super().__init__(master)
        self.title(f"سجل عربية المياه: {truck['vehicle_number']}")
        self.geometry("1200x700")
        self.truck = truck
        self.build()

    def build(self):
        info = tk.Frame(self, padx=20, pady=20)
        info.pack(fill="x")
        data = [
            ("الكود", self.truck["code"]),
            ("رقم العربية", self.truck["vehicle_number"]),
            ("رقم اللوحة", self.truck["plate_number"]),
            ("السائق", self.truck["driver_name"]),
            ("السعة", self.truck["capacity"]),
            ("المشروع", self.truck["project"]),
            ("سعر النقلة", self.truck["trip_price"]),
        ]
        for i, (label, value) in enumerate(data):
            tk.Label(info, text=f"{label}:", font=("Tahoma", 10, "bold")).grid(row=i, column=0, sticky="w", padx=8, pady=6)
            tk.Label(info, text=str(value), font=("Tahoma", 10)).grid(row=i, column=1, sticky="w", padx=8, pady=6)

        totals = get_water_totals(self.truck["id"])
        totals_frame = tk.Frame(self, padx=20, pady=10)
        totals_frame.pack(fill="x")
        tk.Label(totals_frame, text=f"إجمالي عدد النقلات: {totals['total_trips']}", font=("Tahoma", 10, "bold"), fg="#7C3AED").pack(side="left", padx=10)
        tk.Label(totals_frame, text=f"إجمالي المستحق: {totals['total_amount']}", font=("Tahoma", 10, "bold"), fg="#7C3AED").pack(side="left", padx=10)

        ttk.Button(self, text="إضافة سجل نقل", command=self.add_record).pack(anchor="e", padx=20, pady=(0, 10))

        columns = ("التاريخ", "المشروع", "المكان", "نوع النقلة", "عدد النقلات", "سعر النقلة", "إجمالي المستحق", "ملاحظات")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_records()

    def refresh_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in get_water_records(self.truck["id"]):
            self.tree.insert("", "end", values=(
                rec["record_date"], rec["project"], rec["location"], rec["trip_type"],
                rec["trips"], rec["trip_price"], rec["total_amount"], rec["notes"],
            ))

    def add_record(self):
        WaterRecordDialog(self, self.truck, self.refresh_records)


class WaterRecordDialog(Toplevel):
    def __init__(self, master, truck, refresh_callback):
        super().__init__(master)
        self.title("إضافة سجل نقل للمياه")
        self.geometry("540x430")
        self.truck = truck
        self.refresh_callback = refresh_callback
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        fields = [
            ("التاريخ", "record_date"),
            ("المشروع", "project"),
            ("المكان", "location"),
            ("نوع النقلة", "trip_type"),
            ("عدد النقلات", "trips"),
            ("سعر النقلة", "trip_price"),
            ("ملاحظات", "notes"),
        ]
        self.values = {}
        for index, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=("Tahoma", 10, "bold")).grid(row=index, column=0, sticky="w", pady=6)
            entry = tk.Entry(form, width=30, font=("Tahoma", 10))
            entry.grid(row=index, column=1, padx=8, pady=6)
            self.values[key] = entry
        ttk.Button(form, text="حفظ", command=self.save).grid(row=len(fields), column=0, columnspan=2, pady=16)

    def save(self):
        try:
            data = {key: widget.get().strip() for key, widget in self.values.items()}
            data["truck_id"] = self.truck["id"]
            data["trip_price"] = data["trip_price"] or str(self.truck["trip_price"])
            add_water_record(data)
            self.refresh_callback()
            messagebox.showinfo("نجاح", "تم حفظ سجل المياه بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {exc}")
