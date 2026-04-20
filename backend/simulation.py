import random
import time
from datetime import datetime
from typing import Dict

class SimulationEngine:
    def __init__(self):
        self.pressure = 100.0  # PSI
        self.flow_rate_upstream = 50.0  # Barrel/min
        self.flow_rate_downstream = 50.0
        self.temperature = 75.0  # Fahrenheit
        self.is_leaking = False
        self.is_theft = False
        self.zone = "Zone A"

    def get_latest_data(self) -> Dict:
        # Add normal noise
        noise_p = random.uniform(-0.5, 0.5)
        noise_f = random.uniform(-0.2, 0.2)
        noise_t = random.uniform(-0.1, 0.1)

        if self.is_leaking:
            # Pressure drops rapidly, downstream flow drops
            self.pressure -= random.uniform(2.0, 5.0)
            self.flow_rate_downstream -= random.uniform(1.0, 3.0)
            if self.pressure < 20: self.pressure = 20
        elif self.is_theft:
            # Downstream flow is significantly lower than upstream, pressure stays relatively stable
            self.flow_rate_downstream = self.flow_rate_upstream * 0.7
        else:
            # Normal recovery if was leaking/theft
            if self.pressure < 100: self.pressure += 1.0
            if self.flow_rate_downstream < self.flow_rate_upstream:
                self.flow_rate_downstream += 0.5
            
            # Constrain to normal ranges
            self.pressure = max(80, min(120, self.pressure + noise_p))
            self.flow_rate_upstream = max(45, min(55, self.flow_rate_upstream + noise_f))
            self.flow_rate_downstream = max(45, min(55, self.flow_rate_downstream + noise_f))
        
        self.temperature = max(70, min(85, self.temperature + noise_t))

        return {
            "timestamp": datetime.now().isoformat(),
            "pressure": round(self.pressure, 2),
            "flow_rate_upstream": round(self.flow_rate_upstream, 2),
            "flow_rate_downstream": round(self.flow_rate_downstream, 2),
            "temperature": round(self.temperature, 2),
            "zone": self.zone
        }

    def trigger_leak(self, state: bool):
        self.is_leaking = state
        if state: self.is_theft = False

    def trigger_theft(self, state: bool):
        self.is_theft = state
        if state: self.is_leaking = False

simulation_engine = SimulationEngine()
