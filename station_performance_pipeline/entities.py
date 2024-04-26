from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Operator:
    operator_name: str
    operator_code: str


@dataclass
class Station:
    crs_code: str
    station_name: str


@dataclass
class Service:
    operator: Operator
    service_uid: str


@dataclass
class Arrival:
    station: Station
    service: Service
    scheduled_arrival: datetime
    actual_arrival: datetime


@dataclass
class CancellationType:
    cancellation_code: str
    description: str


@dataclass
class Cancellation:
    cancellation_type: CancellationType
    station: Station
    service: Service
    scheduled_arrival: datetime
