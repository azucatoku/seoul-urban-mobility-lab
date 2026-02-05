import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
import pydeck as pdk
import sys
import os

# 필수 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from api_client import (
    get_trend_rhythm_data, 
    get_trend_rank_daytime_active_data
)
# Style Loader
try:
    from utils.style_loader import load_global_style
    load_global_style()
except:
    pass

# Bauhaus Theme Helper
def apply_bauhaus_theme(fig):
    fig.update_layout(
        template='simple_white', # Stark contrast
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Jost', color='#111111'),
        xaxis=dict(showgrid=True, gridcolor='#EEEEEE', zerolinecolor='#111111', showline=True, linewidth=2, linecolor='#111'),
        yaxis=dict(showgrid=True, gridcolor='#EEEEEE', zerolinecolor='#111111', showline=True, linewidth=2, linecolor='#111'),
    )
    return fig

# =============================================================================
# Bump Chart
# =============================================================================
def render_bump_chart(df_all, chart_title, unique_key):
    df_all['rank'] = df_all.groupby('year')['volume'].rank(ascending=False, method='min')
    top_10_club = df_all[df_all['rank'] <= 10]['stnNm'].unique()

    if len(top_10_club) == 0:
        st.warning("NO DATA")
        return df_all

    df_filtered = df_all[df_all['stnNm'].isin(top_10_club)].copy()
    year_order = ["2022", "2023", "2024", "Current"]
    available = [y for y in year_order if y in df_filtered['year'].unique()]
    df_filtered['year'] = pd.Categorical(df_filtered['year'], categories=available, ordered=True)
    df_filtered = df_filtered.sort_values(['stnNm', 'year'])

    # Filter UI
    st.markdown(f"#### {unique_key} FILTER")
    c_sel1, c_sel2 = st.columns([1, 2])
    with c_sel1:
        highlight_stn = st.selectbox(
            f"SELECT NODE", 
            ["ALL NODES"] + list(top_10_club),
            key=f"sel_{unique_key}"
        )

    fig = go.Figure()
    # Bauhaus Palette
    bauhaus_colors = [
        '#D02020', # Red
        '#1E5AA0', # Blue
        '#F0B000', # Yellow
        '#111111', # Black
        '#999999', # Gray
    ]

    for idx, stn in enumerate(top_10_club):
        stn_data = df_filtered[df_filtered['stnNm'] == stn]
        if highlight_stn != "ALL NODES" and highlight_stn != stn:
            line_color = '#EEEEEE'; opacity = 0.5; width = 1; text_mode = False
        else:
            line_color = bauhaus_colors[idx % len(bauhaus_colors)]; opacity = 1.0; width = 4; text_mode = True

        text_labels = [stn if r <= 10 else "" for r in stn_data['rank']] if text_mode else None

        fig.add_trace(go.Scatter(
            x=stn_data['year'], y=stn_data['rank'], mode='lines+markers+text' if text_mode else 'lines+markers',
            name=stn, text=text_labels, textposition="top center",
            textfont=dict(size=12, weight="bold", color=line_color),
            line=dict(color=line_color, width=width), marker=dict(size=10, color=line_color, line=dict(width=2, color='white')),
            opacity=opacity
        ))

    fig.update_layout(
        title=dict(text=chart_title.upper(), font=dict(color='black', size=20, family='Space Grotesk')),
        height=600, showlegend=False,
        yaxis=dict(title="RANK (1-10)", range=[10.5, 0.5], dtick=1),
        margin=dict(r=50, t=60, l=50, b=50)
    )
    fig = apply_bauhaus_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"DATA MATRIX // {unique_key}"):
        df_dedup = df_filtered.drop_duplicates(subset=['stnNm', 'year'])
        pivot_df = df_dedup.pivot(index='stnNm', columns='year', values='rank')
        st.dataframe(pivot_df.style.format("{:.0f}", na_rep="-"), use_container_width=True)

    return df_filtered

