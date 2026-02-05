import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# 필수 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from api_client import get_station_detail_data, get_all_stations

# Style Loader
try:
    from utils.style_loader import load_global_style
    load_global_style()
except:
    pass

def apply_bauhaus_theme(fig):
    fig.update_layout(
        template='simple_white',
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Jost', color='#111111'),
    )
    return fig

# Header
st.markdown("<h2>STATION DIAGNOSIS</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-weight:bold; color:#555;'>NODE INSPECTION // RISK ASSESSMENT</p>", unsafe_allow_html=True)

# Selector
with st.spinner("SCANNING..."):
    df_meta = get_all_stations()

if not df_meta.empty:
    df_meta['display_name'] = df_meta['stnNm'] + " [" + df_meta['lineNm'] + "]"
    
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_display_name = st.selectbox(
            "SELECT TARGET", 
            df_meta['display_name'].unique(),
            index=0
        )

    with col_btn:
        st.write("") 
        st.write("")
        run_btn = st.button("RUN SCAN", type="primary")

    if run_btn:
        target_row = df_meta[df_meta['display_name'] == selected_display_name].iloc[0]
        target_code = str(target_row['stnCd']).zfill(4) 
        target_name = target_row['stnNm']
        target_line = target_row['lineNm']
        
        with st.spinner(f"PROCESSING {target_code}..."):
            data = get_station_detail_data(target_code)
        
        if data and "error" not in data:
            basic = data['basic']
            df_time = pd.DataFrame(data['time'])
            df_day = pd.DataFrame(data['day'])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            total_vol = basic.get('total_vol', 0)
            senior_vol = basic.get('senior_vol', 0)
            ratio = (senior_vol / total_vol) * 100 if total_vol > 0 else 0
            
            def metric_box(label, val, sub, accent):
                return f"""
                <div class="bauhaus-card {accent}" style="text-align:center;">
                    <div style="font-weight:bold; font-size:0.8rem; letter-spacing:1px; margin-bottom:10px;">{label}</div>
                    <div style="font-family:'Space Grotesk'; font-size:2.5rem; font-weight:900; line-height:1;">{val}</div>
                    <div style="font-size:0.75rem; font-weight:bold; border-top:2px solid #111; margin-top:10px; padding-top:5px;">{sub}</div>
                </div>
                """

            with c1:
                st.markdown(metric_box("NODE ID", target_code, f"{target_name} / {target_line}", "b-blue"), unsafe_allow_html=True)
            with c2:
                st.markdown(metric_box("VOLUME", f"{int(senior_vol):,}", "ACCUMULATED SENIOR TRAFFIC", "b-yellow"), unsafe_allow_html=True)
            with c3:
                is_risk = ratio > 30
                diag_msg = "HIGH RISK" if is_risk else "NORMAL"
                accent = "b-red" if is_risk else "b-blue"
                st.markdown(metric_box("RATIO", f"{ratio:.1f}%", diag_msg, accent), unsafe_allow_html=True)
            
            col_chart1, col_chart2 = st.columns([2, 1])
            
            with col_chart1:
                st.markdown("#### PULSE (24H)")
                if not df_time.empty:
                    fig_time = px.area(
                        df_time, x='pasngHr', y='vol', 
                        labels={'pasngHr':'HR', 'vol':'VOL'}, 
                    )
                    # Red Area with Black Stroke
                    fig_time.update_traces(line_color='#111', fillcolor='rgba(208, 32, 32, 0.8)')
                    fig_time.update_xaxes(tickmode='linear', dtick=4) 
                    fig_time.update_layout(height=300, title=None, margin=dict(t=10,b=10,l=10,r=10))
                    fig_time = apply_bauhaus_theme(fig_time)
                    st.plotly_chart(fig_time, use_container_width=True)
                    
            with col_chart2:
                st.markdown("#### PATTERN")
                if not df_day.empty:
                    if 'day_type' not in df_day.columns: df_day['day_type'] = []
                    fig_day = px.pie(
                        df_day, values='vol', names='day_type', 
                        color='day_type', 
                        color_discrete_map={'Weekday':'#1E5AA0', 'Weekend':'#F0B000'}, # Blue vs Yellow
                    )
                    fig_day.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
                    fig_day.update_layout(height=300, showlegend=False, margin=dict(t=10,b=10,l=10,r=10))
                    fig_day = apply_bauhaus_theme(fig_day)
                    st.plotly_chart(fig_day, use_container_width=True)
            
            # AI Inference
            if not df_time.empty and not df_day.empty:
                max_time_idx = df_time['vol'].idxmax()
                max_time = df_time.loc[max_time_idx]['pasngHr']
                
                total_day_vol = df_day['vol'].sum()
                if 'Weekend' in df_day['day_type'].values:
                    weekend_vol = df_day[df_day['day_type']=='Weekend']['vol'].sum() 
                else:
                    weekend_vol = 0
                weekend_ratio = weekend_vol / total_day_vol if total_day_vol > 0 else 0
                
                if weekend_ratio > 0.35:
                    type_tag = "LEISURE TYPE"
                    desc = "WEEKEND DOMINANT. PARK/MOUNTAIN ACTIVITY."
                else:
                    type_tag = "RESIDENTIAL TYPE"
                    desc = "WEEKDAY DOMINANT. LIVING/COMMUTE HUB."
                
                if max_time < 12: time_desc = "MORNING"
                elif max_time < 16: time_desc = "DAYTIME"
                else: time_desc = "EVENING"

                st.markdown(f"""
                <div class="bauhaus-card b-red">
                    <div style="font-weight:900; font-size:1.5rem; border-bottom:3px solid #111; padding-bottom:10px; margin-bottom:15px;">
                        AI INFERENCE LOG
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span style="font-weight:bold;">CLASSIFICATION</span>
                        <span style="background:#111; color:white; padding:2px 8px; font-weight:bold;">{type_tag}</span>
                    </div>
                    <div style="font-size:0.9rem; color:#555; margin-bottom:20px;">>> {desc}</div>
                    
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span style="font-weight:bold;">PEAK HOUR</span>
                        <span style="background:#D02020; color:white; padding:2px 8px; font-weight:bold;">{max_time}:00 ({time_desc})</span>
                    </div>
                    <div style="font-size:0.9rem; color:#555;">>> MAX CONGESTION THRESHOLD REACHED.</div>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.error("DATA FETCH FAILED")

else:
    st.error("META DATA OFFLINE")