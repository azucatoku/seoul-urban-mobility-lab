import requests
import streamlit as st
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"

def get_system_status():
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data
def get_all_stations():
    try:
        response = requests.get(f"{API_BASE_URL}/meta/stations")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def get_station_detail_data(stn_cd):
    try:
        response = requests.get(f"{API_BASE_URL}/station/detail/{stn_cd}")
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

@st.cache_data
def get_trend_rhythm_data():
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/trend/rhythm")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def get_trend_rank_daytime_active_data():
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/trend/rank-daytime-active")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def get_timelapse_data_api():
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/timelapse")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def get_clustering_data_api():
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/clustering")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

# ==============================================================================
# NEW ENDPOINTS FOR PROJECT EVOLUTION
# ==============================================================================

@st.cache_data
def get_vitality_data():
    """
    Fetches the new Vitality Index data.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/vitality")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def get_prediction_data():
    """
    Fetches the Silver Tipping Point prediction data.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/prediction")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()