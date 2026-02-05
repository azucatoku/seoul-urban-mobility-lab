import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import QuantileTransformer
import pydeck as pdk
import sys
import os
import numpy as np

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from api_client import get_clustering_data_api

# Style Loader
try:
    from utils.style_loader import load_global_style
    load_global_style()
except:
    pass

st.markdown("<h2>AI CLUSTERING</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-weight:bold; color:#555;'>PATTERN RECOGNITION MATRIX</p>", unsafe_allow_html=True)

# 1. 데이터 로드
with st.spinner("COMPUTING..."):
    df = get_clustering_data_api()

if not df.empty:
    df['total'] = df['total'].astype(float)
    df['morning_ratio'] = df.apply(lambda x: x['morning'] / x['total'] if x['total'] > 0 else 0, axis=1)
    df['afternoon_ratio'] = df.apply(lambda x: x['afternoon'] / x['total'] if x['total'] > 0 else 0, axis=1)

    features = ['morning_ratio', 'afternoon_ratio']
    X = df[features].fillna(0)
    
    if len(df) < 3:
        st.warning("NOT ENOUGH DATA FOR AI CLUSTERING (NEED > 3 NODES)")
        # Stop execution of this view
        st.stop()
        
    try:
        n_q = min(len(df), 100)
        scaler = QuantileTransformer(n_quantiles=n_q, output_distribution='uniform', random_state=42)
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=20)
        df['cluster'] = kmeans.fit_predict(X_scaled)
    except Exception as e:
        st.error(f"CLUSTERING ENGINE FAILURE: {str(e)}")
        st.stop()
    
    cluster_means = df.groupby('cluster')[features].mean()
    morning_cluster_id = cluster_means['morning_ratio'].idxmax()
    remaining = cluster_means.drop(morning_cluster_id)
    afternoon_cluster_id = remaining['afternoon_ratio'].idxmax()
    all_ids = set([0, 1, 2])
    balance_cluster_id = list(all_ids - {morning_cluster_id, afternoon_cluster_id})[0]
    
    # Bauhaus Color Mapping
    mapping = {
        morning_cluster_id: {
            "name": "TYPE A (AM)",
            "color": [30, 90, 160], # Blue
            "hex": "#1E5AA0"
        },
        afternoon_cluster_id: {
            "name": "TYPE B (PM)",
            "color": [208, 32, 32],   # Red
            "hex": "#D02020"
        },
        balance_cluster_id: {
            "name": "TYPE C (MIX)",
            "color": [240, 176, 0],  # Yellow
            "hex": "#F0B000"
        }
    }
    
    df['cluster_name'] = df['cluster'].map(lambda x: mapping[x]['name'])
    df['viz_color'] = df['cluster'].map(lambda x: mapping[x]['color'] + [200])

    # Radius
    df['log_total'] = np.log1p(df['total'])
    max_log = df['log_total'].max()
    min_log = df['log_total'].min()
    df['viz_radius'] = ((df['log_total'] - min_log) / (max_log - min_log)) * (600 - 50) + 50

    # 1. 산점도
    st.markdown("### SCATTER DISTRIBUTION")
    
    plotly_color_map = {}
    for cid in mapping:
        info = mapping[cid]
        plotly_color_map[info['name']] = info['hex']
        
    fig_scatter = px.scatter(
        df, x='morning_ratio', y='afternoon_ratio',
        color='cluster_name', 
        hover_name='stnNm',
        size='total', size_max=25,
        color_discrete_map=plotly_color_map
    )
    fig_scatter.add_shape(type="line", x0=0, y0=0, x1=0.6, y1=0.6, line=dict(color="#111", width=1, dash="dash"))
    
    fig_scatter.update_layout(
        template='simple_white',
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Jost', color='#111'),
        xaxis=dict(showgrid=True, gridcolor='#EEE', showline=True, linewidth=2, linecolor='#111'),
        yaxis=dict(showgrid=True, gridcolor='#EEE', showline=True, linewidth=2, linecolor='#111'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(255,255,255,0.8)', bordercolor='#111', borderwidth=1)
    )
    fig_scatter.update_traces(marker=dict(line=dict(width=1, color='black')))
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 2. 지도
    st.markdown("### GEOSPATIAL CLUSTERS")
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"], get_fill_color="viz_color", get_radius="viz_radius",
        pickable=True, stroked=True, get_line_color=[0, 0, 0],
        line_width_min_pixels=1, opacity=0.9
    )
    
    view_state = pdk.ViewState(
        longitude=df['lon'].mean(), latitude=df['lat'].mean(), zoom=10.0
    )
    
    st.pydeck_chart(pdk.Deck(
        layers=[layer], initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"html": "<div style='background:white;color:black;border:2px solid black;padding:5px;'><b>{stnNm}</b><br>{cluster_name}</div>"}
    ))
    
    # 3. 리스트
    st.markdown("### NODE LIST")
    c1, c2, c3 = st.columns(3)
    order_ids = [morning_cluster_id, afternoon_cluster_id, balance_cluster_id]
    cols = [c1, c2, c3]
    
    descriptions = {
        morning_cluster_id: "EARLY MEDICAL/MARKET PEAK",
        afternoon_cluster_id: "LATE SOCIAL LEISURE PEAK",
        balance_cluster_id: "BALANCED RESIDENTIAL HUB"
    }
    
    accent_classes = {
        morning_cluster_id: "b-blue",
        afternoon_cluster_id: "b-red",
        balance_cluster_id: "b-yellow"
    }

    for i, cid in enumerate(order_ids):
        info = mapping[cid]
        accent = accent_classes[cid]
        
        with cols[i]:
            st.markdown(f"""
                <div class="bauhaus-card {accent}" style="min-height: 200px;">
                    <div style='font-weight:900; font-size:1.1em; margin-bottom:10px; text-transform:uppercase;'>{info['name']}</div>
                    <div style='font-size:0.8rem; font-weight:bold; color:#555; margin-bottom:15px; height:40px;'>{descriptions[cid]}</div>
                    <div style='font-size:0.85rem; color:#111; font-family:"Jost";'>
                        {", ".join(df[df['cluster'] == cid].nlargest(10, 'total')['stnNm'].tolist())}
                    </div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.error("CALCULATION ERROR")