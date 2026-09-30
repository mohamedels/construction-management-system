from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
EXPORTS_DIR = ROOT / "exports"
DB_PATH = DATA_DIR / "database.db"

DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

import sqlite3


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                job_title TEXT,
                phone TEXT,
                national_id TEXT,
                project TEXT,
                daily_rate REAL DEFAULT 0,
                status TEXT DEFAULT 'يعمل',
                created_at TEXT DEFAULT CURRENT_DATE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employee_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                record_date TEXT NOT NULL,
                project TEXT,
                status TEXT,
                daily_amount REAL DEFAULT 0,
                extra REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                net_amount REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                equipment_type TEXT,
                equipment_number TEXT,
                operator_name TEXT,
                project TEXT,
                hourly_rate REAL DEFAULT 0,
                status TEXT DEFAULT 'نشط',
                created_at TEXT DEFAULT CURRENT_DATE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS equipment_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER NOT NULL,
                record_date TEXT NOT NULL,
                project TEXT,
                start_time TEXT,
                end_time TEXT,
                hours REAL DEFAULT 0,
                hourly_rate REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (equipment_id) REFERENCES equipment(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transport_vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                vehicle_number TEXT,
                vehicle_type TEXT,
                plate_number TEXT,
                driver_name TEXT,
                project TEXT,
                trip_price REAL DEFAULT 0,
                status TEXT DEFAULT 'نشط',
                created_at TEXT DEFAULT CURRENT_DATE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transport_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                record_date TEXT NOT NULL,
                project TEXT,
                origin TEXT,
                destination TEXT,
                load_type TEXT,
                trips INTEGER DEFAULT 0,
                trip_price REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES transport_vehicles(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS water_trucks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                vehicle_number TEXT,
                plate_number TEXT,
                driver_name TEXT,
                capacity TEXT,
                project TEXT,
                trip_price REAL DEFAULT 0,
                status TEXT DEFAULT 'نشط',
                created_at TEXT DEFAULT CURRENT_DATE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS water_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                truck_id INTEGER NOT NULL,
                record_date TEXT NOT NULL,
                project TEXT,
                location TEXT,
                trip_type TEXT,
                trips INTEGER DEFAULT 0,
                trip_price REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (truck_id) REFERENCES water_trucks(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES('company_name', 'شركة المقاولات')"
        )

        conn.commit()


def next_code(prefix: str, table_name: str, code_col: str) -> str:
    with connect() as conn:
        row = conn.execute(
            f"SELECT {code_col} FROM {table_name} WHERE {code_col} LIKE ? ORDER BY {code_col} DESC LIMIT 1",
            (f"{prefix}-%",),
        ).fetchone()
        if not row:
            return f"{prefix}-001"
        last_code = row[code_col]
        try:
            number = int(str(last_code).split('-')[-1])
        except ValueError:
            number = 0
        return f"{prefix}-{number + 1:03d}"


def add_employee(data):
    with connect() as conn:
        code = next_code("EMP", "employees", "code")
        conn.execute(
            """
            INSERT INTO employees (code, name, job_title, phone, national_id, project, daily_rate, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                data["name"],
                data["job_title"],
                data["phone"],
                data["national_id"],
                data["project"],
                float(data["daily_rate"] or 0),
                data["status"],
            ),
        )
        conn.commit()
        return code


def list_employees():
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM employees ORDER BY id ASC"
        ).fetchall()


def get_employee(employee_id):
    with connect() as conn:
        return conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()


def add_employee_record(data):
    status = data["status"]
    daily_amount = float(data.get("daily_amount") or 0)
    extra = float(data.get("extra") or 0)
    discount = float(data.get("discount") or 0)
    net_amount = daily_amount + extra - discount
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO employee_records (employee_id, record_date, project, status, daily_amount, extra, discount, net_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(data["employee_id"]),
                data["record_date"],
                data["project"],
                status,
                daily_amount,
                extra,
                discount,
                net_amount,
                data["notes"],
            ),
        )
        conn.commit()


def get_employee_records(employee_id):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM employee_records WHERE employee_id = ? ORDER BY record_date DESC",
            (employee_id,),
        ).fetchall()


def add_equipment(data):
    with connect() as conn:
        code = next_code("EQ", "equipment", "code")
        conn.execute(
            """
            INSERT INTO equipment (code, name, equipment_type, equipment_number, operator_name, project, hourly_rate, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                data["name"],
                data["equipment_type"],
                data["equipment_number"],
                data["operator_name"],
                data["project"],
                float(data["hourly_rate"] or 0),
                data["status"],
            ),
        )
        conn.commit()
        return code


def list_equipment():
    with connect() as conn:
        return conn.execute("SELECT * FROM equipment ORDER BY id ASC").fetchall()


def get_equipment(equipment_id):
    with connect() as conn:
        return conn.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,)).fetchone()


