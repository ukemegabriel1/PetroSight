from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SensorData(BaseModel):
    timestamp: str
    pressure: float
    flow_rate_upstream: float
    flow_rate_downstream: float
    temperature: float

class Alert(BaseModel):
    id: str
    timestamp: str
    type: str  # Leak, Theft, Maintenance
    severity: str  # Critical, Warning, Info
    message: str
    zone: str

class SystemStatus(BaseModel):
    status: str  # Normal, Risk, Emergency
    alerts: List[Alert]
    current_data: SensorData
