from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from database import init_db, get_dashboard_summary, search_all
from excel_manager import export_excel
from reports import employee_report, equipment_report, transport_report, water_report


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام إدارة المقاولات")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        self.configure(bg="#F3F6FA")
        self._build_ui()
        init_db()

    def _build_ui(self):
        self.sidebar = tk.Frame(self, width=250, bg="#1F2D3D")
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg="#F3F6FA")
        self.content.pack(side="right", fill="both", expand=True)

        title = tk.Label(self.sidebar, text="لوحة التحكم", fg="white", bg="#1F2D3D", font=("Tahoma", 18, "bold"))
        title.pack(pady=(20, 10), fill="x")

        buttons = [
            ("الرئيسية", self.show_dashboard),
            ("العمال", self.show_employees),
            ("المعدات", self.show_equipment),
            ("عربيات النقل", self.show_transport),
            ("عربيات المياه", self.show_water),
            ("التقارير", self.show_reports),
            ("بحث", self.show_search),
            ("إضافة عامل", self.add_employee),
            ("إضافة معدة", self.add_equipment),
            ("إضافة عربية نقل", self.add_transport_vehicle),
            ("إضافة عربية مياه", self.add_water_truck),
            ("إعدادات", self.show_settings),
            ("تصدير إلى Excel", self.export_data),
        ]

        for text, command in buttons:
            btn = tk.Button(
                self.sidebar,
                text=text,
                command=command,
                bg="#2A3F5F",
                fg="white",
                font=("Tahoma", 11, "bold"),
                relief="flat",
                padx=10,
                pady=10,
                width=20,
                cursor="hand2",
            )
            btn.pack(pady=4, padx=10, fill="x")

        self.current_page = None
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        frame = tk.Frame(self.content, bg="#F3F6FA")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame, text="لوحة التحكم", font=("Tahoma", 24, "bold"), bg="#F3F6FA").pack(anchor="w")

        summary = get_dashboard_summary()
        cards = [
            ("عدد العمال", summary["employees_count"], "#0A6EBD"),
            ("عدد المعدات", summary["equipment_count"], "#2E7D32"),
            ("عدد عربيات النقل", summary["transport_count"], "#D97706"),
            ("عدد عربيات المياه", summary["water_count"], "#7C3AED"),
            ("إجمالي مستحقات العمال", summary["employee_net_total"], "#C2185B"),
            ("إجمالي تشغيل المعدات", summary["equipment_total"], "#2E7D32"),
            ("إجمالي عربيات النقل", summary["transport_total"], "#D97706"),
            ("إجمالي عربيات المياه", summary["water_total"], "#7C3AED"),
        ]

        for i, (label, value, color) in enumerate(cards):
            card = tk.Frame(frame, bg="#FFFFFF", padx=20, pady=20, bd=1, relief="solid")
            card.grid(row=i // 4, column=i % 4, padx=12, pady=12, sticky="nsew")
            tk.Label(card, text=label, font=("Tahoma", 11), bg="#FFFFFF", fg="#555555").pack(anchor="w")
            tk.Label(card, text=f"{value:,.2f}", font=("Tahoma", 20, "bold"), bg="#FFFFFF", fg=color).pack(anchor="w", pady=(10, 0))

        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def show_employees(self):
        self.clear_content()
        from ui.employees import EmployeesPage
        EmployeesPage(self.content, self).pack(fill="both", expand=True)

    def show_equipment(self):
        self.clear_content()
        from ui.equipment import EquipmentPage
        EquipmentPage(self.content, self).pack(fill="both", expand=True)

    def show_transport(self):
        self.clear_content()
        from ui.transport import TransportPage
        TransportPage(self.content, self).pack(fill="both", expand=True)

    def show_water(self):
        self.clear_content()
        from ui.water_trucks import WaterTrucksPage
        WaterTrucksPage(self.content, self).pack(fill="both", expand=True)

    def show_reports(self):
        self.clear_content()
        report_frame = tk.Frame(self.content, bg="#F3F6FA")
        report_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(report_frame, text="التقارير", font=("Tahoma", 20, "bold"), bg="#F3F6FA").pack(anchor="w")

        form = tk.Frame(report_frame, bg="#F3F6FA")
        form.pack(fill="x", pady=10)

        tk.Label(form, text="من تاريخ", bg="#F3F6FA", font=("Tahoma", 11)).grid(row=0, column=0, padx=10, pady=10)
        start_date = tk.Entry(form, width=20, font=("Tahoma", 11))
        start_date.grid(row=0, column=1)
        start_date.insert(0, "2024-01-01")

        tk.Label(form, text="إلى تاريخ", bg="#F3F6FA", font=("Tahoma", 11)).grid(row=0, column=2, padx=10, pady=10)
        end_date = tk.Entry(form, width=20, font=("Tahoma", 11))
        end_date.grid(row=0, column=3)
        end_date.insert(0, "2024-12-31")

        tk.Label(form, text="المشروع", bg="#F3F6FA", font=("Tahoma", 11)).grid(row=1, column=0, padx=10, pady=10)
        project = tk.Entry(form, width=20, font=("Tahoma", 11))
        project.grid(row=1, column=1)

        def run_report():
            try:
                d1 = start_date.get()
                d2 = end_date.get()
                p = project.get().strip()
                rows1 = employee_report(d1, d2, p or None)
                rows2 = equipment_report(d1, d2, p or None)
                rows3 = transport_report(d1, d2, p or None)
                rows4 = water_report(d1, d2, p or None)

                messagebox.showinfo("التقرير", 
                    f"العمال: {len(rows1)}\nالمعدات: {len(rows2)}\nعربيات النقل: {len(rows3)}\nعربيات المياه: {len(rows4)}\n\nتم تجهيز التقرير بنجاح.")
            except Exception as exc:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء إنشاء التقرير: {exc}")

        ttk.Button(form, text="إنشاء التقرير", command=run_report).grid(row=1, column=3, pady=10)

    def show_search(self):
        self.clear_content()
        frame = tk.Frame(self.content, bg="#F3F6FA")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame, text="البحث", font=("Tahoma", 22, "bold"), bg="#F3F6FA").pack(anchor="w")
        search_var = tk.StringVar()
        tk.Entry(frame, textvariable=search_var, font=("Tahoma", 12), width=50).pack(anchor="w", pady=10)

        tree = ttk.Treeview(frame, columns=("الكود", "الاسم", "النوع"), show="headings")
        tree.heading("الكود", text="الكود")
        tree.heading("الاسم", text="الاسم")
        tree.heading("النوع", text="النوع")
        tree.pack(fill="both", expand=True)

        def do_search():
            tree.delete(*tree.get_children())
            term = search_var.get().strip()
            if not term:
                return
            rows = search_all(term)
            for r in rows:
                tree.insert("", "end", values=(r.get("code", ""), r.get("name", r.get("vehicle_number", "")), r.get("type", "")))

        ttk.Button(frame, text="بحث", command=do_search).pack(anchor="w", pady=10)

    def show_settings(self):
        messagebox.showinfo("الإعدادات", "سيتم إضافة إعدادات الشركة لاحقًا في نسخة التطوير التالية.")

    def add_employee(self):
        from ui.employees import EmployeeFormDialog
        EmployeeFormDialog(self)

    def add_equipment(self):
        from ui.equipment import EquipmentFormDialog
        EquipmentFormDialog(self)

    def add_transport_vehicle(self):
        from ui.transport import TransportVehicleFormDialog
        TransportVehicleFormDialog(self)

    def add_water_truck(self):
        from ui.water_trucks import WaterTruckFormDialog
        WaterTruckFormDialog(self)

    def export_data(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("ملف Excel", "*.xlsx")],
            initialfile="export_construction_system.xlsx",
        )
        if not path:
            return
        try:
            result = export_excel(path)
            messagebox.showinfo("نجاح", f"تم تصدير الملف بنجاح:\n{result}")
        except Exception as exc:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التصدير: {exc}")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
