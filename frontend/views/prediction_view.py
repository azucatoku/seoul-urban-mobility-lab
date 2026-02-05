import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from api_client import get_prediction_data

try:
    from utils.style_loader import load_global_style
    load_global_style()
except:
    pass

st.markdown("<h2>FUTURE FORECAST</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-weight:bold; color:#555;'>SILVER TRAFFIC PROJECTION (2030)</p>", unsafe_allow_html=True)

with st.spinner("RUNNING SIMULATION..."):
    df = get_prediction_data()

if not df.empty:
    # Segregate Rising vs Falling
    rising = df[df['cagr'] > 0]
    falling = df[df['cagr'] <= 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="bauhaus-card b-red">
            <div style="font-weight:900; color:#D02020; margin-bottom:5px;">RISING TREND</div>
            <div style="font-size:3rem; font-weight:900; font-family:'Space Grotesk';">{len(rising)}</div>
            <div style="font-size:0.8rem; font-weight:bold;">STATIONS SHOWING GROWTH</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="bauhaus-card b-blue">
            <div style="font-weight:900; color:#1E5AA0; margin-bottom:5px;">STABLE / DECLINE</div>
            <div style="font-size:3rem; font-weight:900; font-family:'Space Grotesk';">{len(falling)}</div>
            <div style="font-size:0.8rem; font-weight:bold;">STATIONS SHOWING DECREASE</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Chart: Top 10 Fastest Growing
    st.markdown("### FASTEST GROWING ZONES (CAGR %)")
    
    top_10 = rising.head(10).sort_values('cagr', ascending=True)
    fig = px.bar(top_10, x='cagr', y='stnNm', orientation='h', text='cagr')
    
    fig.update_traces(marker_color='#D02020', texttemplate='%{text:.1f}%', textposition='outside', marker_line_color='black', marker_line_width=2)
    fig.update_layout(
        template='simple_white',
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Jost', color='#111'),
        xaxis_title="COMPOUND ANNUAL GROWTH RATE (%)",
        yaxis_title=None,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Projections Table
    st.markdown("### PROJECTION MATRIX (2024 -> 2030)")
    
    st.markdown("""
    <style>
    .dataframe { font-family: 'Jost'; }
    </style>
    """, unsafe_allow_html=True)
    
    display_df = df[['stnNm', 'vol_2024', 'proj_2030', 'cagr', 'trend']].copy()
    display_df['growth_vol'] = display_df['proj_2030'] - display_df['vol_2024']
    
    st.dataframe(
        display_df.style.format({
            'vol_2024': '{:,.0f}', 
            'proj_2030': '{:,.0f}', 
            'growth_vol': '{:+,.0f}',
            'cagr': '{:.2f}%'
        }).background_gradient(subset=['cagr'], cmap='Reds'),
        use_container_width=True
    )

else:
    st.error("SIMULATION FAILED")
