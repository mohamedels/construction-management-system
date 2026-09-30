from datetime import datetime, timedelta

from database import connect


def employee_report(start_date, end_date, project=None):
    with connect() as conn:
        query = """
            SELECT e.code, e.name, e.job_title, COUNT(r.id) AS work_days,
                   COALESCE(SUM(r.daily_amount),0) AS total_daily,
                   COALESCE(SUM(r.extra),0) AS total_extra,
                   COALESCE(SUM(r.discount),0) AS total_discount,
                   COALESCE(SUM(r.net_amount),0) AS net_total
            FROM employees e
            LEFT JOIN employee_records r ON r.employee_id = e.id
            WHERE r.record_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if project:
            query += " AND (r.project = ? OR e.project = ?)"
            params += [project, project]
        query += " GROUP BY e.id ORDER BY e.name"
        rows = conn.execute(query, params).fetchall()
    return rows


def equipment_report(start_date, end_date, project=None):
    with connect() as conn:
        query = """
            SELECT e.code, e.name, e.hourly_rate, COALESCE(SUM(r.hours),0) AS total_hours,
                   COALESCE(SUM(r.total_amount),0) AS total_amount
            FROM equipment e
            LEFT JOIN equipment_records r ON r.equipment_id = e.id
            WHERE r.record_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if project:
            query += " AND (r.project = ? OR e.project = ?)"
            params += [project, project]
        query += " GROUP BY e.id ORDER BY e.name"
        rows = conn.execute(query, params).fetchall()
    return rows


def transport_report(start_date, end_date, project=None):
    with connect() as conn:
        query = """
            SELECT v.code, v.vehicle_number, v.driver_name, COALESCE(SUM(r.trips),0) AS total_trips,
                   COALESCE(SUM(r.total_amount),0) AS total_amount
            FROM transport_vehicles v
            LEFT JOIN transport_records r ON r.vehicle_id = v.id
            WHERE r.record_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if project:
            query += " AND (r.project = ? OR v.project = ?)"
            params += [project, project]
        query += " GROUP BY v.id ORDER BY v.vehicle_number"
        rows = conn.execute(query, params).fetchall()
    return rows


def water_report(start_date, end_date, project=None):
    with connect() as conn:
        query = """
            SELECT w.code, w.vehicle_number, w.driver_name, COALESCE(SUM(r.trips),0) AS total_trips,
                   COALESCE(SUM(r.total_amount),0) AS total_amount
            FROM water_trucks w
            LEFT JOIN water_records r ON r.truck_id = w.id
            WHERE r.record_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if project:
            query += " AND (r.project = ? OR w.project = ?)"
            params += [project, project]
        query += " GROUP BY w.id ORDER BY w.vehicle_number"
        rows = conn.execute(query, params).fetchall()
    return rows


def current_week_range():
    today = datetime.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start.date().isoformat(), end.date().isoformat()


def current_month_range():
    today = datetime.today()
    start = today.replace(day=1)
    next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    end = next_month - timedelta(days=1)
    return start.date().isoformat(), end.date().isoformat()
