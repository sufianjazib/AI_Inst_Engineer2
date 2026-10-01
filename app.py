import time
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from tank_simulation import TankSimulation, get_gauge_color

# Streamlit Page Config for Dark Industrial SCADA Dashboard
st.set_page_config(
    page_title="AI INSTRUMENTATION ENGINE - Stage 2",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Industrial Dark CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #0B101D; color: #E2E8F0; }
    div[data-testid="stSidebar"] { background-color: #070A13; border-right: 1px solid #1E293B; }
    
    /* SCADA Card Container */
    .scada-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    
    /* Table Styling */
    .health-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .health-table th { color: #64748B; text-align: left; padding: 6px; border-bottom: 1px solid #1E293B; }
    .health-table td { padding: 6px; border-bottom: 1px solid #111827; }
    
    .status-normal { color: #10B981; font-weight: bold; }
    .status-warning { color: #F59E0B; font-weight: bold; }
    .status-danger { color: #EF4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "tank" not in st.session_state:
    st.session_state.tank = TankSimulation()
if "history" not in st.session_state:
    st.session_state.history = {"time": [], "level": [], "pressure": [], "valve_cmd": [], "valve_fb": []}

tank = st.session_state.tank

# Helper to generate Gauge Plots
def build_donut_gauge(value, min_v, max_v, title, unit, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': f" {unit}", 'font': {'size': 18, 'color': '#FFFFFF'}},
        gauge={
            'axis': {'range': [min_v, max_v], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "#1E293B",
            'borderwidth': 0,
        }
    ))
    fig.update_layout(
        height=130, margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        title={'text': title, 'font': {'size': 12, 'color': '#94A3B8'}, 'x': 0.5}
    )
    return fig

# --- TOP HEADER BAR ---
h_col1, h_col2, h_col3 = st.columns([3, 1, 1])
with h_col1:
    st.markdown("<h2 style='margin:0; color:#38BDF8;'>⚙️ AI INSTRUMENTATION ENGINE – Stage 2</h2>", unsafe_allow_html=True)
    st.caption("Multi-Agent AI for Complete Instrumentation & Process Engineering")
with h_col2:
    st.markdown("🟢 **Plant Connected** | Apr 26, 2026 14:32:18")
with h_col3:
    sim_mode = st.toggle("Mode: AI + Simulation", value=True)

st.divider()

# --- SIDEBAR NAVIGATION & FAULT INJECTION ---
st.sidebar.markdown("### MAIN NAVIGATION")
st.sidebar.button("🌐 Overview", use_container_width=True)
st.sidebar.button("🔬 Process View", use_container_width=True)
st.sidebar.button("🤖 AI Diagnosis", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ FAULT INJECTION")
fault_choice = st.sidebar.radio(
    "Select Fault Mode:",
    ["No Fault", "PT-101 Drift", "4–20 mA Loop Fault", "Stuck Transmitter", "Impulse Line Blockage", "Control Valve Fault", "Low Instrument Air"],
    index=0
)
if st.sidebar.button("Inject Fault", type="primary", use_container_width=True):
    tank.inject_fault(fault_choice)

st.sidebar.markdown("---")
st.sidebar.markdown("### PROCESS CONTROL")
inlet_val = st.sidebar.slider("Inlet Valve Command (%)", 0, 100, int(tank.inlet_valve_cmd))
outlet_val = st.sidebar.slider("Outlet Valve Command (%)", 0, 100, int(tank.outlet_valve_cmd))
tank.set_valves(inlet_val, outlet_val)

# Update simulation dynamics
tank.update_simulation(dt=1.0)
status = tank.get_status()

# Store timeline history
st.session_state.history["time"].append(time.strftime("%H:%M:%S"))
st.session_state.history["level"].append(status["level_pct"])
st.session_state.history["pressure"].append(status["pressure"])
st.session_state.history["valve_cmd"].append(status["valve_cmd"])
st.session_state.history["valve_fb"].append(status["valve_fb"])

# Keep last 30 points
for key in st.session_state.history:
    st.session_state.history[key] = st.session_state.history[key][-30:]

# --- TOP DASHBOARD ROW ---
r1_c1, r1_c2, r1_c3 = st.columns([1.2, 1.8, 1.2])

# Panel 1: Plant Diagram
with r1_c1:
    st.markdown('<div class="scada-card"><div class="card-title">🏭 Plant Overview – Tank T-101</div>', unsafe_allow_html=True)
    gauge_col = get_gauge_color(status["level_pct"], tank.HIGH_ALARM_PCT, tank.LOW_ALARM_PCT)
    
    # Visual Dynamic Tank Container
    tank_visual = f"""
    <div style="border: 2px solid #334155; border-radius: 8px; height: 180px; background: #0F172A; position: relative; overflow: hidden; margin-top: 10px;">
        <div style="position: absolute; top: 5%; width: 100%; border-top: 1px dashed #EF4444; z-index: 2;"></div>
        <div style="position: absolute; top: 95%; width: 100%; border-top: 1px dashed #F59E0B; z-index: 2;"></div>
        <div style="position: absolute; bottom: 0; width: 100%; height: {status['level_pct']}%; background-color: {gauge_col}; transition: height 0.5s ease; opacity: 0.7;"></div>
        <div style="position: absolute; width: 100%; top: 40%; text-align: center; font-size: 22px; font-weight: bold; color: white;">
            T-101<br><span style="font-size:18px;">{status['level_pct']}%</span>
        </div>
    </div>
    <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:12px; color:#94A3B8;">
        <span>Inlet: {status['inflow']} m³/h</span>
        <span>Outlet: {status['outflow']} m³/h</span>
    </div>
    """
    st.markdown(tank_visual, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Panel 2: Key Process Parameters Gauges
with r1_c2:
    st.markdown('<div class="scada-card"><div class="card-title">🎛️ Key Process Parameters</div>', unsafe_allow_html=True)
    g_col1, g_col2, g_col3 = st.columns(3)
    
    with g_col1:
        st.plotly_chart(build_donut_gauge(status["level_pct"], 0, 100, "Level (LT-101)", "%", gauge_col), use_container_width=True)
        st.plotly_chart(build_donut_gauge(status["inflow"], 0, 300, "Flow (FT-101)", "m³/h", "#00E5FF"), use_container_width=True)
        
    with g_col2:
        st.plotly_chart(build_donut_gauge(status["pressure"], 0, 16, "Pressure (PT-101)", "bar", "#3B82F6"), use_container_width=True)
        valve_color = "#EF4444" if status["valve_fault"] else "#10B981"
        st.plotly_chart(build_donut_gauge(status["valve_fb"], 0, 100, "Valve Position (CV-101)", "%", valve_color), use_container_width=True)
        
    with g_col3:
        st.plotly_chart(build_donut_gauge(status["temp"], 0, 150, "Temperature (TT-101)", "°C", "#10B981"), use_container_width=True)
        st.plotly_chart(build_donut_gauge(status["inst_air"], 0, 10, "Instrument Air", "bar", "#3B82F6"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Panel 3: Instrument Health Table
with r1_c3:
    st.markdown('<div class="scada-card"><div class="card-title">🩺 Instrument Health</div>', unsafe_allow_html=True)
    
    cv_status = '<span class="status-warning">WARNING</span>' if status["valve_fault"] else '<span class="status-normal">NORMAL</span>'
    
    table_html = f"""
    <table class="health-table">
        <tr><th>Instrument</th><th>PV</th><th>Signal</th><th>Health</th><th>Status</th></tr>
        <tr><td>PT-101</td><td>{status['pressure']} bar</td><td>12.2 mA</td><td>96%</td><td><span class="status-normal">NORMAL</span></td></tr>
        <tr><td>LT-101</td><td>{status['level_pct']} %</td><td>12.0 mA</td><td>94%</td><td><span class="status-normal">NORMAL</span></td></tr>
        <tr><td>TT-101</td><td>{status['temp']} °C</td><td>13.1 mA</td><td>93%</td><td><span class="status-normal">NORMAL</span></td></tr>
        <tr><td>FT-101</td><td>{status['inflow']} m³/h</td><td>13.7 mA</td><td>92%</td><td><span class="status-normal">NORMAL</span></td></tr>
        <tr><td>CV-101</td><td>{status['valve_fb']} % FB</td><td>35 % FB</td><td>58%</td><td>{cv_status}</td></tr>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECOND ROW: TRENDS & AI WORKFLOW ---
r2_c1, r2_c2 = st.columns([1.8, 1.2])

with r2_c1:
    st.markdown('<div class="scada-card"><div class="card-title">📈 Process Trends (Real-Time)</div>', unsafe_allow_html=True)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=st.session_state.history["time"], y=st.session_state.history["level"], name="Level (%)", line=dict(color=gauge_col, width=2)))
    fig_trend.add_trace(go.Scatter(x=st.session_state.history["time"], y=st.session_state.history["valve_cmd"], name="Valve Cmd (%)", line=dict(color="#3B82F6", width=2)))
    fig_trend.add_trace(go.Scatter(x=st.session_state.history["time"], y=st.session_state.history["valve_fb"], name="Valve FB (%)", line=dict(color="#EF4444", width=2, dash='dash')))
    
    fig_trend.update_layout(
        height=240, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#1E293B'), yaxis=dict(gridcolor='#1E293B'),
        legend=dict(orientation="h", y=1.1, x=0)
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r2_c2:
    st.markdown('<div class="scada-card"><div class="card-title">🤖 AI Analysis – Multi-Agent Workflow</div>', unsafe_allow_html=True)
    
    st.success("1. **Diagnostic Engineer:** Detected deviation on CV-101 feedback vs command.")
    st.info("2. **Process Engineer:** Process conditions appear stable.")
    st.info("3. **Automation Engineer:** PLC/SCADA I/O healthy. Valve command signal verified.")
    st.warning("4. **Root Cause Engineer:** High probability of positioner or actuator air line issue.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- BOTTOM ROW: AI ENGINEERING REPORT ---
st.markdown('<div class="scada-card"><div class="card-title" style="color:#EF4444;">🚨 AI Engineering Report – HIGH PRIORITY</div>', unsafe_allow_html=True)
if status["high_alarm"]:
    st.error(f"🚨 **HIGH LEVEL ALARM ACTIVE ({status['level_pct']}%):** Tank level exceeded upper 95% threshold!")
elif status["low_alarm"]:
    st.warning(f"⚠️ **LOW LEVEL ALARM ACTIVE ({status['level_pct']}%):** Tank level dropped below lower 5% threshold!")
elif status["valve_fault"]:
    st.error("🚨 **INSTRUMENT DEVIATION:** CV-101 position feedback (35%) is lower than command (80%). Inspect positioner air pressure.")
else:
    st.success("✅ **ALL SYSTEMS NORMAL:** Process parameters within configured operating bounds.")
st.markdown('</div>', unsafe_allow_html=True)

# Auto-rerun loop for live SCADA dashboard updates
time.sleep(1.0)
st.rerun()
