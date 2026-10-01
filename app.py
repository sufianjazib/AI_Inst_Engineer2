import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import datetime
import time
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="AI Instrumentation Engine – Stage 2",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark industrial dashboard theme matching Stage 2 specs
st.markdown("""
<style>
    /* Dark Theme Core Styles */
    .stApp {
        background-color: #0B132B;
        color: #F1F5F9;
    }
    
    /* Panel Containers */
    .card-panel {
        background-color: #131C35;
        border: 1px solid #1E294B;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    /* Badge & Tag Styling */
    .badge-normal {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }

    /* Agent Card Styling */
    .agent-card {
        background-color: #0B132B;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #2563EB;
    }
    
    /* Light Engineering Report Styling */
    .report-light-container {
        background-color: #F8FAFC;
        color: #0F172A;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #CBD5E1;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Initialize simulation state variables in Streamlit Session State
if 'tick_count' not in st.session_state:
    st.session_state.tick_count = 0
if 'sim_running' not in st.session_state:
    st.session_state.sim_running = True
if 'active_fault' not in st.session_state:
    st.session_state.active_fault = 'VALVE_FAULT'
if 'num_points' not in st.session_state:
    st.session_state.num_points = 25

# Initialize trend buffers if missing
if 'press_history' not in st.session_state:
    st.session_state.press_history = [8.2] * st.session_state.num_points
    st.session_state.press_ref_history = [8.1] * st.session_state.num_points
    st.session_state.level_history = [50.0] * st.session_state.num_points
    st.session_state.temp_history = [85.0] * st.session_state.num_points
    st.session_state.flow_history = [182.0] * st.session_state.num_points
    st.session_state.valve_cmd_history = [80.0] * st.session_state.num_points
    st.session_state.valve_fb_history = [35.0] * st.session_state.num_points

def update_plant_simulation():
    """Simulates real-time plant physics and injects configured instrument faults."""
    if st.session_state.sim_running:
        st.session_state.tick_count += 1
        t = st.session_state.tick_count
        noise = np.sin(t * 0.3) * 0.1
        
        # Base physical parameters
        level = max(0.0, min(100.0, 50.0 + noise * 2.0))
        pressure = max(0.0, 8.2 + noise * 0.2)
        temp = 85.0 + noise * 0.5
        flow = 182.0 + noise * 3.0
        air_press = 5.8
        
        # Fault behavior overrides
        fault = st.session_state.active_fault
        if fault == 'VALVE_FAULT':
            valve_cmd = 80.0
            valve_fb = 35.0
        elif fault == 'PT101_DRIFT':
            pressure = 12.8
            valve_cmd = 60.0
            valve_fb = 60.0
        elif fault == 'LOOP_FAULT':
            pressure = 0.0
            valve_cmd = 50.0
            valve_fb = 50.0
        elif fault == 'LOW_AIR':
            air_press = 3.2
            valve_cmd = 80.0
            valve_fb = 42.0
        else: # NO_FAULT
            valve_cmd = 60.0
            valve_fb = 60.0

        # Update historical trend buffers
        st.session_state.press_history.pop(0)
        st.session_state.press_history.append(pressure)
        
        st.session_state.press_ref_history.pop(0)
        st.session_state.press_ref_history.append(8.1 + noise * 0.1)
        
        st.session_state.level_history.pop(0)
        st.session_state.level_history.append(level)
        
        st.session_state.temp_history.pop(0)
        st.session_state.temp_history.append(temp)
        
        st.session_state.flow_history.pop(0)
        st.session_state.flow_history.append(flow)
        
        st.session_state.valve_cmd_history.pop(0)
        st.session_state.valve_cmd_history.append(valve_cmd)
        
        st.session_state.valve_fb_history.pop(0)
        st.session_state.valve_fb_history.append(valve_fb)

# Run simulation step
update_plant_simulation()

# Sidebar Layout
with st.sidebar:
    st.markdown("### ⚙️ Engine Control Panel")
    
    # Navigation Section
    st.markdown("#### Navigation")
    nav_selection = st.selectbox(
        "Select View",
        ["Overview & Diagnostics", "Process Detail View", "AI Multi-Agent Logs", "Engineering Reports", "System Settings"]
    )
    
    st.divider()
    
    # Fault Injection Section
    st.markdown("#### ⚡ Fault Injection Matrix")
    fault_map = {
        "No Fault": "NO_FAULT",
        "Control Valve Fault (CV-101)": "VALVE_FAULT",
        "PT-101 Drift Fault": "PT101_DRIFT",
        "4-20 mA Loop Disruption": "LOOP_FAULT",
        "Low Instrument Air Supply": "LOW_AIR"
    }
    
    selected_fault_label = st.radio(
        "Inject Fault Scenario:",
        list(fault_map.keys()),
        index=1
    )
    st.session_state.active_fault = fault_map[selected_fault_label]
    
    st.divider()
    
    # Simulation Execution Controls
    st.markdown("#### 🔄 Simulation Runtime")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.sim_running = True
    with col_sim2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.sim_running = False
            
    st.caption(f"Status: {'🟢 RUNNING' if st.session_state.sim_running else '🔴 PAUSED'} | Ticks: {st.session_state.tick_count}")
    
    # Optional GROQ API Key Input
    st.divider()
    groq_key = st.text_input("Groq API Key (Optional)", type="password", help="Enter key for live LLM multi-agent reasoning")

# Main Dashboard Header
current_time = datetime.datetime.now().strftime("%b %d, %Y %H:%M:%S")

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 1px solid #1E294B; margin-bottom: 16px;">
    <div>
        <h1 style="margin:0; font-size: 24px; font-weight: 800; color: #FFFFFF;">
            AI INSTRUMENTATION ENGINE <span style="color: #60A5FA;">– Stage 2</span>
        </h1>
        <p style="margin:0; font-size: 12px; color: #94A3B8;">Multi-Agent AI Platform for Process Instrumentation & Diagnostic Engineering</p>
    </div>
    <div style="text-align: right;">
        <span class="badge-normal">● Plant Connected</span>
        <div style="font-family: monospace; font-size: 11px; color: #94A3B8; margin-top: 4px;">{current_time}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Grid: Process Overview SVG, Radial Gauges, Instrument Health
col_overview, col_gauges, col_health = st.columns([4, 4, 4])

with col_overview:
    st.markdown("<h4 style='font-size:14px; margin-bottom:8px;'>🏭 Plant Overview – Tank T-101</h4>", unsafe_allow_html=True)
    
    curr_lvl = st.session_state.level_history[-1]
    curr_press = st.session_state.press_history[-1]
    curr_cmd = st.session_state.valve_cmd_history[-1]
    curr_fb = st.session_state.valve_fb_history[-1]
    curr_temp = st.session_state.temp_history[-1]
    curr_flow = st.session_state.flow_history[-1]
    
    # SVG Tank Schematic HTML Component
    svg_html = f"""
    <div style="background-color: #131C35; border: 1px solid #1E294B; border-radius: 10px; padding: 10px; text-align: center;">
        <svg viewBox="0 0 320 170" style="width: 100%; height: 180px;">
            <!-- Inlet Pipe -->
            <path d="M 10 120 L 70 120 L 70 100 L 95 100" fill="none" stroke="#334155" stroke-width="8"/>
            <path d="M 10 120 L 70 120 L 70 100 L 95 100" fill="none" stroke="#0284c7" stroke-width="4"/>
            
            <!-- Outlet Pipe -->
            <path d="M 205 100 L 250 100 L 250 120 L 310 120" fill="none" stroke="#334155" stroke-width="8"/>
            <path d="M 205 100 L 250 100 L 250 120 L 310 120" fill="none" stroke="#0284c7" stroke-width="4"/>

            <!-- Tank Vessel Body -->
            <rect x="95" y="40" width="110" height="100" rx="12" fill="#0f172a" stroke="#38bdf8" stroke-width="2.5"/>
            
            <!-- Dynamic Liquid Level -->
            <rect x="98" y="{138 - (curr_lvl * 0.9) }" width="104" height="{curr_lvl * 0.9}" rx="4" fill="#0284c7" opacity="0.8"/>
            <text x="150" y="115" font-family="sans-serif" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">{curr_lvl:.0f}%</text>
            <text x="150" y="75" font-family="sans-serif" font-size="12" font-weight="bold" fill="#94a3b8" text-anchor="middle">T-101</text>

            <!-- PT-101 Transmitter -->
            <line x1="150" y1="40" x2="150" y2="20" stroke="#38bdf8" stroke-width="2"/>
            <circle cx="150" cy="15" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
            <text x="150" y="18" font-family="sans-serif" font-size="7" fill="#38bdf8" font-weight="bold" text-anchor="middle">PT</text>

            <!-- LT-101 Sensor -->
            <rect x="70" y="55" width="14" height="20" rx="3" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
            <text x="77" y="68" font-family="sans-serif" font-size="7" fill="#10b981" font-weight="bold" text-anchor="middle">LT</text>

            <!-- Control Valve CV-101 -->
            <g transform="translate(225, 90)">
                <path d="M 0 0 L 18 14 L 0 14 L 18 0 Z" fill="#38bdf8" stroke="#0284c7" stroke-width="1"/>
                <line x1="9" y1="7" x2="9" y2="-6" stroke="#38bdf8" stroke-width="2"/>
                <circle cx="9" cy="-10" r="5" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
            </g>
        </svg>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #CBD5E1; margin-top: 4px; font-family: monospace;">
            <span>LT-101: <strong>{curr_lvl:.1f}%</strong></span>
            <span>PT-101: <strong>{curr_press:.1f} bar</strong></span>
            <span>CV-101: <strong>{curr_cmd:.0f}% ({curr_fb:.0f}% FB)</strong></span>
        </div>
    </div>
    """
    components.html(svg_html, height=240)

with col_gauges:
    st.markdown("<h4 style='font-size:14px; margin-bottom:8px;'>📊 Key Process Parameters</h4>", unsafe_allow_html=True)
    
    # 2x3 Plotly Donut Gauge Charts
    fig_gauges = make_subplots(
        rows=2, cols=3,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
               [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
        vertical_spacing=0.25, horizontal_spacing=0.1
    )
    
    # Level Gauge
    fig_gauges.add_trace(go.Indicator(
        mode="gauge+number", value=curr_lvl,
        number={'suffix': "%", 'font': {'size': 14, 'color': '#FFFFFF'}},
        title={'text': "Level (LT-101)", 'font': {'size': 10, 'color': '#94A3B8'}},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': '#38BDF8'}, 'bgcolor': '#1E294B'}
    ), row=1, col=1)

    # Pressure Gauge
    fig_gauges.add_trace(go.Indicator(
        mode="gauge+number", value=curr_press,
        number={'suffix': " bar", 'font': {'size': 14, 'color': '#FFFFFF'}},
        title={'text': "Pressure (PT-101)", 'font': {'size': 10, 'color': '#94A3B8'}},
        gauge={'axis': {'range': [0, 16]}, 'bar': {'color': '#10B981'}, 'bgcolor': '#1E294B'}
    ), row=1, col=2)

    # Temp Gauge
    fig_gauges.add_trace(go.Indicator(
        mode="gauge+number", value=curr_temp,
        number={'suffix': " °C", 'font': {'size': 14, 'color': '#FFFFFF'}},
        title={'text': "Temp (TT-101)", 'font': {'size': 10, 'color': '#94A3B8'}},
        gauge={'axis': {'range': [0, 150]}, 'bar': {'color': '#F97316'}, 'bgcolor': '#1E294B'}
    ), row=1, col=3)

    # Flow Gauge
    fig_gauges.add_trace(go.Indicator(
        mode="gauge+number", value=curr_flow,
        number={'suffix': " m³/h", 'font': {'size': 12, 'color': '#FFFFFF'}},
        title={'text': "Flow (FT-101)", 'font': {'size': 10, 'color': '#94A3B8'}},
        gauge={'axis': {'range': [0, 300]}, 'bar': {'color': '#06B6D4'}, 'bgcolor': '#1E294B'}
    ), row=2, col=1)

    # Valve Gauge
    fig_gauges.add_trace(go.Indicator(
        mode="gauge+number", value=curr_cmd,
        number={'suffix': "%", 'font': {'size': 14, 'color': '#FFFFFF'}},
        title={'text': "Valve (CV-101)", 'font': {'size': 10, 'color': '#94A3B8'}},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': '#F59E0B'}, 'bgcolor': '#1E294B'}
    ), row=2, col=2)

    # Air Pressure Gauge
    fig_gauges.add_trace(go.Indicator(
        mode="gauge+number", value=5.8 if st.session_state.active_fault != 'LOW_AIR' else 3.2,
        number={'suffix': " bar", 'font': {'size': 14, 'color': '#FFFFFF'}},
        title={'text': "Inst Air", 'font': {'size': 10, 'color': '#94A3B8'}},
        gauge={'axis': {'range': [0, 10]}, 'bar': {'color': '#8B5CF6'}, 'bgcolor': '#1E294B'}
    ), row=2, col=3)

    fig_gauges.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10), height=230
    )
    st.plotly_chart(fig_gauges, use_container_width=True)

with col_health:
    st.markdown("<h4 style='font-size:14px; margin-bottom:8px;'>❤️ Instrument Health Table</h4>", unsafe_allow_html=True)
    
    cv_status = "NORMAL" if st.session_state.active_fault != 'VALVE_FAULT' else "WARNING"
    pt_status = "NORMAL" if st.session_state.active_fault != 'PT101_DRIFT' else "WARNING"
    
    health_data = {
        "Tag": ["PT-101", "PT-102", "LT-101", "TT-101", "FT-101", "CV-101"],
        "PV": [f"{curr_press:.1f} bar", "8.1 bar", f"{curr_lvl:.0f} %", f"{curr_temp:.0f} °C", f"{curr_flow:.0f} m³/h", f"{curr_cmd:.0f} %"],
        "Signal": ["12.2 mA", "12.1 mA", "12.0 mA", "13.1 mA", "13.7 mA", f"{curr_fb:.0f}% FB"],
        "Health": ["42%" if pt_status == "WARNING" else "96%", "95%", "94%", "93%", "92%", "58%" if cv_status == "WARNING" else "95%"],
        "Status": [pt_status, "NORMAL", "NORMAL", "NORMAL", "NORMAL", cv_status]
    }
    
    df_health = pd.DataFrame(health_data)
    st.dataframe(df_health, hide_index=True, use_container_width=True, height=220)

st.divider()

# Middle Row: Trend Sparklines Grid & AI Multi-Agent Workflow
col_trends, col_agents = st.columns([6, 6])

with col_trends:
    st.markdown("<h4 style='font-size:14px;'>📈 Process Trends (Last 2 Hours)</h4>", unsafe_allow_html=True)
    
    # 2x3 Plotly Trend Sparklines
    fig_trends = make_subplots(
        rows=2, cols=3,
        subplot_titles=("Pressure (PT-101)", "Level (LT-101)", "Temp (TT-101)", 
                        "Flow (FT-101)", "Transmitter Comp", "Valve Cmd vs FB")
    )
    
    x_axis = list(range(st.session_state.num_points))
    
    # Chart 1: Pressure
    fig_trends.add_trace(go.Scatter(y=st.session_state.press_history, mode='lines', line=dict(color='#38BDF8', width=2)), row=1, col=1)
    # Chart 2: Level
    fig_trends.add_trace(go.Scatter(y=st.session_state.level_history, mode='lines', line=dict(color='#C084FC', width=2)), row=1, col=2)
    # Chart 3: Temp
    fig_trends.add_trace(go.Scatter(y=st.session_state.temp_history, mode='lines', line=dict(color='#F97316', width=2)), row=1, col=3)
    # Chart 4: Flow
    fig_trends.add_trace(go.Scatter(y=st.session_state.flow_history, mode='lines', line=dict(color='#06B6D4', width=2)), row=2, col=1)
    # Chart 5: Comparison
    fig_trends.add_trace(go.Scatter(y=st.session_state.press_history, mode='lines', name="PT101", line=dict(color='#38BDF8', width=1.5)), row=2, col=2)
    fig_trends.add_trace(go.Scatter(y=st.session_state.press_ref_history, mode='lines', name="PT102", line=dict(color='#10B981', width=1.5, dash='dot')), row=2, col=2)
    # Chart 6: Valve Cmd vs FB
    fig_trends.add_trace(go.Scatter(y=st.session_state.valve_cmd_history, mode='lines', name="Cmd", line=dict(color='#EAB308', width=1.5)), row=2, col=3)
    fig_trends.add_trace(go.Scatter(y=st.session_state.valve_fb_history, mode='lines', name="FB", line=dict(color='#F43F5E', width=1.5)), row=2, col=3)

    fig_trends.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, height=340, margin=dict(l=10, r=10, t=30, b=10)
    )
    fig_trends.update_xaxes(showgrid=True, gridcolor='#1E294B')
    fig_trends.update_yaxes(showgrid=True, gridcolor='#1E294B')
    
    st.plotly_chart(fig_trends, use_container_width=True)

with col_agents:
    st.markdown("<h4 style='font-size:14px;'>🧠 AI Analysis – Multi-Agent Workflow Feed</h4>", unsafe_allow_html=True)
    
    # Dynamic Agent Card content based on active fault
    if st.session_state.active_fault == 'VALVE_FAULT':
        a1_msg = f"<strong>Detected anomaly:</strong> CV-101 position feedback ({curr_fb:.0f}%) is significantly lower than command ({curr_cmd:.0f}%). Deviation of {curr_cmd - curr_fb:.0f}% active for >15 mins."
        a2_msg = "Process parameters (Level, Pressure, Flow) are within operational bounds. Issue isolated to CV-101 actuation assembly."
        a3_msg = "PLC command output correct at 80%. Positioner feedback disagreement confirmed."
        a4_causes = [
            ("1. Control valve / positioner failure", "45%"),
            ("2. Insufficient instrument air pressure", "25%"),
            ("3. Valve stem sticking / mechanical binding", "15%"),
            ("4. I/P Converter calibration drift", "10%")
        ]
    elif st.session_state.active_fault == 'PT101_DRIFT':
        a1_msg = f"<strong>Detected anomaly:</strong> Pressure transmitter PT-101 reading {curr_press:.1f} bar vs redundant reference PT-102 at 8.1 bar."
        a2_msg = "Process pressure verified stable by PT-102. Zero/span drift identified on PT-101 primary element."
        a3_msg = "Transmitter loop current 19.5 mA (out of specification for actual process pressure)."
        a4_causes = [
            ("1. PT-101 Sensing Diaphragm Drift", "65%"),
            ("2. Impulse line blockage / sludge", "20%"),
            ("3. Analog Input Channel drift", "15%")
        ]
    else:
        a1_msg = "✓ All process loops operating normally. PT-101 matches PT-102 within ±0.1 bar."
        a2_msg = "Process parameters completely stable."
        a3_msg = "No I/O errors or SCADA alarm overrides active."
        a4_causes = [("Baseline Operation Normal", "100%")]

    # Agent 1: Diagnostic
    st.markdown(f"""
    <div class="agent-card" style="border-left-color: #10B981;">
        <div style="font-weight: bold; color: #10B981; font-size: 12px;">1. Diagnostic Engineer Agent</div>
        <div style="font-size: 11px; color: #E2E8F0; margin-top: 4px;">{a1_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Agent 2: Process Engineer
    st.markdown(f"""
    <div class="agent-card" style="border-left-color: #2563EB;">
        <div style="font-weight: bold; color: #60A5FA; font-size: 12px;">2. Process Engineer Agent</div>
        <div style="font-size: 11px; color: #E2E8F0; margin-top: 4px;">{a2_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Agent 3: Automation Engineer
    st.markdown(f"""
    <div class="agent-card" style="border-left-color: #8B5CF6;">
        <div style="font-weight: bold; color: #A78BFA; font-size: 12px;">3. Automation Engineer Agent</div>
        <div style="font-size: 11px; color: #E2E8F0; margin-top: 4px;">{a3_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Agent 4: Root Cause Engineer
    causes_html = "".join([f"<div style='display:flex; justify-between; font-size:11px; margin-top:2px;'><span>{c[0]}</span><strong style='color:#F59E0B;'>{c[1]}</strong></div>" for c in a4_causes])
    st.markdown(f"""
    <div class="agent-card" style="border-left-color: #F59E0B;">
        <div style="font-weight: bold; color: #FBBF24; font-size: 12px;">4. Root Cause Probabilities</div>
        {causes_html}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Bottom Row: AI Detailed Engineering Report & Interactive Assistant
col_report, col_assistant = st.columns([8, 4])

with col_report:
    p_tag = "HIGH PRIORITY" if st.session_state.active_fault != 'NO_FAULT' else "NORMAL"
    badge_color = "#EF4444" if p_tag == "HIGH PRIORITY" else "#10B981"
    
    st.markdown(f"""
    <div class="report-light-container">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #CBD5E1; padding-bottom: 8px; margin-bottom: 12px;">
            <span style="font-weight: 800; font-size: 16px; color: #0F172A;">📄 AI Engineering Report</span>
            <span style="background-color: {badge_color}; color: white; padding: 2px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{p_tag}</span>
        </div>
        <div style="background-color: #E2E8F0; padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 12px; margin-bottom: 12px; color: #1E293B;">
            Asset Under Investigation: <span style="color: #2563EB;">CV-101 (Control Valve Assembly)</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 12px; color: #334155;">
            <div>
                <strong style="color: #0F172A;">Detected Condition:</strong>
                <p>Position feedback divergence. Command = {curr_cmd:.0f}%, Feedback = {curr_fb:.0f}%. Stem position lagging controller output.</p>
                <strong style="color: #0F172A;">Recommended Action Steps:</strong>
                <ol style="margin-top:4px; padding-left: 18px;">
                    <li>Check supply air pressure (> 5.0 bar required).</li>
                    <li>Inspect digital positioner feedback link & calibration.</li>
                    <li>Perform stroke test during planned window.</li>
                </ol>
            </div>
            <div>
                <strong style="color: #0F172A;">Required Field Tools:</strong>
                <ul style="margin-top:4px; padding-left: 18px;">
                    <li>Multimeter & HART Field Communicator</li>
                    <li>Pressure test gauge (0-10 bar)</li>
                    <li>Valve packing adjustment wrench set</li>
                </ul>
            </div>
        </div>
        <div style="margin-top: 12px; padding: 8px; background-color: #FEF3C7; border: 1px solid #F59E0B; border-radius: 6px; font-size: 10px; color: #78350F;">
            ⚠️ <strong>Safety Notice:</strong> Ensure permit-to-work, LOTO procedures, and loop isolation are active before field inspection.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_assistant:
    st.markdown("<h4 style='font-size:14px;'>💬 Engineering Assistant</h4>", unsafe_allow_html=True)
    
    selected_task = st.selectbox(
        "Select Engineering Task:",
        ["CV-101 Positioner Diagnostics", "P&ID Specification Review", "Instrument Calibration Export", "Loop Tuning Assistance"]
    )
    
    user_query = st.text_area("Ask a technical question:", value=f"What are the diagnostic steps for {selected_task}?", height=80)
    
    if st.button("Get AI Recommendation", use_container_width=True):
        st.info(f"**AI Recommendation for {selected_task}:**\n1. Check supply air regulator filter for oil/moisture contamination.\n2. Re-align positioner feedback potentiometer arms.\n3. Run auto-tune procedure via HART communicator.")

# Auto-rerun loop for smooth live dashboard updates when simulation is active
if st.session_state.sim_running:
    time.sleep(1.0)
    st.rerun()
