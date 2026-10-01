import time
import streamlit as st
from tank_simulation import TankSimulation, get_tank_color_theme

# Page Configuration
st.set_page_config(
    page_title="AI Instrumentation - Tank Level Simulator",
    page_icon="🛢️",
    layout="wide"
)

# Initialize Tank Simulation in Session State
if "tank" not in st.session_state:
    st.session_state.tank = TankSimulation(capacity_liters=1000.0, initial_level_pct=50.0)

tank = st.session_state.tank

st.title("🛢️ Industrial Tank Level Simulator & Alarm System")
st.markdown("Smooth dynamic fill/drain simulation with upper **95% High** and lower **5% Low** threshold alarms.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎛️ Valve Control Panel")

inlet_position = st.sidebar.slider(
    "Inlet Valve Open Position (%)",
    min_value=0,
    max_value=100,
    value=int(tank.inlet_valve * 100),
    step=5
) / 100.0

outlet_position = st.sidebar.slider(
    "Outlet Valve Open Position (%)",
    min_value=0,
    max_value=100,
    value=int(tank.outlet_valve * 100),
    step=5
) / 100.0

# Apply valve inputs to simulation
tank.set_valves(inlet_open_pct=inlet_position, outlet_open_pct=outlet_position)

auto_run = st.sidebar.toggle("▶️ Run Continuous Simulation", value=True)
step_btn = st.sidebar.button("⏱️ Manual Time Step (+1 sec)")

# --- SIMULATION UPDATE STEP ---
if auto_run or step_btn:
    tank.update_simulation(dt=1.0)

# Fetch status and color coding configuration
status = tank.get_status()
theme = get_tank_color_theme(status["level_pct"], tank.HIGH_ALARM_PCT, tank.LOW_ALARM_PCT)

# --- MAIN DISPLAY LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Visual Tank Gauge")
    
    # Custom HTML/CSS Visual Tank Container with Dynamic Fluid Level & Color
    tank_html = f"""
    <div style="
        border: 4px solid #333;
        border-radius: 12px;
        width: 180px;
        height: 280px;
        margin: auto;
        position: relative;
        background-color: #F8F9FA;
        overflow: hidden;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
    ">
        <!-- Alarm Threshold Line: 95% -->
        <div style="
            position: absolute;
            top: 5%;
            width: 100%;
            border-top: 2px dashed #FF4B4B;
            z-index: 2;
        "></div>
        
        <!-- Alarm Threshold Line: 5% -->
        <div style="
            position: absolute;
            top: 95%;
            width: 100%;
            border-top: 2px dashed #FFA500;
            z-index: 2;
        "></div>
        
        <!-- Dynamic Fluid Level Body -->
        <div style="
            position: absolute;
            bottom: 0;
            width: 100%;
            height: {status['level_pct']}%;
            background-color: {theme['color_hex']};
            transition: height 0.5s ease-in-out, background-color 0.5s ease;
            z-index: 1;
        "></div>
        
        <!-- Center Text Overlay -->
        <div style="
            position: absolute;
            width: 100%;
            top: 45%;
            text-align: center;
            font-weight: bold;
            font-size: 20px;
            color: #111;
            z-index: 3;
            text-shadow: 0px 0px 4px rgba(255,255,255,0.8);
        ">
            {status['level_pct']}%
        </div>
    </div>
    """
    st.markdown(tank_html, unsafe_allow_html=True)

with col2:
    st.subheader("Process Readouts & Status")
    
    st.metric(label="Current Fluid Level", value=f"{status['level_pct']} %")
    st.metric(label="Calculated Volume", value=f"{status['level_liters']} L")
    
    st.markdown("### System Status")
    
    if theme["alert_type"] == "error":
        st.error(f"🚨 **HIGH ALARM:** Tank level reached **{status['level_pct']}%** (Threshold >= {tank.HIGH_ALARM_PCT}%). Close inlet valve immediately!")
    elif theme["alert_type"] == "warning":
        st.warning(f"⚠️ **LOW ALARM:** Tank level dropped to **{status['level_pct']}%** (Threshold <= {tank.LOW_ALARM_PCT}%). Open inlet valve immediately!")
    else:
        st.success(f"✅ **NORMAL:** Tank operating inside safe operating boundary (5% – 95%).")

    # Status pill display
    st.markdown(f"Status Badge: :{theme['badge_color']}[**{theme['status_text']}**]")

# Auto-refresh loop for live animation
if auto_run:
    time.sleep(0.5)
    st.rerun()
