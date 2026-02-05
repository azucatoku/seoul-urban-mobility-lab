import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from api_client import get_vitality_data

try:
    from utils.style_loader import load_global_style
    load_global_style()
except:
    pass

st.markdown("<h2>VITALITY INDEX</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-weight:bold; color:#555;'>THE SILVER PULSE OF THE CITY</p>", unsafe_allow_html=True)

with st.spinner("CALCULATING INDEX..."):
    df = get_vitality_data()

if not df.empty:
    # KPI Section
    top_station = df.iloc[0]
    avg_score = df['vitality_score'].mean()
    
    c1, c2, c3 = st.columns(3)
    
    def kpi_card(title, value, sub, accent=""):
        return f"""
        <div class="bauhaus-card {accent}">
            <div style="font-weight:900; font-size:1.0rem; margin-bottom:10px;">{title}</div>
            <div style="font-size:2.5rem; font-weight:900; font-family:'Space Grotesk'; line-height:1;">{value}</div>
            <div style="font-size:0.8rem; font-weight:bold; color:#555; margin-top:10px; border-top:2px solid #111; padding-top:5px;">{sub}</div>
        </div>
        """
    
    with c1:
        st.markdown(kpi_card("HIGHEST PULSE", top_station['stnNm'], f"SCORE: {top_station['vitality_score']:.1f}", "b-red"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("AVG INDEX", f"{avg_score:.1f}", "CITYWIDE AVERAGE", "b-blue"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("NODES ONLINE", f"{len(df)}", "TOTAL STATIONS ANALYZED", "b-yellow"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Map Visualization
    st.markdown("### VITALITY HEATMAP")
    
    # Radius based on score
    df['radius'] = (df['vitality_score'] / 100) * 1000 + 100
    
    # Color based on score (Red = High, Gray = Low)
    def get_color(score):
        if score > 80: return [208, 32, 32, 200] # Red
        elif score > 50: return [30, 90, 160, 200] # Blue
        else: return [100, 100, 100, 150] # Gray
        
    df['color'] = df['vitality_score'].apply(get_color)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"], get_fill_color="color", get_radius="radius",
        pickable=True, stroked=True, get_line_color=[0, 0, 0],
        line_width_min_pixels=1, opacity=0.8
    )
    
    view_state = pdk.ViewState(
        longitude=df['lon'].mean(), latitude=df['lat'].mean(), zoom=10.5
    )
    
    st.pydeck_chart(pdk.Deck(
        layers=[layer], initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"html": "<div style='background:white;color:black;border:2px solid black;padding:5px;'><b>{stnNm}</b><br>Score: {vitality_score:.1f}</div>"}
    ))
    
    # Leaderboard
    st.markdown("### LEADERBOARD")
    
    display_df = df[['stnNm', 'vitality_score', 'norm_vol', 'silver_ratio', 'balance_score']].head(10).copy()
    display_df.columns = ["STATION", "VITALITY SCORE", "VOLUME IDX", "SILVER RATIO", "BALANCE"]
    display_df.reset_index(drop=True, inplace=True)
    display_df.index = display_df.index + 1
    
    st.dataframe(
        display_df.style.format({
            "VITALITY SCORE": "{:.1f}", 
            "VOLUME IDX": "{:.1f}", 
            "SILVER RATIO": "{:.1f}", 
            "BALANCE": "{:.1f}"
        }), 
        use_container_width=True
    )
else:
    st.error("INDEX CALCULATION FAILED")
