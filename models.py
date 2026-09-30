from dataclasses import dataclass
from typing import Literal

EMPLOYEE_STATUSES = ["يعمل", "متوقف", "إجازة"]
EQUIPMENT_STATUSES = ["نشط", "متوقف", "صيانة"]
VEHICLE_STATUSES = ["نشط", "متوقف", "إصلاح"]


@dataclass
class Employee:
    code: str
    name: str
    job_title: str
    phone: str
    national_id: str
    project: str
    daily_rate: float
    status: Literal["يعمل", "متوقف", "إجازة"]


@dataclass
class Equipment:
    code: str
    name: str
    equipment_type: str
    equipment_number: str
    operator_name: str
    project: str
    hourly_rate: float
    status: Literal["نشط", "متوقف", "صيانة"]


@dataclass
class TransportVehicle:
    code: str
    vehicle_number: str
    vehicle_type: str
    plate_number: str
    driver_name: str
    project: str
    trip_price: float
    status: Literal["نشط", "متوقف", "إصلاح"]


@dataclass
class WaterTruck:
    code: str
    vehicle_number: str
    plate_number: str
    driver_name: str
    capacity: str
    project: str
    trip_price: float
    status: Literal["نشط", "متوقف", "إصلاح"]