def add_equipment_record(data):
    start_h = data.get("start_time")
    end_h = data.get("end_time")
    hours = 0.0
    from calculations import hours_between
    if start_h and end_h:
        hours = hours_between(start_h, end_h)
    total = hours * float(data.get("hourly_rate") or 0)
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO equipment_records (equipment_id, record_date, project, start_time, end_time, hours, hourly_rate, total_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(data["equipment_id"]),
                data["record_date"],
                data["project"],
                start_h,
                end_h,
                hours,
                float(data.get("hourly_rate") or 0),
                total,
                data["notes"],
            ),
        )
        conn.commit()


def get_equipment_records(equipment_id):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM equipment_records WHERE equipment_id = ? ORDER BY record_date DESC",
            (equipment_id,),
        ).fetchall()


def add_transport_vehicle(data):
    with connect() as conn:
        code = next_code("TRK", "transport_vehicles", "code")
        conn.execute(
            """
            INSERT INTO transport_vehicles (code, vehicle_number, vehicle_type, plate_number, driver_name, project, trip_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                data["vehicle_number"],
                data["vehicle_type"],
                data["plate_number"],
                data["driver_name"],
                data["project"],
                float(data["trip_price"] or 0),
                data["status"],
            ),
        )
        conn.commit()
        return code


def list_transport_vehicles():
    with connect() as conn:
        return conn.execute("SELECT * FROM transport_vehicles ORDER BY id ASC").fetchall()


def get_transport_vehicle(vehicle_id):
    with connect() as conn:
        return conn.execute("SELECT * FROM transport_vehicles WHERE id = ?", (vehicle_id,)).fetchone()


def add_transport_record(data):
    trips = int(data.get("trips") or 0)
    trip_price = float(data.get("trip_price") or 0)
    total = trips * trip_price
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO transport_records (vehicle_id, record_date, project, origin, destination, load_type, trips, trip_price, total_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(data["vehicle_id"]),
                data["record_date"],
                data["project"],
                data["origin"],
                data["destination"],
                data["load_type"],
                trips,
                trip_price,
                total,
                data["notes"],
            ),
        )
        conn.commit()


def get_transport_records(vehicle_id):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM transport_records WHERE vehicle_id = ? ORDER BY record_date DESC",
            (vehicle_id,),
        ).fetchall()


def add_water_truck(data):
    with connect() as conn:
        code = next_code("WTR", "water_trucks", "code")
        conn.execute(
            """
            INSERT INTO water_trucks (code, vehicle_number, plate_number, driver_name, capacity, project, trip_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                data["vehicle_number"],
                data["plate_number"],
                data["driver_name"],
                data["capacity"],
                data["project"],
                float(data["trip_price"] or 0),
                data["status"],
            ),
        )
        conn.commit()
        return code


def list_water_trucks():
    with connect() as conn:
        return conn.execute("SELECT * FROM water_trucks ORDER BY id ASC").fetchall()


def get_water_truck(truck_id):
    with connect() as conn:
        return conn.execute("SELECT * FROM water_trucks WHERE id = ?", (truck_id,)).fetchone()


def add_water_record(data):
    trips = int(data.get("trips") or 0)
    trip_price = float(data.get("trip_price") or 0)
    total = trips * trip_price
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO water_records (truck_id, record_date, project, location, trip_type, trips, trip_price, total_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(data["truck_id"]),
                data["record_date"],
                data["project"],
                data["location"],
                data["trip_type"],
                trips,
                trip_price,
                total,
                data["notes"],
            ),
        )
        conn.commit()


