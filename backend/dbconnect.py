import pymysql
import dotenv, os

def MydbConnect(database, port=3306):
    # .env 로드
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(cur_dir, '.env')
    
    if os.path.exists(env_path):
        dotenv.load_dotenv(env_path)
    else:
        dotenv.load_dotenv()

    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')

    try:
        connect = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.Cursor,
            connect_timeout=10,  # 10초 넘으면 포기 (무한 대기 방지)
            read_timeout=30      # 읽기 30초 제한
        )
        return connect
        
    except Exception as e:
        print(f'❌ DB Connection Error: {e}')
        # sys.exit() 절대 금지 -> 에러를 호출한 곳으로 던짐
        raise Exception(f"DB Connect Failed: {e}")

if __name__ == '__main__':
    try:
        conn = MydbConnect('seoul_urban_lab')
        print("✅ Test Connection Success")
        conn.close()
    except Exception as e:
        print(f"❌ Test Failed: {e}")