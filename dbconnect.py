# DB 접속을 위한 정보 초기화
import pymysql
import dotenv, os, sys


#  MySQL/mariaDB 연결 커넥트
def MydbConnect(database, port=3306):
  # .env에 있는 정보 읽어오기
  dotenv.load_dotenv()

  # 읽어온 정보에서 원한는 정보 가져오기
  host = os.getenv('DB_HOST')
  user = os.getenv('DB_USER')
  password = os.getenv('DB_PASSWORD')

  print('데이터베이서 연결 시작!')

  try:
    connect = pymysql.connect(
      host = host,
      port = port,
      user = user,
      password = password,
      database = database
      # autocommit=True
    )
    print('MySQL DB 연결 성공')
    config = True
  except Exception as e:
    print(f'연결실패: {e}')
    config = False

  if config == False: sys.exit()

  return connect


# 현재 파일 위치에서 함수 호출시에서 실행되는 코드(테스트 코드)
if __name__ == '__main__':
  conn_mysql = MydbConnect('book_db', 3306)
  

