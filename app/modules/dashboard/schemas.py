from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class KPIValue(BaseModel):
    title: str
    value: str
    subtitle: str


class MonthlyTrip(BaseModel):
    month: str
    viajes: int


class RecentActivity(BaseModel):
    id: int
    descripcion: str = Field(alias="descripcion")
    estado: str
    hora: str


class UpcomingTrip(BaseModel):
    hora: str
    origen: str
    destino: str
    pasajeros: int


class Alert(BaseModel):
    type: str
    title: str
    description: str


class DashboardOut(BaseModel):
    kpis: list[KPIValue]
    monthly_trips: list[MonthlyTrip] = Field(alias="monthlyTrips")
    recent_activities: list[RecentActivity] = Field(alias="recentActivities")
    upcoming_trips: list[UpcomingTrip] = Field(alias="upcomingTrips")
    alerts: list[Alert]
