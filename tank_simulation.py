import numpy as np

class TankSimulation:
    def __init__(self, capacity_liters=1000.0, initial_level_pct=50.0):
        self.capacity = capacity_liters      # Total tank volume in Liters
        self.level_pct = initial_level_pct   # Current level in percentage
        
        # Base rates (% level change per second at 100% valve position)
        self.max_inflow_rate = 3.0   
        self.base_drain_rate = 1.5   
        
        # Valve position states (0.0 = 0% closed, 1.0 = 100% open)
        self.inlet_valve = 0.0
        self.outlet_valve = 0.0
        
        # Alarm threshold configurations
        self.HIGH_ALARM_PCT = 95.0
        self.LOW_ALARM_PCT = 5.0

    def set_valves(self, inlet_open_pct: float, outlet_open_pct: float):
        """Sets valve openings clamped between 0.0 and 1.0."""
        self.inlet_valve = np.clip(inlet_open_pct, 0.0, 1.0)
        self.outlet_valve = np.clip(outlet_open_pct, 0.0, 1.0)

    def update_simulation(self, dt: float):
        """
        Advances the tank level smoothly.
        Filling and draining occur continuously based on valve positions and hydrostatic pressure.
        """
        # Smooth continuous inflow calculation
        inflow = self.inlet_valve * self.max_inflow_rate * dt
        
        # Hydrostatic pressure factor: higher water level drains slightly faster
        hydrostatic_factor = max(0.1, self.level_pct / 100.0) if self.level_pct > 0 else 0.0
        outflow = self.outlet_valve * self.base_drain_rate * hydrostatic_factor * dt
        
        # Update current level safely clamped between 0% and 100%
        net_change = inflow - outflow
        self.level_pct = np.clip(self.level_pct + net_change, 0.0, 100.0)

    def check_alarms(self) -> dict:
        """Returns active boolean alarm states based on thresholds."""
        return {
            "high_alarm": self.level_pct >= self.HIGH_ALARM_PCT,
            "low_alarm": self.level_pct <= self.LOW_ALARM_PCT,
            "normal": self.LOW_ALARM_PCT < self.level_pct < self.HIGH_ALARM_PCT
        }

    def get_status(self) -> dict:
        """Returns comprehensive status dictionary."""
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
    Returns visual color parameters (Hex code, status badge, CSS styles)
    based on the current tank fill level.
    """
    if level_pct >= high_threshold:
        return {
            "color_hex": "#FF4B4B",         # Bright Red
            "status_text": "CRITICAL HIGH (>= 95%)",
            "badge_color": "red",
            "bg_tint": "#FFE6E6",
            "alert_type": "error"
        }
    elif level_pct <= low_threshold:
        return {
            "color_hex": "#FFA500",         # Warning Orange
            "status_text": "CRITICAL LOW (<= 5%)",
            "badge_color": "orange",
            "bg_tint": "#FFF0D6",
            "alert_type": "warning"
        }
    else:
        return {
            "color_hex": "#1C83E1",         # Normal Operating Blue
            "status_text": "NORMAL OPERATING RANGE",
            "badge_color": "blue",
            "bg_tint": "#E8F4FE",
            "alert_type": "success"
        }
