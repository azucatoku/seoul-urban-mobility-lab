import streamlit as st
import pandas as pd
import sys
import os

# 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from api_client import get_system_status

# Style Loader logic
try:
    from utils.style_loader import load_global_style
    load_global_style()
except Exception as e:
    pass

# ==============================================================================
# Header Section (Constructivist)
# ==============================================================================
col_title, col_status = st.columns([4, 1])

with col_title:
    st.markdown("""
        <h1>SEOUL URBAN LAB</h1>
        <div style="background-color:#111; color:#fff; padding:5px 10px; display:inline-block; font-family:'Jost'; font-weight:bold;">
            MOBILITY ANALYTICS ARCHIVE V.2025
        </div>
    """, unsafe_allow_html=True)

# Server Status Check
stats = get_system_status()

with col_status:
    st.write("")
    if stats:
        st.markdown('<div style="border:3px solid #111; background:#D02020; color:white; padding:10px; text-align:center; font-weight:bold;">ONLINE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="border:3px solid #111; background:#F0F0F0; color:#111; padding:10px; text-align:center; font-weight:bold;">OFFLINE</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==============================================================================
# Dashboard Metrics (The Grid)
# ==============================================================================
if stats:
    c1, c2, c3 = st.columns(3)
    
    # Custom Bauhaus Card
    def bauhaus_card(title, value, unit, accent_class):
        return f"""
        <div class="bauhaus-card {accent_class}">
            <div style="font-family:'Jost'; font-weight:700; font-size:0.9rem; text-transform:uppercase; margin-bottom:10px;">{title}</div>
            <div style="font-family:'Space Grotesk'; font-size:3.5rem; font-weight:900; line-height:1;">
                {value}
            </div>
            <div style="border-top:2px solid #111; margin-top:15px; padding-top:5px; font-size:0.8rem; font-weight:bold;">
                {unit}
            </div>
        </div>
        """

    with c1:
        st.markdown(bauhaus_card("TOTAL LOGS", f"{stats['api_count']:,}", "DATA ENTRIES", "b-blue"), unsafe_allow_html=True)
    with c2:
        val = stats.get('senior_count', 0)
        st.markdown(bauhaus_card("SENIOR FLOW", f"{val:,}", "TARGET GROUP", "b-red"), unsafe_allow_html=True)
    with c3:
        st.markdown(bauhaus_card("NODES", f"{stats['meta_count']:,}", "STATIONS", "b-yellow"), unsafe_allow_html=True)

    # ==============================================================================
    # Navigation Hub (The Modules)
    # ==============================================================================
    st.markdown("<h3>MODULES</h3>", unsafe_allow_html=True)

    # Row 1
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    
    def nav_card(number, title, subtitle):
        return f"""
        <div class="bauhaus-card" style="min-height:220px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="font-size:3rem; font-weight:900; color:#ccc; line-height:0.8;">{number}</div>
                <div style="font-size:1.5rem; font-weight:900; margin-top:10px; line-height:1.1;">{title}</div>
            </div>
            <div style="font-family:'Jost'; font-size:0.9rem; margin-top:10px;">
                {subtitle}
            </div>
        </div>
        """

    with col_nav1:
        st.markdown(nav_card("01", "TREND", "RHYTHM & RANK"), unsafe_allow_html=True)
        if st.button("OPEN MODULE", key="go_bump", use_container_width=True):
             st.switch_page("views/bump_chart_view.py")

    with col_nav2:
        st.markdown(nav_card("02", "DIAGNOSIS", "DEEP ANALYSIS"), unsafe_allow_html=True)
        if st.button("OPEN MODULE", key="go_detail", use_container_width=True):
             st.switch_page("views/station_detail_view.py")

    with col_nav3:
        st.markdown(nav_card("03", "MAP", "SPACETIME"), unsafe_allow_html=True)
        if st.button("OPEN MODULE", key="go_time", use_container_width=True):
             st.switch_page("views/timelapse_view.py")
             
    # Row 2
    st.markdown("<br>", unsafe_allow_html=True)
    col_nav4, col_nav5, col_nav6 = st.columns(3)

    with col_nav4:
        st.markdown(nav_card("04", "CLUSTER", "AI GROUPING"), unsafe_allow_html=True)
        if st.button("OPEN MODULE", key="go_cluster", use_container_width=True):
             st.switch_page("views/clustering_view.py")
             
    with col_nav5:
        st.markdown(nav_card("05", "VITALITY", "URBAN PULSE"), unsafe_allow_html=True)
        if st.button("OPEN MODULE", key="go_vitality", use_container_width=True):
             st.switch_page("views/vitality_view.py")
             
    with col_nav6:
        st.markdown(nav_card("06", "FORECAST", "FUTURE IMPACT"), unsafe_allow_html=True)
        if st.button("OPEN MODULE", key="go_pred", use_container_width=True):
             st.switch_page("views/prediction_view.py")

else:
    st.error("SYSTEM DISCONNECTED")
    
    col_retry1, col_retry2 = st.columns(2)
    with col_retry1:
        if st.button("RECONNECT", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()