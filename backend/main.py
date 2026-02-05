from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import sys
import os

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import dbconnect 

app = FastAPI(title="SEOUL URBAN LAB: CORE ENGINE (RESTORED)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SystemStatus(BaseModel):
    api_count: int
    senior_count: int
    meta_count: int

def get_db_connection():
    try:
        return dbconnect.MydbConnect('seoul_urban_lab')
    except Exception as e:
        print(f"🚨 Backend DB Error: {e}")
        # Gracefully handle connection failure
        return None

# =============================================================================
# [CORE] SYSTEM STATUS
# =============================================================================
@app.get("/status", response_model=SystemStatus)
def get_status():
    conn = None
    stats = {"api_count": 0, "senior_count": 0, "meta_count": 0}
    try:
        conn = get_db_connection()
        if not conn: return stats
        
        cursor = conn.cursor()
        
        # 1. Traffic Log
        cursor.execute("SELECT COUNT(*) FROM subway_traffic_log")
        stats["api_count"] = cursor.fetchone()[0]
        
        # 2. Senior Log (Try/Except for safety)
        try:
            cursor.execute("SELECT COUNT(*) FROM `subway_traffic_log_senior_22-24`")
            stats["senior_count"] = cursor.fetchone()[0]
        except:
            stats["senior_count"] = 0
            
        # 3. Meta
        cursor.execute("SELECT COUNT(*) FROM station_meta")
        stats["meta_count"] = cursor.fetchone()[0]
        
        return stats
    except Exception as e:
        print(f"❌ Status Error: {e}")
        return stats
    finally:
        if conn: conn.close()

# =============================================================================
# [MODULE A] VITALITY INDEX (NEW FEATURE)
# =============================================================================
@app.get("/analysis/vitality")
def calculate_vitality_index():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return []
        
        # Using the standard log for current vitality
        sql = """
            SELECT t.stnNm, LPAD(t.stnCd, 4, '0') as stnCd, m.lat, m.lon,
            SUM(t.rideNope + t.gffNope) as total_vol,
            SUM(CASE WHEN t.UserGroup LIKE '%노인%' OR t.UserGroup LIKE '%약자%' THEN t.rideNope + t.gffNope ELSE 0 END) as senior_vol,
            SUM(CASE WHEN t.pasngHr BETWEEN 7 AND 10 THEN t.rideNope + t.gffNope ELSE 0 END) as morning_vol,
            SUM(CASE WHEN t.pasngHr BETWEEN 17 AND 20 THEN t.rideNope + t.gffNope ELSE 0 END) as evening_vol
            FROM subway_traffic_log t
            JOIN station_meta m ON LPAD(t.stnCd, 4, '0') = LPAD(m.stnCd, 4, '0')
            GROUP BY t.stnNm, t.stnCd, m.lat, m.lon
        """
        df = pd.read_sql(sql, conn)
        
        if df.empty: return []

        # Filter low volume
        df = df[df['total_vol'] > 100].copy()
        if df.empty: return []

        max_vol = df['senior_vol'].max() if df['senior_vol'].max() > 0 else 1
        
        df['norm_vol'] = (df['senior_vol'] / max_vol) * 100
        df['silver_ratio'] = (df['senior_vol'] / df['total_vol']) * 100
        
        # Balance Score
        # Avoid division by zero
        denom = df['morning_vol'] + df['evening_vol']
        denom = denom.apply(lambda x: x if x > 0 else 1)
        
        df['balance_score'] = 100 - (abs(df['morning_vol'] - df['evening_vol']) / denom * 100)
        
        # Vitality Score
        df['vitality_score'] = (
            (df['norm_vol'] * 0.5) + 
            (df['balance_score'] * 0.3) + 
            (df['silver_ratio'] * 0.2)
        )
        
        return df.sort_values('vitality_score', ascending=False).fillna(0).to_dict(orient='records')
        
    except Exception as e:
        print(f"❌ Vitality Error: {e}")
        return []
    finally:
        if conn: conn.close()

# =============================================================================
# [MODULE B] PREDICTION (NEW FEATURE)
# =============================================================================
@app.get("/analysis/prediction")
def predict_silver_tipping_point():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return []
        
        # Using Historical Table if available, fallback or join with current logic
        # For prediction, we need multi-year data. 
        # Strategy: Use `subway_traffic_log_senior_22-24` for 2022-2024 history.
        
        sql = """
            SELECT CAST(SUBSTR(pasngDe, 1, 4) AS CHAR) as year, stnNm, 
            SUM(rideNope + gffNope) as total_vol
            FROM `subway_traffic_log_senior_22-24`
            GROUP BY year, stnNm
        """
        try:
            df_hist = pd.read_sql(sql, conn)
        except:
            # Fallback if table doesn't exist (user said copies work, so it likely exists, but safety first)
            print("⚠️ Historical table not found, using main log")
            sql_fallback = "SELECT SUBSTR(pasngDe, 1, 4) as year, stnNm, SUM(rideNope+gffNope) as total_vol FROM subway_traffic_log WHERE UserGroup LIKE '%노인%' GROUP BY year, stnNm"
            df_hist = pd.read_sql(sql_fallback, conn)

        if df_hist.empty: return [] # No history = No prediction
        
        pivot = df_hist.pivot(index='stnNm', columns='year', values='total_vol').fillna(0)
        
        if len(pivot.columns) < 2: return []
            
        years = sorted(pivot.columns)
        start_year, end_year = years[0], years[-1]
        
        results = []
        for stn in pivot.index:
            try:
                s_val = pivot.loc[stn, start_year]
                e_val = pivot.loc[stn, end_year]
                
                if s_val == 0: continue
                
                # CAGR
                years_diff = len(years) - 1
                if years_diff == 0: years_diff = 1
                
                cagr = ((e_val / s_val) ** (1/years_diff)) - 1
                
                # Project to 2030 (6 years from 2024)
                proj_2030 = e_val * ((1 + cagr) ** 6)
                
                results.append({
                    "stnNm": stn, 
                    "cagr": round(cagr * 100, 2),
                    "vol_2024": int(e_val),
                    "proj_2030": int(proj_2030),
                    "trend": "RISING" if cagr > 0 else "FALLING"
                })
            except: continue
                
        return sorted(results, key=lambda x: x['cagr'], reverse=True)
    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        return []
    finally:
        if conn: conn.close()

# =============================================================================
# [LEGACY / STANDARD ENDPOINTS - RESTORED LOGIC]
# =============================================================================
@app.get("/meta/stations")
def get_meta_stations():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return []
        sql = """
            SELECT DISTINCT m.stnNm, m.lineNm, LPAD(m.stnCd, 4, '0') as stnCd
            FROM station_meta m
            JOIN subway_traffic_log t ON LPAD(m.stnCd, 4, '0') = LPAD(t.stnCd, 4, '0')
            ORDER BY m.stnNm, m.lineNm
        """
        df = pd.read_sql(sql, conn)
        return df.to_dict(orient='records')
    except: return []
    finally:
        if conn: conn.close()

@app.get("/station/detail/{stn_cd}")
def get_station_detail(stn_cd: str):
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return {"error": "DB"}
        target_code = stn_cd.zfill(4)
        
        # Basic Stats (Restored SQL)
        sql_basic = f"""
            SELECT MAX(stnNm) as stnNm, SUM(rideNope + gffNope) as total_vol,
            SUM(CASE WHEN UserGroup LIKE '%노인%' OR UserGroup LIKE '%약자%' OR UserGroup LIKE '%우대%' THEN rideNope + gffNope ELSE 0 END) as senior_vol
            FROM subway_traffic_log WHERE LPAD(stnCd, 4, '0') = '{target_code}'
        """
        df_basic = pd.read_sql(sql_basic, conn)
        
        if df_basic.empty or df_basic['stnNm'].iloc[0] is None:
             return {"error": f"No data: {target_code}"}
            
        # Time Pattern
        sql_time = f"""
            SELECT pasngHr, SUM(rideNope + gffNope) as vol FROM subway_traffic_log
            WHERE LPAD(stnCd, 4, '0') = '{target_code}' 
            AND (UserGroup LIKE '%노인%' OR UserGroup LIKE '%약자%' OR UserGroup LIKE '%우대%')
            GROUP BY pasngHr ORDER BY pasngHr
        """
        df_time = pd.read_sql(sql_time, conn)
        
        # Day Pattern
        sql_day = f"""
            SELECT CASE WHEN DAYOFWEEK(STR_TO_DATE(pasngDe, '%Y%m%d')) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END as day_type,
            SUM(rideNope + gffNope) as vol FROM subway_traffic_log
            WHERE LPAD(stnCd, 4, '0') = '{target_code}' 
            AND (UserGroup LIKE '%노인%' OR UserGroup LIKE '%약자%' OR UserGroup LIKE '%우대%')
            GROUP BY day_type
        """
        df_day = pd.read_sql(sql_day, conn)
        
        return {
            "basic": df_basic.fillna(0).to_dict(orient='records')[0],
            "time": df_time.fillna(0).to_dict(orient='records'),
            "day": df_day.fillna(0).to_dict(orient='records')
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn: conn.close()

@app.get("/analysis/trend/rhythm")
def get_trend_rhythm():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return []
        
        # Restored Logic: Union of Past (Senior Table) and Current (Log)
        sql_hist = "SELECT CAST(SUBSTR(pasngDe, 1, 4) AS CHAR) as year, pasngHr, SUM(rideNope + gffNope) as volume FROM `subway_traffic_log_senior_22-24` GROUP BY year, pasngHr"
        try:
            df_hist = pd.read_sql(sql_hist, conn)
        except:
            df_hist = pd.DataFrame() # Fallback
            
        sql_curr = "SELECT 'Current' as year, pasngHr, SUM(rideNope + gffNope) as volume FROM subway_traffic_log WHERE (UserGroup LIKE '%노인%' OR UserGroup LIKE '%약자%') GROUP BY pasngHr"
        df_curr = pd.read_sql(sql_curr, conn)
        
        return pd.concat([df_hist, df_curr], ignore_index=True).to_dict(orient='records')
    except: return []
    finally:
        if conn: conn.close()

@app.get("/analysis/trend/rank-daytime-active")
def get_trend_rank_daytime_active():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return []
        
        # 1. Past Data
        sql_hist = """SELECT CAST(SUBSTR(pasngDe, 1, 4) AS CHAR) as year, stnNm, SUM(rideNope + gffNope) as volume FROM `subway_traffic_log_senior_22-24` WHERE pasngHr BETWEEN 10 AND 16 GROUP BY year, stnNm"""
        try:
            df_hist = pd.read_sql(sql_hist, conn)
        except:
            df_hist = pd.DataFrame(columns=['year', 'stnNm', 'volume'])
        
        # 2. Current Data
        sql_curr = """SELECT 'Current' as year, stnNm, SUM(rideNope + gffNope) as volume FROM subway_traffic_log WHERE (UserGroup LIKE '%노인%' OR UserGroup LIKE '%약자%' OR UserGroup LIKE '%우대%') AND pasngHr BETWEEN 10 AND 16 GROUP BY stnNm"""
        df_curr = pd.read_sql(sql_curr, conn)
        
        # 3. Meta Data
        sql_meta = "SELECT stnNm, lat, lon FROM station_meta"
        df_meta = pd.read_sql(sql_meta, conn)
        
        # Restored Processing Logic (Fixing the Station Name Mismatch)
        df_all = pd.concat([df_hist, df_curr], ignore_index=True)
        
        # Apply strict suffixing to ensure matches
        df_all['stnNm'] = df_all['stnNm'].apply(lambda x: x if str(x).endswith('역') else str(x) + '역')
        df_meta['stnNm'] = df_meta['stnNm'].apply(lambda x: x if str(x).endswith('역') else str(x) + '역')
        
        df_grouped = df_all.groupby(['year', 'stnNm'], as_index=False)['volume'].sum()
        df_meta_unique = df_meta.drop_duplicates(subset=['stnNm'])
        
        # Left merge to keep traffic data, drop if no coordinates
        df_final = pd.merge(df_grouped, df_meta_unique, on='stnNm', how='left').dropna(subset=['lat', 'lon'])
        
        return df_final.to_dict(orient='records')
    except Exception as e:
        print(f"❌ Active Error: {e}")
        return []
    finally:
        if conn: conn.close()
        
@app.get("/analysis/timelapse")
def get_timelapse():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return []
        sql = """
            SELECT t.pasngHr, t.stnNm, MAX(m.lat) as lat, MAX(m.lon) as lon, SUM(t.rideNope + t.gffNope) as volume
            FROM subway_traffic_log t 
            JOIN station_meta m ON LPAD(t.stnCd, 4, '0') = LPAD(m.stnCd, 4, '0')
            WHERE (t.UserGroup LIKE '%노인%' OR t.UserGroup LIKE '%약자%' OR t.UserGroup LIKE '%우대%')
            GROUP BY t.pasngHr, t.stnNm
        """
        return pd.read_sql(sql, conn).to_dict(orient='records')
    except: return []
    finally:
        if conn: conn.close()

@app.get("/analysis/clustering")
def get_clustering():
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return []
        
        # Restored Clustering Logic (Total > 500)
        sql = """
            SELECT t.stnNm, LPAD(t.stnCd, 4, '0') as stnCd, 
            SUM(t.rideNope + t.gffNope) as total,
            SUM(CASE WHEN t.pasngHr BETWEEN 6 AND 11 THEN t.rideNope + t.gffNope ELSE 0 END) as morning,
            SUM(CASE WHEN t.pasngHr BETWEEN 12 AND 17 THEN t.rideNope + t.gffNope ELSE 0 END) as afternoon,
            SUM(CASE WHEN t.pasngHr >= 18 THEN t.rideNope + t.gffNope ELSE 0 END) as evening
            FROM subway_traffic_log t
            WHERE (t.UserGroup LIKE '%노인%' OR t.UserGroup LIKE '%약자%' OR t.UserGroup LIKE '%우대%')
            GROUP BY t.stnNm, stnCd 
            HAVING total > 500
        """
        df = pd.read_sql(sql, conn)
        
        sql_meta = "SELECT LPAD(stnCd, 4, '0') as stnCd, lat, lon FROM station_meta"
        df_meta = pd.read_sql(sql_meta, conn).drop_duplicates(subset=['stnCd'])
        
        return pd.merge(df, df_meta, on='stnCd', how='inner').fillna(0).to_dict(orient='records')
    except Exception as e:
        print(f"❌ Clustering Error: {e}")
        return []
    finally:
        if conn: conn.close()

