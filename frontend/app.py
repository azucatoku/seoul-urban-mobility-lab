# frontend/app.py 수정

import streamlit as st
import sys
import os

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 스타일 로더 임포트
from utils.style_loader import load_global_style

# 1. 전역 설정
st.set_page_config(
    page_title="Seoul Urban Mobility Lab",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 스타일 적용 (모든 페이지 공통)
load_global_style()

# 3. 페이지 라우팅 (Routing)
home_page = st.Page("Home.py", title="DASHBOARD", default=True)

# [Analytcs]
bump_chart_page = st.Page("views/bump_chart_view.py", title="TREND ANALYSIS")

# [Deep Dive]
station_detail_page = st.Page("views/station_detail_view.py", title="STATION DIAGNOSIS")
timelapse_page = st.Page("views/timelapse_view.py", title="SILVER MAP")
clustering_page = st.Page("views/clustering_view.py", title="CLUSTERING")

# [Futurism] (NEW)
vitality_page = st.Page("views/vitality_view.py", title="VITALITY INDEX")
prediction_page = st.Page("views/prediction_view.py", title="FUTURE FORECAST")

# 4. 내비게이션 구조 정의
pg = st.navigation({
    "MAIN": [home_page],
    "ANALYTICS": [bump_chart_page],
    "DEEP DIVE": [station_detail_page, timelapse_page, clustering_page],
    "FUTURISM": [vitality_page, prediction_page]
})

# 5. 실행
pg.run()