def render_ranking_map(df_all):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3>SPATIAL VIEW</h3>", unsafe_allow_html=True)
    
    available_years = sorted(df_all['year'].unique())
    if "Current" in available_years:
        available_years.remove("Current")
        available_years.append("Current")
        
    selected_year = st.radio(
        "TIMEFRAME", 
        available_years, 
        index=len(available_years)-1, 
        horizontal=True
    )

    df_target = df_all[df_all['year'] == selected_year].copy()
    df_target['rank'] = df_target['volume'].rank(ascending=False, method='min')
    df_top10 = df_target[df_target['rank'] <= 10].sort_values('rank').drop_duplicates(subset=['stnNm'])
    df_top10['rank_str'] = df_top10['rank'].astype(int).astype(str)

    if df_top10.empty:
        st.warning("NO DATA")
        return

    def get_dynamic_style(row):
        rank = row['rank']
        ratio = (rank - 1) / 9 if rank <= 10 else 1.0
        radius = 600 - (ratio * (600 - 200))
        
        # Color: Primary Red to Yellow
        start_rgb = [208, 32, 32]; end_rgb = [240, 176, 0]
        r = start_rgb[0] + ratio * (end_rgb[0] - start_rgb[0])
        g = start_rgb[1] + ratio * (end_rgb[1] - start_rgb[1])
        b = start_rgb[2] + ratio * (end_rgb[2] - start_rgb[2])
        return pd.Series([radius, [int(r), int(g), int(b), 255]]) # No transparency

    df_top10[['viz_radius', 'viz_color']] = df_top10.apply(get_dynamic_style, axis=1)

    col_map, col_list = st.columns([3, 1])
    with col_map:
        layer_scatter = pdk.Layer(
            "ScatterplotLayer",
            df_top10,
            get_position=["lon", "lat"], get_fill_color="viz_color", get_radius="viz_radius",
            pickable=True, stroked=True, filled=True, get_line_color=[0, 0, 0], # Black outline
            line_width_min_pixels=2, get_line_width=30,
        )
        layer_text = pdk.Layer(
            "TextLayer",
            df_top10,
            get_position=["lon", "lat"], get_text="rank_str", get_color=[0, 0, 0], 
            get_size=24, get_weight="bold", get_alignment_baseline="'center'", get_text_anchor="'middle'",
            pickable=True
        )

        view_state = pdk.ViewState(
            longitude=df_top10['lon'].mean(), latitude=df_top10['lat'].mean(), zoom=10.5
        )
        
        # Light Map for Print Look
        st.pydeck_chart(pdk.Deck(
            layers=[layer_scatter, layer_text],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            tooltip={"html": "<div style='color:black;background:white;border:2px solid black;padding:5px;font-weight:bold;'>{rank} // {stnNm}</div>"}
        ))
        
    with col_list:
        st.markdown(f"<div style='margin-bottom:10px; font-weight:900;'>TOP 10 // {selected_year}</div>", unsafe_allow_html=True)
        for _, row in df_top10.iterrows():
            if row['rank'] <= 3: color = "#D02020"
            elif row['rank'] <= 7: color = "#F0B000"
            else: color = "#999"
            st.markdown(f"<div style='padding:5px; border-bottom:2px solid #111; font-weight:bold;'><span style='color:{color}'>●</span> #{int(row['rank'])} {row['stnNm']}</div>", unsafe_allow_html=True)

# Main Logic
st.markdown("<h2>TREND ANALYSIS</h2>", unsafe_allow_html=True)

if st.button("REFRESH DATA"):
    st.cache_data.clear()
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### 01 / RHYTHM", unsafe_allow_html=True)
df_rhythm = get_trend_rhythm_data()

if not df_rhythm.empty:
    year_totals = df_rhythm.groupby('year')['volume'].transform('sum')
    df_rhythm['ratio'] = (df_rhythm['volume'] / year_totals) * 100
    
    fig = go.Figure()
    colors = {"2022": "#999", "2023": "#666", "2024": "#333", "Current": "#D02020"} # Red for Current
    years = sorted(df_rhythm['year'].unique())
    if "Current" in years: years.remove("Current"); years.append("Current")
    
    for year in years:
        subset = df_rhythm[df_rhythm['year'] == year]
        if not subset.empty:
            is_current = (year == "Current")
            fig.add_trace(go.Scatter(
                x=subset['pasngHr'], y=subset['ratio'], name=year, 
                mode='lines', 
                line=dict(color=colors.get(year, "gray"), width=5 if is_current else 2)
            ))
            
    fig.update_layout(height=450, hovermode="x unified", title="HOURLY PATTERN", yaxis_title="RATIO (%)")
    fig = apply_bauhaus_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### 02 / ACTIVE ZONE", unsafe_allow_html=True)
try:
    df_active = get_trend_rank_daytime_active_data()
    
    if df_active is not None and not df_active.empty:
        # Ensure year is string for categorical sorting consistency
        df_active['year'] = df_active['year'].astype(str)
        render_bump_chart(df_active, "RANKING EVOLUTION", "ActiveZone")
        render_ranking_map(df_active)
    else:
        st.info("NO ACTIVE ZONE DATA AVAILABLE (AWAITING SERVER INPUT)")
except Exception as e:
    st.error(f"ACTIVE ZONE MODULE FAILURE: {str(e)}")