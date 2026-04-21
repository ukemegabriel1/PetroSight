import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium

# --- Page Configuration ---
st.set_page_config(
    page_title="PetroSight - Dashboard",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Apply Custom CSS for dark theme look ---
# This CSS attempts to match the dark background, colors, and font sizes of the reference image.
st.markdown("""
<style>
    /* Main Content Background */
    .block-container {
        padding: 1.5rem 3rem;
        background-color: #0c0e12;
        color: #e6e8eb;
    }
    
    /* Top Header Bar */
    [data-testid="stHeader"] {
        background-color: #12141a;
        color: #e6e8eb;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0e1014;
        width: 250px !important;
    }
    section[data-testid="stSidebar"] .css-ng1t4o { /* Header */
        color: #a0a6ae;
    }
    section[data-testid="stSidebar"] button { /* Nav links */
        color: #e6e8eb;
        background: transparent;
        border: none;
        text-align: left;
        width: 100%;
        font-weight: normal;
        margin-bottom: 5px;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #1e2229;
        border-radius: 4px;
    }
    section[data-testid="stSidebar"] button[kind="primary"] { /* Active nav */
        background-color: #1e2229;
        border-radius: 4px;
        color: #7cacf8;
        font-weight: bold;
    }
    
    /* Global font and headers */
    html, body, [class*="css"]  {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Metrics and Data Cards */
    .stMetric {
        background-color: #16181d;
        border: 1px solid #23272e;
        border-radius: 8px;
        padding: 20px;
    }
    .stMetric [data-testid="stMetricLabel"] {
        color: #a0a6ae;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: bold;
        color: #ffffff;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        color: #7cacf8; /* Match color in reference */
    }
    
    /* Small status text and icons */
    .info-text {
        font-size: 0.8rem;
        color: #a0a6ae;
    }
    .green-dot {
        height: 8px;
        width: 8px;
        background-color: #2ecc71;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    
    /* Custom Alerts Section CSS */
    .alert-card {
        background-color: #16181d;
        border: 1px solid #23272e;
        border-radius: 8px;
        padding: 1.5rem;
    }
    .alert-title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .alert-count-badge {
        background-color: #e74c3c;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
    }
    .alert-item {
        border-bottom: 1px solid #23272e;
        padding: 1rem 0;
        display: flex;
        align-items: flex-start;
    }
    .alert-item:last-child {
        border-bottom: none;
    }
    .alert-icon {
        font-size: 1.2rem;
        margin-right: 1rem;
        color: #e74c3c; /* Alert red */
    }
    .alert-details {
        flex: 1;
    }
    .alert-meta {
        font-size: 0.7rem;
        color: #a0a6ae;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    .alert-time {
        color: #f39c12; /* Match color for pending */
    }

</style>
""", unsafe_allow_html=True)

# --- Top Header Bar (simulated) ---
st.markdown('<div class="info-text">Industrial Navigator</div>', unsafe_allow_html=True)
c_header1, c_header2, c_header3, c_header4 = st.columns([6, 1, 1, 1])
with c_header1:
    st.text_input("Search", label_visibility="collapsed", placeholder="Search assets, logistics, or data...")
with c_header2:
    st.markdown("🔔")
with c_header3:
    st.markdown("⚙️")
with c_header4:
    st.markdown("👤 User") # Replace with avatar
st.divider()

# --- Main Page Layout ---
main_title, main_ops = st.columns([8, 2])
with main_title:
    st.header("Asset Overview")
    st.markdown('<p class="info-text">Real-time telemetry and production metrics across global platforms.</p>', unsafe_allow_html=True)
with main_ops:
    c_ops1, c_ops2 = st.columns([2, 1])
    c_ops1.markdown('🟢 LIVE SYSTEM STATUS: OPTIMAL', unsafe_allow_html=True) # Could use st.success
    c_ops2.button("GENERATE REPORT", type="primary")

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# --- Metric Cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="TOTAL DAILY PRODUCTION", 
        value="1,240", 
        delta="+2.4% from 24h average",
        delta_color="normal" # Default green, but CSS can change it
    )
    st.markdown('<div class="info-text" style="color: #ffffff;">MBBL</div>', unsafe_allow_html=True)
    # Placeholder for chart - create a simple Plotly bar chart
    df = pd.DataFrame({"day": list(range(1, 8)), "prod": np.random.randint(50, 100, 7)})
    fig = px.bar(df, x="day", y="prod", height=60)
    # Match the background and color style
    fig.update_layout(
        plot_bgcolor="#16181d",
        paper_bgcolor="#16181d",
        font_color="#e6e8eb",
        xaxis={'visible': False}, 
        yaxis={'visible': False}, 
        margin=dict(l=0, r=0, t=0, b=0),
        bargap=0.3
    )
    fig.update_traces(marker_color='#7cacf8') # Light blue bar color
    st.plotly_chart(fig, config={'displayModeBar': False}, theme=None)

