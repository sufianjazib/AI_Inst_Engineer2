import time
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from tank_simulation import TankSimulation

# Streamlit Page Config for Stage-1 Industrial Dark SCADA
st.set_page_config(
    page_title="AI INSTRUMENTATION ENGINE - Stage-1",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Stage-1 SCADA CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #070B14; color: #E2E8F0; font-family: 'Inter', monospace, sans-serif; }
    
    /* Header Container */
    .header-card {
        background-color: #0D1322;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 12px 20px;
        margin-bottom: 16px;
    }
    
    /* Panel Cards */
    .scada-panel {
        background-color: #0D1322;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    .panel-header {
        font-size: 13px;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Metric Cards Top Row */
    .metric-card {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 11px; color: #94A3B8; font-weight: 600; display: flex; justify-content: space-between; }
    .metric-sub { font-size: 11px; color: #64748B; margin-top: 2px; }
    .metric-val { font-size: 20px; font-weight: 700; color: #FFFFFF; margin: 4px 0; }
    .metric-val span { font-size: 12px; color: #94A3B8; font-weight: normal; }
    .metric-sig { font-size: 11px; color: #38BDF8; font-family: monospace; }
    
    .tag-ok { background-color: #064E3B; color: #34D399; font-size: 10px; padding: 2px 6px; border-radius: 4px; border: 1px solid #059669; }
    .tag-fault { background-color: #7F1D1D; color: #FCA5A5; font-size: 10px; padding: 2px 6px; border-radius: 4px; border: 1px solid #DC2626; }
    .tag-active { background-color: #064E3B; color: #34D399; font-size: 11px; padding: 4px 10px; border-radius: 12px; font-weight: 600; }

    /* Target Process Info Row */
    .info-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 12px; background: #070B14; padding: 8px; border-radius: 4px; }
    .info-label { color: #64748B; }
    .info-val { color: #38BDF8; font-weight: 600; font-family: monospace; }

    /* Telemetry Table */
    .telem-table { width: 100%; border-collapse: collapse; font-size: 12px; font-family: monospace; }
    .telem-table th { color: #64748B; text-align: left; padding: 8px; border-bottom: 1px solid #1E293B; font-weight: 600; }
    .telem-table td { padding: 8px; border-bottom: 1px solid #0F172A; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "tank" not in st.session_state:
    st.session_state.tank = TankSimulation()
if "history" not in st.session_state:
    st.session_state.history = {"time": list(range(30)), "pt101": [8.21]*30, "pt102": [8.21]*30, "cmd": [58.0]*30, "fb": [58.0]*30}
if "paused" not in st.session_state:
    st.session_state.paused = False

tank = st.session_state.tank

# --- TOP SCADA HEADER ---
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background-color: #0284C7; padding: 8px; border-radius: 8px;">⚙️</div>
            <div>
                <div style="font-size: 20px; font-weight: bold; color: #FFFFFF;">
                    AI INSTRUMENTATION ENGINE <span style="background-color: #0C4A6E; color: #38BDF8; font-size: 12px; padding: 2px 8px; border-radius: 12px; border: 1px solid #0284C7;">Stage-1 v1.0</span>
                </div>
                <div style="font-size: 12px; color: #64748B;">
                    Intelligent Instrument Health Monitoring, Deterministic Diagnostics & Fault Isolation
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with head_col2:
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        if st.button("⏸ Pause Sim" if not st.session_state.paused else "▶ Resume Sim", use_container_width=True):
            st.session_state.paused = not st.session_state.paused
    with btn_c2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.tank = TankSimulation()
            st.rerun()

st.divider()

if not st.session_state.paused:
    tank.update_simulation(dt=1.0)

status = tank.get_status()

# Update simulation history
st.session_state.history["pt101"].append(status["pressure"])
st.session_state.history["pt102"].append(status["pressure"])
st.session_state.history["cmd"].append(status["valve_cmd"])
st.session_state.history["fb"].append(status["valve_fb"])

for k in st.session_state.history:
    st.session_state.history[k] = st.session_state.history[k][-30:]

# --- MAIN LAYOUT ---
col_left, col_right = st.columns([1, 3])

# --- LEFT COLUMN: TARGET PROCESS & FAULT INJECTION ---
with col_left:
    # Target Process Panel
    st.markdown("""
    <div class="scada-panel">
        <div class="panel-header">
            <span>Target Process</span>
            <span style="color:#38BDF8;">T-101 TANK</span>
        </div>
        <div class="info-row"><span class="info-label">Process Medium</span><span class="info-val">Demin Water System</span></div>
        <div class="info-row"><span class="info-label">Sim Engine Loop</span><span class="info-val">1000 ms / Tick</span></div>
        <div class="info-row"><span class="info-label">Rule Evaluation</span><span class="info-val">Deterministic IEC 61508</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Fault Injection Panel
    st.markdown("""
    <div class="scada-panel">
        <div class="panel-header">
            <span>⚠️ Fault Injection</span>
            <span class="tag-active">NO_FAULT</span>
        </div>
        <p style="font-size: 11px; color: #64748B; margin-bottom: 14px;">
            Inject physical hardware, calibration, signal loop, or pneumatic abnormalities to test diagnostic engine:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    fault_options = [
        "0. Normal Operations (No Fault)",
        "1. PT-101 Calibration Drift (+4.5 bar)",
        "2. PT-101 4–20mA Loop Fault (3.6 mA)",
        "3. PT-101 Stuck Transmitter (8.0 bar)",
        "4. Impulse Line Blockage (Damped)",
        "5. Control Valve CV-101 Stiction"
    ]
    
    selected_fault = st.radio("Select Active Fault:", fault_options, label_visibility="collapsed")
    
    # Map selection back to simulation logic
    if "0." in selected_fault:
        tank.inject_fault("No Fault")
    elif "1." in selected_fault:
        tank.inject_fault("PT-101 Drift")
    elif "2." in selected_fault:
        tank.inject_fault("4–20 mA Loop Fault")
    elif "3." in selected_fault:
        tank.inject_fault("Stuck Transmitter")
    elif "4." in selected_fault:
        tank.inject_fault("Impulse Line Blockage")
    elif "5." in selected_fault:
        tank.inject_fault("Control Valve Fault")

# --- RIGHT COLUMN: METRIC CARDS, TRENDS & TELEMETRY ---
with col_right:
    # Top Metrics Bar (6 Instrumentation Cards)
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">PT-101 <span class="tag-ok">OK</span></div>
            <div class="metric-sub">Pressure Tx</div>
            <div class="metric-val">{status['pressure']} <span>bar</span></div>
            <div class="metric-sig">Signal: 12.21 mA</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">PT-102 [RED] <span class="tag-ok">OK</span></div>
            <div class="metric-sub">Ref Pressure</div>
            <div class="metric-val">{status['pressure']} <span>bar</span></div>
            <div class="metric-sig">Signal: 12.21 mA</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">LT-101 <span class="tag-ok">OK</span></div>
            <div class="metric-sub">Tank Level</div>
            <div class="metric-val">{status['level_pct']} <span>%</span></div>
            <div class="metric-sig">Signal: 13.73 mA</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TT-101 <span class="tag-ok">OK</span></div>
            <div class="metric-sub">Temperature</div>
            <div class="metric-val">{status['temp']} <span>°C</span></div>
            <div class="metric-sig">Signal: 13.05 mA</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">FT-101 <span class="tag-ok">OK</span></div>
            <div class="metric-sub">Inlet Flow</div>
            <div class="metric-val">{status['inflow']} <span>m³/h</span></div>
            <div class="metric-sig">Signal: 13.52 mA</div>
        </div>
        """, unsafe_allow_html=True)

    with m6:
        valve_tag = '<span class="tag-fault">WARN</span>' if status["valve_fault"] else '<span class="tag-ok">OK</span>'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">CV-101 {valve_tag}</div>
            <div class="metric-sub">Cmd vs FB</div>
            <div class="metric-val">{status['valve_fb']} <span>%</span></div>
            <div class="metric-sig">Air Sup: {status['inst_air']} bar</div>
        </div>
        """, unsafe_allow_html=True)

    # Process Trends Panel
    st.markdown('<div class="scada-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">📈 Dynamic Real-Time Process Trends (Tank T-101)</div>', unsafe_allow_html=True)
    
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(y=st.session_state.history["pt101"], name="PT-101 (bar)", line=dict(color="#00E5FF", width=2)))
        fig_p.add_trace(go.Scatter(y=st.session_state.history["pt102"], name="PT-102 Ref (bar)", line=dict(color="#38BDF8", width=2, dash="dash")))
        fig_p.update_layout(
            title={'text': "PT-101 vs Redundant PT-102 Pressure", 'font': {'size': 12, 'color': '#94A3B8'}},
            height=200, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1E293B', showticklabels=True), yaxis=dict(gridcolor='#1E293B')
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with t_col2:
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(y=st.session_state.history["cmd"], name="CV-101 Command (%)", line=dict(color="#818CF8", width=2)))
        fig_v.add_trace(go.Scatter(y=st.session_state.history["fb"], name="CV-101 Feedback (%)", line=dict(color="#F59E0B", width=2)))
        fig_v.update_layout(
            title={'text': "CV-101 Control Valve Cmd vs Feedback", 'font': {'size': 12, 'color': '#94A3B8'}},
            height=200, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='#1E293B', showticklabels=True), yaxis=dict(gridcolor='#1E293B')
        )
        st.plotly_chart(fig_v, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Telemetry Table Panel
    st.markdown("""
    <div class="scada-panel">
        <div class="panel-header">📊 Deterministic Instrument Telemetry & Calculation Table</div>
        <table class="telem-table">
            <thead>
                <tr>
                    <th>Tag</th>
                    <th>Description</th>
                    <th>LRV - URV</th>
                    <th>Calculated PV</th>
                    <th>Analog Signal</th>
                    <th>Health %</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color:#38BDF8; font-weight:bold;">PT-101</td>
                    <td>Tank Pressure Tx</td>
                    <td>0 - 16 bar</td>
                    <td><b>{} bar</b></td>
                    <td style="color:#38BDF8;">12.21 mA</td>
                    <td style="color:#34D399;">98%</td>
                    <td><span class="tag-ok">NORMAL</span></td>
                </tr>
                <tr>
                    <td style="color:#38BDF8; font-weight:bold;">PT-102</td>
                    <td>Redundant Press Tx</td>
                    <td>0 - 16 bar</td>
                    <td><b>{} bar</b></td>
                    <td style="color:#38BDF8;">12.21 mA</td>
                    <td style="color:#34D399;">98%</td>
                    <td><span class="tag-ok">NORMAL</span></td>
                </tr>
            </tbody>
        </table>
    </div>
    """.format(status['pressure'], status['pressure']), unsafe_allow_html=True)

# Auto-rerun loop for live simulation updating
if not st.session_state.paused:
    time.sleep(1.0)
    st.rerun()
