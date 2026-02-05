import pandas as pd
import dbconnect
import sys

# 출력 옵션 설정 (잘 보이게)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def diagnose_database():
    print("🚀 [DB 정밀 진단] 데이터 매칭 상태를 점검합니다...\n")
    conn = dbconnect.MydbConnect('seoul_urban_lab')
    
    try:
        # ----------------------------------------------------------------------
        # 1. station_meta (기준 정보) 점검
        # ----------------------------------------------------------------------
        print("1️⃣ [station_meta] 역 정보 테이블 점검")
        sql_meta = "SELECT stnNm, stnCd, lineNm FROM station_meta LIMIT 5"
        df_meta = pd.read_sql(sql_meta, conn)
        print(f"   -> 샘플 데이터:\n{df_meta}\n")
        
        # ----------------------------------------------------------------------
        # 2. subway_traffic_log (이동 데이터) 점검
        # ----------------------------------------------------------------------
        print("2️⃣ [subway_traffic_log] 이동 로그 테이블 점검")
        # stnCd가 비어있는지(NULL or '') 확인
        sql_log_check = """
            SELECT 
                COUNT(*) as total_rows,
                COUNT(CASE WHEN stnCd IS NULL OR stnCd = '' THEN 1 END) as missing_code_rows,
                COUNT(CASE WHEN stnNm IS NULL OR stnNm = '' THEN 1 END) as missing_name_rows
            FROM subway_traffic_log
        """
        df_check = pd.read_sql(sql_log_check, conn)
        print(f"   -> 전체 데이터 수: {df_check['total_rows'][0]:,}건")
        print(f"   -> 코드가 없는 행(Missing stnCd): {df_check['missing_code_rows'][0]:,}건")
        
        # 샘플 데이터 확인
        sql_log_sample = "SELECT pasngDe, stnNm, stnCd, lineNm FROM subway_traffic_log LIMIT 5"
        df_log = pd.read_sql(sql_log_sample, conn)
        print(f"   -> 샘플 데이터:\n{df_log}\n")

        # ----------------------------------------------------------------------
        # 3. 매칭 테스트 (실제 조인 시도)
        # ----------------------------------------------------------------------
        print("3️⃣ [매칭 테스트] '서울역' 데이터 조회 시도")
        
        # 3-1. 이름으로 찾기
        sql_by_name = "SELECT COUNT(*) FROM subway_traffic_log WHERE stnNm LIKE '%서울역%'"
        count_name = pd.read_sql(sql_by_name, conn).iloc[0,0]
        print(f"   -> 이름('서울역')으로 찾았을 때: {count_name:,}건 발견")

        # 3-2. 코드로 찾기 (서울역 1호선 코드가 보통 '0150' 또는 '150')
        # 메타 테이블에서 서울역 코드 가져오기
        try:
            target_code = df_meta[df_meta['stnNm'].str.contains('서울')]['stnCd'].values[0]
            print(f"   -> 메타 테이블의 서울역 코드: '{target_code}'")
            
            sql_by_code = f"SELECT COUNT(*) FROM subway_traffic_log WHERE stnCd = '{target_code}'"
            count_code = pd.read_sql(sql_by_code, conn).iloc[0,0]
            print(f"   -> 코드('{target_code}')로 찾았을 때: {count_code:,}건 발견")
            
            if count_name > 0 and count_code == 0:
                print("\n🚨 [진단 결과] 심각함: 데이터에 '이름'은 있는데 '코드'가 비어있거나 다릅니다!")
                print("   => 해결책: subway_traffic_log 테이블의 stnCd를 업데이트해야 합니다.")
            elif count_name == 0:
                 print("\n🚨 [진단 결과] 데이터 자체가 없습니다. DB에 데이터가 제대로 적재되었는지 확인하세요.")
            else:
                print("\n✅ [진단 결과] 정상입니다. 다른 문제일 수 있습니다.")
                
        except IndexError:
            print("   -> (메타 테이블에서 서울역을 찾지 못해 코드 테스트 생략)")

    except Exception as e:
        print(f"❌ 진단 중 오류 발생: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_database()