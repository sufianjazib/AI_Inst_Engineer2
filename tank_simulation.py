import numpy as np

class TankSimulation:
    def __init__(self, capacity_liters=1000.0, initial_level_pct=50.0):
        self.capacity = capacity_liters      # Total volume (Liters)
        self.level_pct = initial_level_pct   # Current level (%)
        
        # Base flow rates (% change per second when valve is 100% open)
        self.max_inflow_rate = 3.0   
        self.base_drain_rate = 1.5   
        
        # Valve openings (0.0 = 0%, 1.0 = 100%)
        self.inlet_valve = 0.0
        self.outlet_valve = 0.0
        
        # Alarm threshold settings
        self.HIGH_ALARM_PCT = 95.0
        self.LOW_ALARM_PCT = 5.0

    def set_valves(self, inlet_open_pct: float, outlet_open_pct: float):
        """Sets valve openings clamped between 0.0 (0%) and 1.0 (100%)."""
        self.inlet_valve = np.clip(inlet_open_pct, 0.0, 1.0)
        self.outlet_valve = np.clip(outlet_open_pct, 0.0, 1.0)

    def update_simulation(self, dt: float):
        """
        Calculates gradual fill/drain transitions based on valve positions and hydrostatic head.
        """
        # Inflow calculation
        inflow = self.inlet_valve * self.max_inflow_rate * dt
        
        # Outflow calculation with hydrostatic pressure factor (drains faster when fuller)
        hydrostatic_factor = max(0.1, self.level_pct / 100.0) if self.level_pct > 0 else 0.0
        outflow = self.outlet_valve * self.base_drain_rate * hydrostatic_factor * dt
        
        # Smooth net level change bounded strictly between 0% and 100%
        net_change = inflow - outflow
        self.level_pct = np.clip(self.level_pct + net_change, 0.0, 100.0)

    def check_alarms(self) -> dict:
        """Returns boolean status for alarm conditions."""
        return {
            "high_alarm": self.level_pct >= self.HIGH_ALARM_PCT,
            "low_alarm": self.level_pct <= self.LOW_ALARM_PCT,
            "normal": self.LOW_ALARM_PCT < self.level_pct < self.HIGH_ALARM_PCT
        }

    def get_status(self) -> dict:
        """Returns dictionary of current process parameters."""
        alarms = self.check_alarms()
        return {
            "level_pct": round(self.level_pct, 2),
            "level_liters": round((self.level_pct / 100.0) * self.capacity, 1),
            "high_alarm": alarms["high_alarm"],
            "low_alarm": alarms["low_alarm"],
            "normal": alarms["normal"]
        }


def get_tank_color_theme(level_pct: float, high_threshold: float = 95.0, low_threshold: float = 5.0) -> dict:
    """
    Determines visual theme parameters according to the current fill state and active alarms.
    """
    if level_pct >= high_threshold:
        return {
            "color_hex": "#FF4B4B",         # Bright Red
            "status_text": "CRITICAL HIGH (>= 95%)",
            "badge_color": "red",
            "alert_type": "error"
        }
    elif level_pct <= low_threshold:
        return {
            "color_hex": "#FFA500",         # Warning Orange
            "status_text": "CRITICAL LOW (<= 5%)",
            "badge_color": "orange",
            "alert_type": "warning"
        }
    else:
        return {
            "color_hex": "#1C83E1",         # Operating Blue
            "status_text": "NORMAL OPERATING RANGE",
            "badge_color": "blue",
            "alert_type": "success"
        }
