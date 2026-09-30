from datetime import datetime


def parse_time(value):
    if value in (None, ""):
        return None
    try:
        return datetime.strptime(str(value), "%H:%M")
    except ValueError:
        try:
            return datetime.strptime(str(value), "%H:%M:%S")
        except ValueError:
            return None


def hours_between(start_time, end_time):
    start = parse_time(start_time)
    end = parse_time(end_time)
    if start is None or end is None:
        return 0.0
    delta = end - start
    total_hours = delta.total_seconds() / 3600
    return round(total_hours, 2)


def net_employee_amount(daily_amount, extra, discount):
    return float(daily_amount) + float(extra) - float(discount)


def round_two(value):
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def safe_decimal(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_currency(value):
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "0.00"
