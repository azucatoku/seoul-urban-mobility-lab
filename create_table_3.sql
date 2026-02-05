USE seoul_urban_lab;

-- 기존 테이블이 있다면 삭제 후 재생성 (선택 사항)
-- DROP TABLE IF EXISTS station_meta;

CREATE TABLE IF NOT EXISTS station_meta (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '고유 식별자',
    stnCd VARCHAR(20) NOT NULL COMMENT '역코드 (Join Key)',
    stnNm VARCHAR(50) NOT NULL COMMENT '역명',
    lineNm VARCHAR(50) NOT NULL COMMENT '호선명',
    lat DECIMAL(10, 7) NOT NULL COMMENT '위도 (Latitude)',
    lon DECIMAL(11, 7) NOT NULL COMMENT '경도 (Longitude)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 적재 일시',
    UNIQUE KEY uk_station_code (stnCd),
    INDEX idx_station_name (stnNm)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='서울교통공사 역사 위경도 좌표 마스터';