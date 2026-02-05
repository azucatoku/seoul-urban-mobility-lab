import dbconnect
import pymysql

def fix_station_codes_smart():
    print("🚑 [DB 스마트 복구] 중복 충돌 방지 및 표준화 작업을 시작합니다...")
    conn = dbconnect.MydbConnect('seoul_urban_lab')
    cursor = conn.cursor()
    
    try:
        # ----------------------------------------------------------------------
        # 1. station_meta 테이블 처리
        # ----------------------------------------------------------------------
        print("1️⃣ station_meta 테이블 처리 중...")
        # IGNORE: 이미 0150이 있는데 150을 0150으로 바꾸려 하면, 에러 안 내고 그냥 넘어감
        sql_meta = "UPDATE IGNORE station_meta SET stnCd = LPAD(stnCd, 4, '0')"
        cursor.execute(sql_meta)
        print(f"   -> 표준화 성공 (중복 제외): {cursor.rowcount}건")
        
        # ----------------------------------------------------------------------
        # 2. subway_traffic_log 테이블 처리 (여기가 핵심)
        # ----------------------------------------------------------------------
        print("2️⃣ subway_traffic_log 테이블 처리 중... (시간 소요)")
        
        # [Step A] 바꿀 수 있는 건 다 4자리로 바꿈 (중복 발생 시 무시)
        sql_log_update = "UPDATE IGNORE subway_traffic_log SET stnCd = LPAD(stnCd, 4, '0')"
        cursor.execute(sql_log_update)
        print(f"   -> [업데이트] 표준화 성공: {cursor.rowcount}건")
        
        # [Step B] 아직도 4자리가 아닌 것들은 '중복이라 못 바꾼 찌꺼기'들이므로 삭제
        # (이미 4자리 버전인 '진짜 데이터'가 존재하기 때문)
        sql_log_delete = "DELETE FROM subway_traffic_log WHERE CHAR_LENGTH(stnCd) < 4"
        cursor.execute(sql_log_delete)
        print(f"   -> [청소] 중복 찌꺼기 데이터 삭제: {cursor.rowcount}건")

        # ----------------------------------------------------------------------
        # 3. 과거 데이터 테이블 처리
        # ----------------------------------------------------------------------
        try:
            print("3️⃣ 과거 데이터(22-24) 처리 중...")
            cursor.execute("UPDATE IGNORE `subway_traffic_log_senior_22-24` SET stnCd = LPAD(stnCd, 4, '0')")
            cursor.execute("DELETE FROM `subway_traffic_log_senior_22-24` WHERE CHAR_LENGTH(stnCd) < 4")
            print("   -> 과거 데이터 처리 완료")
        except:
            pass

        # ----------------------------------------------------------------------
        # 4. 저장
        # ----------------------------------------------------------------------
        conn.commit()
        print("\n✅ [성공] 모든 역 코드가 4자리(0150 등)로 통일되었습니다.")
        print("   이제 'Station Not Found' 오류가 해결될 것입니다.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 치명적 오류 발생: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check = input("⚠️ 중복된 짧은 코드(예: 150)를 정리하고 4자리로 통일하시겠습니까? (y/n): ")
    if check.lower() == 'y':
        fix_station_codes_smart()
    else:
        print("작업 취소")