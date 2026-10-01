import time
import streamlit as st
from tank_simulation import TankSimulation, get_tank_color_theme

st.set_page_config(
    page_title="AI Instrumentation - Tank Level Simulator",
    page_icon="🛢️",
    layout="wide"
)

# Initialize tank instance in Streamlit session state
if "tank" not in st.session_state:
    st.session_state.tank = TankSimulation(capacity_liters=1000.0, initial_level_pct=50.0)

tank = st.session_state.tank

st.title("🛢️ Industrial Tank Level Simulator & Alarm System")
st.markdown("Dynamic tank model featuring continuous filling/draining visuals with **95% High** and **5% Low** alarm alerts.")

# --- SIDEBAR: VALVE CONTROLS & ANIMATION ---
st.sidebar.header("🎛️ Valve Control Panel")

inlet_position = st.sidebar.slider(
    "Inlet Valve Position (%)",
    min_value=0,
    max_value=100,
    value=int(tank.inlet_valve * 100),
    step=5
) / 100.0

outlet_position = st.sidebar.slider(
    "Outlet Valve Position (%)",
    min_value=0,
    max_value=100,
    value=int(tank.outlet_valve * 100),
    step=5
) / 100.0

# Apply slider positions to simulation valves
tank.set_valves(inlet_open_pct=inlet_position, outlet_open_pct=outlet_position)

st.sidebar.markdown("---")
auto_run = st.sidebar.toggle("▶️ Continuous Simulation Loop", value=True)
time_step = st.sidebar.slider("Simulation Speed (Step size dt)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)

# Advance simulation state if active
if auto_run:
    tank.update_simulation(dt=time_step)

# Retrieve current metrics and dynamic styling
status = tank.get_status()
theme = get_tank_color_theme(status["level_pct"], tank.HIGH_ALARM_PCT, tank.LOW_ALARM_PCT)

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Dynamic Level Gauge")
    
    # CSS/HTML Dynamic Tank visualization
    tank_html = f"""
    <div style="
        border: 4px solid #333;
        border-radius: 12px;
        width: 200px;
        height: 320px;
        margin: auto;
        position: relative;
        background-color: #F8F9FA;
        overflow: hidden;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.15);
    ">
        <!-- 95% High Alarm Limit Line -->
        <div style="
            position: absolute;
            top: 5%;
            width: 100%;
            border-top: 2px dashed #FF4B4B;
            z-index: 2;
        "></div>
        <span style="position: absolute; top: 1%; right: 8px; font-size: 11px; color: #FF4B4B; font-weight: bold; z-index: 3;">95% High</span>
        
        <!-- 5% Low Alarm Limit Line -->
        <div style="
            position: absolute;
            top: 95%;
            width: 100%;
            border-top: 2px dashed #FFA500;
            z-index: 2;
        "></div>
        <span style="position: absolute; bottom: 1%; right: 8px; font-size: 11px; color: #FFA500; font-weight: bold; z-index: 3;">5% Low</span>
        
        <!-- Gradual Fluid Height Body -->
        <div style="
            position: absolute;
            bottom: 0;
            width: 100%;
            height: {status['level_pct']}%;
            background-color: {theme['color_hex']};
            transition: height 0.3s ease-out, background-color 0.4s ease;
            z-index: 1;
        "></div>
        
        <!-- Center Percentage Readout -->
        <div style="
            position: absolute;
            width: 100%;
            top: 45%;
            text-align: center;
            font-weight: bold;
            font-size: 22px;
            color: #111;
            z-index: 4;
            text-shadow: 0px 0px 6px rgba(255,255,255,0.9);
        ">
            {status['level_pct']}%
        </div>
    </div>
    """
    st.markdown(tank_html, unsafe_allow_html=True)

with col2:
    st.subheader("Process Readouts & Status")
    
    # Real-time process metrics
    m1, m2 = st.columns(2)
    m1.metric(label="Level (%)", value=f"{status['level_pct']} %")
    m2.metric(label="Volume (L)", value=f"{status['level_liters']} L")
    
    st.markdown("---")
    st.markdown("### System Alarm Status")
    
    # Dynamic alert notifications
    if theme["alert_type"] == "error":
        st.error(f"🚨 **HIGH ALARM ACTIVE:** Level reached **{status['level_pct']}%** (>= {tank.HIGH_ALARM_PCT}% threshold). Throttle inlet valve down.")
    elif theme["alert_type"] == "warning":
        st.warning(f"⚠️ **LOW ALARM ACTIVE:** Level dropped to **{status['level_pct']}%** (<= {tank.LOW_ALARM_PCT}% threshold). Increase inlet valve position.")
    else:
        st.success("✅ **SYSTEM NORMAL:** Tank level inside safe operational boundary (5% – 95%).")

    st.markdown(f"**Operating State:** :{theme['badge_color']}[**{theme['status_text']}**]")

# Auto-rerun loop to render real-time gradual level change animations
if auto_run:
    time.sleep(0.3)
    st.rerun()