def get_water_records(truck_id):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM water_records WHERE truck_id = ? ORDER BY record_date DESC",
            (truck_id,),
        ).fetchall()


def get_dashboard_summary():
    with connect() as conn:
        employees_count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        equipment_count = conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
        transport_count = conn.execute("SELECT COUNT(*) FROM transport_vehicles").fetchone()[0]
        water_count = conn.execute("SELECT COUNT(*) FROM water_trucks").fetchone()[0]

        workers_total = conn.execute("SELECT COALESCE(SUM(daily_rate),0) FROM employees").fetchone()[0]
        equipment_total = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM equipment_records").fetchone()[0]
        transport_total = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM transport_records").fetchone()[0]
        water_total = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM water_records").fetchone()[0]

        employee_net_total = conn.execute("SELECT COALESCE(SUM(net_amount),0) FROM employee_records").fetchone()[0]

    return {
        "employees_count": employees_count,
        "equipment_count": equipment_count,
        "transport_count": transport_count,
        "water_count": water_count,
        "employee_net_total": employee_net_total,
        "equipment_total": equipment_total,
        "transport_total": transport_total,
        "water_total": water_total,
        "workers_total": workers_total,
    }


def search_all(term):
    search = f"%{term}%"
    results = []
    with connect() as conn:
        for table_name, cols in {
            "employees": ["name", "code", "job_title", "phone", "national_id"],
            "equipment": ["name", "code", "equipment_number", "operator_name"],
            "transport_vehicles": ["vehicle_number", "plate_number", "driver_name", "code"],
            "water_trucks": ["vehicle_number", "plate_number", "driver_name", "code"],
        }.items():
            if table_name == "employees":
                rows = conn.execute(
                    "SELECT id, code, name, 'عامل' AS type FROM employees WHERE " + " OR ".join([f"{c} LIKE ?" for c in cols]),
                    [search] * len(cols),
                ).fetchall()
            elif table_name == "equipment":
                rows = conn.execute(
                    "SELECT id, code, name, 'معدة' AS type FROM equipment WHERE " + " OR ".join([f"{c} LIKE ?" for c in cols]),
                    [search] * len(cols),
                ).fetchall()
            elif table_name == "transport_vehicles":
                rows = conn.execute(
                    "SELECT id, code, vehicle_number, 'نقل' AS type FROM transport_vehicles WHERE " + " OR ".join([f"{c} LIKE ?" for c in cols]),
                    [search] * len(cols),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, code, vehicle_number, 'مياه' AS type FROM water_trucks WHERE " + " OR ".join([f"{c} LIKE ?" for c in cols]),
                    [search] * len(cols),
                ).fetchall()
            results.extend([dict(r) for r in rows])
    return results


def get_employee_totals(employee_id):
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 
                COUNT(*) AS work_days,
                COALESCE(SUM(daily_amount),0) AS total_daily,
                COALESCE(SUM(extra),0) AS total_extra,
                COALESCE(SUM(discount),0) AS total_discount,
                COALESCE(SUM(net_amount),0) AS net_total
            FROM employee_records
            WHERE employee_id = ?
            """,
            (employee_id,),
        ).fetchone()
        return row


def get_equipment_totals(equipment_id):
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 
                COALESCE(SUM(hours),0) AS total_hours,
                COALESCE(SUM(total_amount),0) AS total_amount
            FROM equipment_records
            WHERE equipment_id = ?
            """,
            (equipment_id,),
        ).fetchone()
        return row


def get_transport_totals(vehicle_id):
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 
                COALESCE(SUM(trips),0) AS total_trips,
                COALESCE(SUM(total_amount),0) AS total_amount
            FROM transport_records
            WHERE vehicle_id = ?
            """,
            (vehicle_id,),
        ).fetchone()
        return row


def get_water_totals(truck_id):
    with connect() as conn:
        row = conn.execute(
            """
            SELECT 
                COALESCE(SUM(trips),0) AS total_trips,
                COALESCE(SUM(total_amount),0) AS total_amount
            FROM water_records
            WHERE truck_id = ?
            """,
            (truck_id,),
        ).fetchone()
        return row


if __name__ == "__main__":
    init_db()
    print("تم إنشاء قاعدة البيانات بنجاح.")
    print(DB_PATH)