with col2:
    st.metric(
        label="SAFETY INCIDENT RATE", 
        value="0.02", 
        delta=None
    )
    st.markdown('<div class="info-text" style="color: #ffffff;">/ 1M Hours</div>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">System maintaining record low incident parameters across all active rigs.</p>', unsafe_allow_html=True)
    st.markdown('<p class="info-text" style="color:#2ecc71;">OPERATIONAL SAFETY: EXCELLENT</p>', unsafe_allow_html=True)

with col3:
    st.metric(
        label="OPERATING MARGIN", 
        value="32.8", 
        delta=None
    )
    st.markdown('<div class="info-text" style="color: #ffffff;">%</div>', unsafe_allow_html=True)
    # Simulating the multi-segment bar
    segment_df = pd.DataFrame({"segment": [1, 2, 3, 4], "value": [10, 10, 10, 10]})
    fig_seg = px.bar(segment_df, x="segment", y="value", height=40, barmode='group')
    fig_seg.update_layout(
        plot_bgcolor="#16181d",
        paper_bgcolor="#16181d",
        font_color="#e6e8eb",
        xaxis={'visible': False}, 
        yaxis={'visible': False}, 
        margin=dict(l=0, r=0, t=0, b=0),
        bargap=0.1
    )
    colors = ['#7cacf8', '#34495e', '#34495e', '#34495e']
    fig_seg.update_traces(marker=dict(color=colors, line=dict(width=0)))
    st.plotly_chart(fig_seg, config={'displayModeBar': False}, theme=None)
    st.markdown('<p class="info-text">Current Market Index: $84.20/BBL</p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# --- Map and Alerts ---
col_map, col_alerts = st.columns([3, 1])

with col_map:
    # Set up Map
    # Use dark style map tiles
    m = folium.Map(location=[0, 0], zoom_start=1.8, tiles="CartoDB dark_matter")
    # Add a marker as in image
    folium.CircleMarker(
        location=[15, -45], # Central Atlantic-like position
        radius=5,
        color='#7cacf8',
        fill=True,
        fill_color='#7cacf8'
    ).add_to(m)

    # Use streamlit-folium to render
    st_data = st_folium(m, width=None, height=450)

with col_alerts:
    # Define Alerts Data
    alerts = [
        {
            "icon": "⚠️", "color": "#e74c3c", "type": "Pressure Differential Spike",
            "msg": "Gulf Sector A-4: Sensor detected 15% deviation in main riser line.",
            "meta": "TRIGGERED 4M AGO • PRIORITY 1",
            "time_style": ""
        },
        {
            "icon": "🔧", "color": "#f39c12", "type": "Scheduled Pump Maintenance",
            "msg": "Bravo Rig: Secondary centrifugal pump requires seal inspection within 24h.",
            "meta": "PENDING • PRIORITY 3",
            "time_style": 'style="color:#f39c12"'
        },
        {
            "icon": "ℹ️", "color": "#a0a6ae", "type": "Logistics Delay Notification",
            "msg": "Tanker 'Deep Voyager' delayed 6h due to storm in the North Sea corridor.",
            "meta": "RECEIVED 1H AGO",
            "time_style": ""
        }
    ]

    # Render alerts using custom CSS
    st.markdown('<div class="alert-card">', unsafe_allow_html=True)
    st.markdown('<div class="alert-title-row"><h4>CRITICAL ALERTS</h4><span class="alert-count-badge">4 NEW</span></div>', unsafe_allow_html=True)
    
    for a in alerts:
        st.markdown(f'''
        <div class="alert-item">
            <div class="alert-icon" style="color: {a["color"]};">{a["icon"]}</div>
            <div class="alert-details">
                <strong>{a["type"]}</strong><br>
                <div class="info-text">{a["msg"]}</div>
                <div class="alert-meta {a["time_style"]}">{a["meta"]}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<button style="background: transparent; border: none; color: #a0a6ae; cursor: pointer;">VIEW ALL ACTIVITY LOGS</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
