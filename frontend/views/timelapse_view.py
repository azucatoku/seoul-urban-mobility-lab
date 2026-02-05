import streamlit as st
import pandas as pd
import pydeck as pdk
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from api_client import get_timelapse_data_api

# Style Loader
try:
    from utils.style_loader import load_global_style
    load_global_style()
except:
    pass

st.markdown("<h2>CHRONO MAPPING</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-weight:bold; color:#555;'>SPATIOTEMPORAL FLOW VISUALIZATION</p>", unsafe_allow_html=True)

with st.spinner("LOADING..."):
    df = get_timelapse_data_api()

if not df.empty:
    st.markdown("### TIME CONTROL", unsafe_allow_html=True)
    selected_hour = st.slider("", 0, 23, 12, format="%02d:00")
    
    df_layer = df[df['pasngHr'] == selected_hour].copy()
    
    if df_layer.empty:
        st.warning("NO SIGNAL")
    else:
        global_max = df['volume'].quantile(0.99)
        
        def get_style(vol):
            ratio = min(vol / global_max, 1.0)
            radius = 100 + (ratio * 900)
            # Red Scale
            # 255, 200, 200 -> 208, 32, 32
            r = 208
            g = int(200 - (ratio * 168))
            b = int(200 - (ratio * 168))
            return pd.Series([radius, [r, g, b, 200]])
        
        df_layer[['radius', 'color']] = df_layer['volume'].apply(get_style).apply(pd.Series)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"<div style='background:#111; color:white; padding:5px 10px; display:inline-block; font-weight:bold;'>T-MINUS {selected_hour:02d}:00</div>", unsafe_allow_html=True)
            
            layer = pdk.Layer(
                "ScatterplotLayer",
                df_layer,
                get_position=["lon", "lat"], get_fill_color="color", get_radius="radius",
                pickable=True, stroked=True, get_line_color=[0, 0, 0],
                line_width_min_pixels=1, opacity=0.8
            )
            
            view_state = pdk.ViewState(
                longitude=126.9780, latitude=37.5665, zoom=10.8, pitch=0, bearing=0 # Flat view for Bauhaus
            )
            
            st.pydeck_chart(pdk.Deck(
                layers=[layer], initial_view_state=view_state,
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                tooltip={"html": "<div style='color:black; background:white; border:2px solid black; padding:5px;'><b>{stnNm}</b>: {volume}</div>"}
            ))
        
        with col2:
            st.markdown("### LOG", unsafe_allow_html=True)
            
            if 6 <= selected_hour <= 9:
                log_title = "DAWN"
                log_msg = "EARLY MOBILIZATION DETECTED."
                accent = "b-blue"
            elif 10 <= selected_hour <= 14:
                log_title = "HEAT"
                log_msg = "CORE DENSITY CRITICAL."
                accent = "b-red"
            elif 15 <= selected_hour <= 18:
                log_title = "FLOW"
                log_msg = "OUTER SECTOR DISPERSION."
                accent = "b-yellow"
            else:
                log_title = "VOID"
                log_msg = "MINIMAL ACTIVITY."
                accent = ""

            st.markdown(f"""
            <div class="bauhaus-card {accent}" style="padding:15px;">
                <div style="font-weight:900; font-size:1.2rem; margin-bottom:5px;">{log_title}</div>
                <div style="font-size:0.8rem; font-weight:bold; color:#555; text-transform:uppercase;">{log_msg}</div>
                <div style="border-top:2px solid #111; margin-top:15px; padding-top:5px;">
                    <span style="font-size:0.8rem;">VOL</span><br>
                    <span style="font-size:1.5rem; font-weight:900;">{df_layer['volume'].sum():,}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.error("DATA LOSS")