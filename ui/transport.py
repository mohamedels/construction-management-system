from tkinter import ttk, messagebox, Toplevel
import tkinter as tk

from database import (
    add_transport_vehicle,
    add_transport_record,
    get_transport_vehicle,
    get_transport_records,
    get_transport_totals,
    list_transport_vehicles,
)


class TransportVehicleFormDialog(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("إضافة عربية نقل")
        self.geometry("500x430")
        self.transient(master)
        self.grab_set()
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        fields = [
            ("رقم العربية", "vehicle_number"),
            ("نوع العربية", "vehicle_type"),
            ("رقم اللوحة", "plate_number"),
            ("السائق", "driver_name"),
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
            add_transport_vehicle(data)
            messagebox.showinfo("نجاح", "تم إضافة العربية بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ: {exc}")


class TransportPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.build()

    def build(self):
        toolbar = tk.Frame(self, bg="#F3F6FA")
        toolbar.pack(fill="x", pady=(10, 5), padx=10)
        ttk.Button(toolbar, text="إضافة عربية نقل", command=self.app.add_transport_vehicle).pack(side="right")
        ttk.Button(toolbar, text="تحديث", command=self.refresh).pack(side="left")

        columns = ("الكود", "رقم العربية", "نوع العربية", "اللوحة", "السائق", "المشروع", "سعر النقلة", "الحالة")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.bind("<Double-1>", self.open_vehicle)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in list_transport_vehicles():
            self.tree.insert("", "end", values=(
                item["code"], item["vehicle_number"], item["vehicle_type"], item["plate_number"],
                item["driver_name"], item["project"], item["trip_price"], item["status"],
            ))

    def open_vehicle(self, event):
        item = self.tree.selection()[0]
        code = self.tree.item(item, "values")[0]
        for vehicle in list_transport_vehicles():
            if vehicle["code"] == code:
                TransportDetailWindow(self.app, vehicle)
                break


class TransportDetailWindow(Toplevel):
    def __init__(self, master, vehicle):
        super().__init__(master)
        self.title(f"سجل عربية النقل: {vehicle['vehicle_number']}")
        self.geometry("1200x700")
        self.vehicle = vehicle
        self.build()

    def build(self):
        info = tk.Frame(self, padx=20, pady=20)
        info.pack(fill="x")
        data = [
            ("الكود", self.vehicle["code"]),
            ("رقم العربية", self.vehicle["vehicle_number"]),
            ("نوع العربية", self.vehicle["vehicle_type"]),
            ("رقم اللوحة", self.vehicle["plate_number"]),
            ("السائق", self.vehicle["driver_name"]),
            ("المشروع", self.vehicle["project"]),
            ("سعر النقلة", self.vehicle["trip_price"]),
        ]
        for i, (label, value) in enumerate(data):
            tk.Label(info, text=f"{label}:", font=("Tahoma", 10, "bold")).grid(row=i, column=0, sticky="w", padx=8, pady=6)
            tk.Label(info, text=str(value), font=("Tahoma", 10)).grid(row=i, column=1, sticky="w", padx=8, pady=6)

        totals = get_transport_totals(self.vehicle["id"])
        totals_frame = tk.Frame(self, padx=20, pady=10)
        totals_frame.pack(fill="x")
        tk.Label(totals_frame, text=f"إجمالي عدد النقلات: {totals['total_trips']}", font=("Tahoma", 10, "bold"), fg="#D97706").pack(side="left", padx=10)
        tk.Label(totals_frame, text=f"إجمالي المستحق: {totals['total_amount']}", font=("Tahoma", 10, "bold"), fg="#D97706").pack(side="left", padx=10)

        ttk.Button(self, text="إضافة سجل نقل", command=self.add_record).pack(anchor="e", padx=20, pady=(0, 10))

        columns = ("التاريخ", "المشروع", "من", "إلى", "نوع الحمولة", "عدد النقلات", "سعر النقلة", "إجمالي المستحق", "ملاحظات")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_records()

    def refresh_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in get_transport_records(self.vehicle["id"]):
            self.tree.insert("", "end", values=(
                rec["record_date"], rec["project"], rec["origin"], rec["destination"], rec["load_type"],
                rec["trips"], rec["trip_price"], rec["total_amount"], rec["notes"],
            ))

    def add_record(self):
        TransportRecordDialog(self, self.vehicle, self.refresh_records)


class TransportRecordDialog(Toplevel):
    def __init__(self, master, vehicle, refresh_callback):
        super().__init__(master)
        self.title("إضافة سجل نقل")
        self.geometry("540x430")
        self.vehicle = vehicle
        self.refresh_callback = refresh_callback
        self.build()

    def build(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        fields = [
            ("التاريخ", "record_date"),
            ("المشروع", "project"),
            ("من", "origin"),
            ("إلى", "destination"),
            ("نوع الحمولة", "load_type"),
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
            data["vehicle_id"] = self.vehicle["id"]
            data["trip_price"] = data["trip_price"] or str(self.vehicle["trip_price"])
            add_transport_record(data)
            self.refresh_callback()
            messagebox.showinfo("نجاح", "تم حفظ سجل النقل بنجاح")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {exc}")
