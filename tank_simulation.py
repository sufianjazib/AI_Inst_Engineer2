import numpy as np

class TankSimulation:
    def __init__(self, capacity_liters=1000.0, initial_level_pct=50.0):
        self.capacity = capacity_liters
        self.level_pct = initial_level_pct
        
        # Physical parameters
        self.max_inflow_rate = 190.0   # m³/h max
        self.base_drain_rate = 182.0   # m³/h max
        
        # Valve state & feedback (%)
        self.inlet_valve_cmd = 80.0
        self.outlet_valve_cmd = 80.0
        self.outlet_valve_fb = 80.0    # Position Feedback
        
        # Pressures & Temperatures
        self.pt101_pressure = 8.2      # bar
        self.tt101_temp = 85.0         # °C
        self.instrument_air = 5.8      # bar
        
        # Fault states
        self.active_fault = "No Fault"
        
        # Alarm Thresholds
        self.HIGH_ALARM_PCT = 95.0
        self.LOW_ALARM_PCT = 5.0

    def set_valves(self, inlet_pct: float, outlet_pct: float):
        self.inlet_valve_cmd = float(np.clip(inlet_pct, 0.0, 100.0))
        self.outlet_valve_cmd = float(np.clip(outlet_pct, 0.0, 100.0))

    def inject_fault(self, fault_name: str):
        self.active_fault = fault_name

    def update_simulation(self, dt: float = 1.0):
        # Apply fault behavior
        if self.active_fault == "Control Valve Fault":
            self.outlet_valve_fb = 35.0  # Valve stuck at 35% feedback despite 80% cmd
        elif self.active_fault == "Stuck Transmitter":
            pass # Level freezes
        else:
            self.outlet_valve_fb = self.outlet_valve_cmd

        # Dynamic smooth level progression based on inflow vs outflow
        if self.active_fault != "Stuck Transmitter":
            inflow = (self.inlet_valve_cmd / 100.0) * (self.max_inflow_rate / 3600.0) * dt * 10
            actual_drain = (self.outlet_valve_fb / 100.0) * (self.base_drain_rate / 3600.0) * dt * 10
            
            # Level change
            net_change = inflow - actual_drain
            self.level_pct = float(np.clip(self.level_pct + net_change, 0.0, 100.0))

    def check_alarms(0 -> dict:
        return {
            "high_alarm": self.level_pct >= self.HIGH_ALARM_PCT,
            "low_alarm": self.level_pct <= self.LOW_ALARM_PCT,
            "valve_fault": abs(self.outlet_valve_cmd - self.outlet_valve_fb) > 10.0,
            "normal": self.LOW_ALARM_PCT < self.level_pct < self.HIGH_ALARM_PCT
        }

    def get_status(0 -> dict:
        alarms = self.check_alarms()
        inflow_val = round((self.inlet_valve_cmd / 100.0) * self.max_inflow_rate, 1)
        outflow_val = round((self.outlet_valve_fb / 100.0) * self.base_drain_rate, 1)
        
        return {
            "level_pct": round(self.level_pct, 1),
            "pressure": self.pt101_pressure,
            "temp": self.tt101_temp,
            "inst_air": self.instrument_air,
            "inflow": inflow_val,
            "outflow": outflow_val,
            "valve_cmd": self.outlet_valve_cmd,
            "valve_fb": self.outlet_valve_fb,
            "high_alarm": alarms["high_alarm"],
            "low_alarm": alarms["low_alarm"],
            "valve_fault": alarms["valve_fault"]
        }


def get_gauge_color(level_pct: float, high_t: float = 95.0, low_t: float = 5.0) -> str:
    if level_pct >= high_t:
        return "#FF4B4B"  # Critical High Red
    elif level_pct <= low_t:
        return "#FFA500"  # Critical Low Orange
    return "#00E5FF"      # Cyan Normal
