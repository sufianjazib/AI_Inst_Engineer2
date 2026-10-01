import numpy as np

class TankSimulation:
    def __init__(self, capacity_liters=1000.0, initial_level_pct=50.0):
        self.capacity = capacity_liters
        self.level_pct = initial_level_pct
        
        # Base process values
        self.max_inflow_rate = 190.0   # m³/h
        self.base_drain_rate = 182.0   # m³/h
        
        # Valve state & feedback (%)
        self.inlet_valve_cmd = 80.0
        self.outlet_valve_cmd = 80.0
        self.outlet_valve_fb = 80.0    
        
        # Pressures & Temperatures
        self.base_pressure = 8.2       # bar (PT-101 base)
        self.pt101_pressure = 8.2      # bar
        self.tt101_temp = 85.0         # °C
        self.instrument_air = 5.8      # bar
        
        # Fault states
        self.active_fault = "No Fault"
        self.drift_offset = 0.0
        
        # Alarm Thresholds
        self.HIGH_ALARM_PCT = 95.0
        self.LOW_ALARM_PCT = 5.0

    def set_valves(self, inlet_pct: float, outlet_pct: float):
        self.inlet_valve_cmd = float(np.clip(inlet_pct, 0.0, 100.0))
        self.outlet_valve_cmd = float(np.clip(outlet_pct, 0.0, 100.0))

    def inject_fault(self, fault_name: str):
        self.active_fault = fault_name
        self.drift_offset = 0.0  # Reset drift accumulator when switching faults

    def update_simulation(self, dt: float = 1.0):
        # 1. Reset values to normal baselines before applying fault rules
        self.outlet_valve_fb = self.outlet_valve_cmd
        self.pt101_pressure = self.base_pressure
        self.instrument_air = 5.8

        # 2. Apply Fault Behaviors
        if self.active_fault == "Control Valve Fault":
            # Valve stuck at 35% position despite receiving higher command
            self.outlet_valve_fb = 35.0

        elif self.active_fault == "PT-101 Drift":
            # Gradually drift pressure sensor reading upwards over time
            self.drift_offset += 0.2
            self.pt101_pressure = self.base_pressure + self.drift_offset

        elif self.active_fault == "4–20 mA Loop Fault":
            # Signal drops to 0 mA / zero reading due to wire disconnect or card failure
            self.pt101_pressure = 0.0

        elif self.active_fault == "Low Instrument Air":
            # Drop supply air from 5.8 bar down to 2.1 bar, restricting valve movement
            self.instrument_air = 2.1
            self.outlet_valve_fb = self.outlet_valve_cmd * 0.4

        elif self.active_fault == "Impulse Line Blockage":
            # Freeze pressure reading regardless of process conditions
            self.pt101_pressure = 8.2

        elif self.active_fault == "Stuck Transmitter":
            # Freeze level dynamics (returns early to skip tank volume updates)
            return

        # 3. Dynamic tank level calculation based on actual inflow and valve feedback
        inflow = (self.inlet_valve_cmd / 100.0) * (self.max_inflow_rate / 3600.0) * dt * 10
        actual_drain = (self.outlet_valve_fb / 100.0) * (self.base_drain_rate / 3600.0) * dt * 10
        
        net_change = inflow - actual_drain
        self.level_pct = float(np.clip(self.level_pct + net_change, 0.0, 100.0))

    def check_alarms(self) -> dict:
        return {
            "high_alarm": self.level_pct >= self.HIGH_ALARM_PCT,
            "low_alarm": self.level_pct <= self.LOW_ALARM_PCT,
            "valve_fault": abs(self.outlet_valve_cmd - self.outlet_valve_fb) > 10.0,
            "air_fault": self.instrument_air < 3.0,
            "pressure_fault": self.pt101_pressure < 1.0 or self.pt101_pressure > 12.0
        }

    def get_status(self) -> dict:
        alarms = self.check_alarms()
        inflow_val = round((self.inlet_valve_cmd / 100.0) * self.max_inflow_rate, 1)
        outflow_val = round((self.outlet_valve_fb / 100.0) * self.base_drain_rate, 1)
        
        return {
            "level_pct": round(self.level_pct, 1),
            "pressure": round(self.pt101_pressure, 2),
            "temp": self.tt101_temp,
            "inst_air": round(self.instrument_air, 1),
            "inflow": inflow_val,
            "outflow": outflow_val,
            "valve_cmd": self.outlet_valve_cmd,
            "valve_fb": self.outlet_valve_fb,
            "high_alarm": alarms["high_alarm"],
            "low_alarm": alarms["low_alarm"],
            "valve_fault": alarms["valve_fault"],
            "air_fault": alarms["air_fault"],
            "pressure_fault": alarms["pressure_fault"]
        }


def get_gauge_color(level_pct: float, high_t: float = 95.0, low_t: float = 5.0) -> str:
    if level_pct >= high_t:
        return "#FF4B4B"  # High Alarm (Red)
    elif level_pct <= low_t:
        return "#FFA500"  # Low Alarm (Orange)
    return "#00E5FF"      # Normal (Cyan)
