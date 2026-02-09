# SEOUL URBAN MOBILITY LAB
> **서울시 지하철 노인 승하차 데이터를 활용한 도시 활력 진단 및 예측 프로젝트**

안녕하세요! 이 프로젝트는 서울시 지하철 데이터를 분석하여 **어르신들이 가장 많이 이용하는 역**과 **시간대별 이동 패턴**을 시각화하고, 이를 바탕으로 도시의 활력을 진단하는 연구소입니다.

## 프로젝트 소개
고령화 사회로 진입하면서 "노인들이 어디로, 언제 이동하는가?"는 도시 계획에 있어 매우 중요한 질문이 되었습니다.
이 프로젝트는 **서울교통공사 지하철 승하차 데이터**를 분석하여 다음과 같은 인사이트를 제공합니다:

- **Silver Map**: 시간대별 노인 승객들의 이동 물결을 시각화
- **Trend Analysis**: 주요 역들의 순위 변동과 리듬 분석
- **Vitality Index**: 역별 활력 지수 산출을 통한 "Anti-Gravity" 구역 발굴
- **Future Forecast**: 현재 추세를 바탕으로 한 미래 노인 이용객 예측

---

## 사용 기술 (Tech Stack)
이 프로젝트는 Python을 기반으로 데이터 분석부터 웹 서비스까지 구축되었습니다.

- **Frontend**: [Streamlit](https://streamlit.io/) (데이터 시각화 대시보드)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (데이터 처리 및 API 서버)
- **Database**: SQL (데이터 저장소)
- **Data Analysis**: Pandas, NumPy (데이터 전처리 및 분석)

---

## 프로젝트 구조 (File Structure)
프로젝트는 크게 데이터 처리(Notebooks), 백엔드(Server), 프론트엔드(UI) 세 부분으로 나뉩니다.

```bash
seoul-urban-mobility-lab/
├── 00... ~ 03...ipynb   # 데이터 전처리 및 DB 적재를 위한 주피터 노트북
├── backend/             # 데이터 API 서버 (FastAPI)
│   ├── main.py          # 서버 실행 메인 파일
│   └── dbconnect.py     # DB 연결 모듈
├── frontend/            # 사용자 대시보드 (Streamlit)
│   ├── app.py           # 앱 실행 메인 파일
│   ├── Home.py          # 홈페이지 화면
│   └── views/           # 각 분석 페이지 (차트, 지도 등)
├── create_table.sql     # DB 테이블 생성 쿼리
└── requirements.txt     # (권장) 필요한 라이브러리 목록
```

---

## 실행 방법 (How to Run)

초보자도 쉽게 따라 할 수 있도록 차근차근 설명해 드릴게요.

### 1단계: 환경 설정
먼저 필요한 Python 라이브러리들을 설치해야 합니다. 터미널에서 아래 명령어를 입력하세요.
```bash
pip install fastapi uvicorn streamlit pandas pymysql plotly
```

### 2단계: 백엔드 서버 실행
데이터를 분석해서 프론트엔드에 보내줄 **백엔드 서버**를 먼저 켜야 합니다.
`backend` 폴더가 있는 위치에서 아래 명령어를 실행하세요.
```bash
# 터미널 1
cd backend
uvicorn main:app --reload
```
*성공하면 `http://127.0.0.1:8000` 주소가 나옵니다.*

### 3단계: 프론트엔드 대시보드 실행
이제 눈으로 볼 수 있는 **프론트엔드 화면**을 켭니다. 새로운 터미널 창을 열고 실행하세요.
```bash
# 터미널 2 (새 창)
cd frontend
streamlit run app.py
```
*성공하면 브라우저가 자동으로 열리며 멋진 대시보드가 나타납니다!* 

---

## 주요 기능 미리보기

### 1. Trend Analysis (이동 패턴 분석)
- 시간대별로 어르신들이 많이 찾는 역이 어떻게 변하는지(Rhythm) 보여줍니다.
- 아침/점심/저녁 시간대별 핫플레이스 랭킹을 확인할 수 있습니다.

### 2. Station Diagnosis (역별 상세 진단)
- 특정 역을 검색하면 그 역의 **승하차 패턴**, **주말/주중 비교**, **연도별 변화**를 한눈에 볼 수 있습니다.

### 3. Futurism (미래 예측)
- 과거 데이터를 학습하여 **2030년에는 이 역이 어떻게 변할지** 예측해 봅니다.
- 도시가 늙어가는 속도를 늦추는 "활력소(Vitality)"가 어디인지 찾아냅니다.

---

궁금한 점이 있다면 언제든 이슈(Issue)를 남겨주세요.
여러분의 도시 연구를 응원합니다! 
