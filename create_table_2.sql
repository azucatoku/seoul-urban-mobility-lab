USE seoul_urban_lab;

-- 기존 테이블과 동일한 구조로 생성
CREATE TABLE IF NOT EXISTS `subway_traffic_log_senior_22-24` (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '고유 식별자',
    UserGroup VARCHAR(50) NOT NULL COMMENT '사용자 그룹 (노인/약자 고정)',
    pasngDe VARCHAR(20) NOT NULL COMMENT '통행일자 (YYYYMMDD)',
    pasngHr INT NOT NULL COMMENT '통행시간 (0~23)',
    lineNm VARCHAR(50) NOT NULL COMMENT '호선명 (CSV는 정보없음으로 들어감)',
    stnCd VARCHAR(20) NOT NULL COMMENT '역코드',
    stnNm VARCHAR(50) NOT NULL COMMENT '역명',
    trnscdUserSeCd VARCHAR(10) NOT NULL COMMENT '사용자 구분 코드 (06 고정)',
    rideNope INT DEFAULT 0 COMMENT '승차인원',
    gffNope INT DEFAULT 0 COMMENT '하차인원',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_senior_log (pasngDe, pasngHr, stnCd, trnscdUserSeCd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='서울교통공사 22-24년 노인 승하차 데이터';