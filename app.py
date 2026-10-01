import time
import numpy as np

class TankSimulation:
    def __init__(self, capacity_liters=1000.0, initial_level_pct=50.0):
        self.capacity = capacity_liters      # Total tank volume (Liters)
        self.level_pct = initial_level_pct   # Current level in %
        
        # Flow rates (Percentage per second at max valve opening)
        self.max_inflow_rate = 3.0   # % level gain per second when fill valve is 100% open
        self.base_drain_rate = 1.5   # Base % level loss per second when drain valve is 100% open
        
        # Valve States (0.0 = Closed, 1.0 = Fully Open)
        self.inlet_valve = 0.0
        self.outlet_valve = 0.0
        
        # Alarm Thresholds
        self.HIGH_ALARM_PCT = 95.0
        self.LOW_ALARM_PCT = 5.0
        
    def set_valves(self, inlet_open_pct: float, outlet_open_pct: float):
        """Set valve positions from 0.0 to 1.0 (0% to 100%)."""
        self.inlet_valve = np.clip(inlet_open_pct, 0.0, 1.0)
        self.outlet_valve = np.clip(outlet_open_pct, 0.0, 1.0)

    def update_simulation(self, dt: float):
        """
        Advances the tank state by dt seconds.
        Level changes smoothly in both directions based on valve positions and pressure.
        """
        # Inflow depends linearly on inlet valve position
        inflow = self.inlet_valve * self.max_inflow_rate * dt
        
        # Hydrostatic pressure effect: higher water level drains slightly faster
        hydrostatic_factor = max(0.1, self.level_pct / 100.0) if self.level_pct > 0 else 0.0
        outflow = self.outlet_valve * self.base_drain_rate * hydrostatic_factor * dt
        
        # Net level change
        net_change = inflow - outflow
        self.level_pct = np.clip(self.level_pct + net_change, 0.0, 100.0)

    def check_alarms(self) -> dict:
        """Evaluates alarm conditions based on current level percentage."""
        return {
            "HIGH_ALARM_95": self.level_pct >= self.HIGH_ALARM_PCT,
            "LOW_ALARM_05": self.level_pct <= self.LOW_ALARM_PCT,
            "NORMAL": self.LOW_ALARM_PCT < self.level_pct < self.HIGH_ALARM_PCT
        }

    def get_status(self) -> dict:
        alarms = self.check_alarms()
        
        if alarms["HIGH_ALARM_95"]:
            alarm_state = "CRITICAL HIGH (>= 95%)"
        elif alarms["LOW_ALARM_05"]:
            alarm_state = "CRITICAL LOW (<= 5%)"
        else:
            alarm_state = "OK (NORMAL OPERATING RANGE)"

        return {
            "level_pct": round(self.level_pct, 2),
            "level_liters": round((self.level_pct / 100.0) * self.capacity, 1),
            "alarm_state": alarm_state,
            "high_alarm": alarms["HIGH_ALARM_95"],
            "low_alarm": alarms["LOW_ALARM_05"]
        }


# --- Demonstration Run ---
if __name__ == "__main__":
    tank = TankSimulation(capacity_liters=1000.0, initial_level_pct=92.0)
    
    print("--- 1. Testing Smooth Fill to High Alarm (>= 95%) ---")
    tank.set_valves(inlet_open_pct=1.0, outlet_open_pct=0.0)
    
    dt = 1.0  # 1-second time step updates
    for t in range(5):
        tank.update_simulation(dt)
        status = tank.get_status()
        print(f"t={t+1}s | Level: {status['level_pct']}% ({status['level_liters']}L) | Alarm Status: {status['alarm_state']}")
    
    print("\n--- 2. Testing Smooth Drain to Low Alarm (<= 5%) ---")
    tank.set_valves(inlet_open_pct=0.0, outlet_open_pct=1.0)
    
    for t in range(1, 40):
        tank.update_simulation(dt)
        status = tank.get_status()
        if t % 5 == 0 or status['low_alarm']:
            print(f"t={t}s | Level: {status['level_pct']}% ({status['level_liters']}L) | Alarm Status: {status['alarm_state']}")
        if status['low_alarm']:
            break
