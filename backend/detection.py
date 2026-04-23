from typing import List, Optional
from datetime import datetime
import uuid

class DetectionLogic:
    def __init__(self):
        self.alerts = []
        self.last_pressure = None

    def analyze(self, data: dict) -> List[dict]:
        new_alerts = []
        pressure = data["pressure"]
        f_up = data["flow_rate_upstream"]
        f_down = data["flow_rate_downstream"]

        # 1. Leak Detection: Rapid pressure drop
        if self.last_pressure is not None:
            drop = self.last_pressure - pressure
            if drop > 1.5:  # Significant drop in one cycle
                alert = {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "type": "Leak Detected",
                    "severity": "Critical",
                    "message": f"Rapid pressure drop of {round(drop, 2)} PSI detected.",
                    "zone": data["zone"]
                }
                new_alerts.append(alert)

        # 2. Theft Detection: Flow mismatch
        flow_diff = f_up - f_down
        if flow_diff > 5.0:  # More than 5 units difference
            alert = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": "Suspected Theft",
                "severity": "Warning",
                "message": f"Flow mismatch detected: Upstream {f_up} vs Downstream {f_down}.",
                "zone": data["zone"]
            }
            new_alerts.append(alert)

        self.last_pressure = pressure
        return new_alerts

detector = DetectionLogic()
